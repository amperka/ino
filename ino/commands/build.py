# -*- coding: utf-8; -*-

import re
import os.path
import inspect
import subprocess
import platform
import jinja2

from jinja2.runtime import StrictUndefined

import ino.filters

from ino.commands.base import Command
from ino.environment import Version
from ino.filters import colorize
from ino.utils import SpaceList, list_subdirs
from ino.exc import Abort


class Build(Command):
    """
    Build a project in the current directory and produce a ready-to-upload
    firmware file.

    The project is expected to have a `src' subdirectroy where all its sources
    are located. This directory is scanned recursively to find
    *.[c|cpp|pde|ino] files. They are compiled and linked into resulting
    firmware hex-file.

    Also any external library dependencies are tracked automatically. If a
    source file includes any library found among standard Arduino libraries or
    a library placed in `lib' subdirectory of the project, the library gets
    build too.

    Build artifacts are placed in `.build' subdirectory of the project.
    """

    name = 'build'
    help_line = "Build firmware from the current directory project"

    def setup_arg_parser(self, parser):
        super(Build, self).setup_arg_parser(parser)
        self.e.add_board_model_arg(parser)
        self.e.add_arduino_dist_arg(parser)
        parser.add_argument('-v', '--verbose', default=False, action='store_true',
                            help='Verbose make output')

    def discover(self):
        self.e.find_arduino_file('version.txt', ['lib'],
                                 human_name='Arduino lib version file (version.txt)')

        if 'arduino_lib_version' not in self.e:
            with open(self.e['version.txt']) as f:
                print 'Detecting Arduino software version ... ',
                v_string = f.read().strip()
                v = Version.parse(v_string)
                self.e['arduino_lib_version'] = v
                print colorize("%s (%s)" % (v, v_string), 'green')

        self.e.find_arduino_dir('arduino_core_dir', 
                                ['hardware', 'arduino', 'cores', 'arduino'], 
                                ['Arduino.h'] if self.e.arduino_lib_version.major else 'WProgram.h', 
                                'Arduino core library')

        self.e.find_arduino_dir('arduino_libraries_dir', ['libraries'],
                                human_name='Arduino standard libraries')

        if self.e.arduino_lib_version.major:
            self.e.find_arduino_dir('arduino_variants_dir',
                                    ['hardware', 'arduino', 'variants'],
                                    human_name='Arduino variants directory')

        toolset = [
            ('cc', 'avr-gcc'),
            ('cxx', 'avr-g++'),
            ('ar', 'avr-ar'),
            ('objcopy', 'avr-objcopy'),
        ]

        # Linux has system-wide avr gcc toolset
        # other platforms are bundled with it as a part of Arduino Software
        system_wide = platform.system() == 'Linux'

        for tool_key, tool_binary in toolset:
            if system_wide:
                self.e.find_tool(tool_key, [tool_binary], human_name=tool_binary)
            else:
                self.e.find_arduino_tool(tool_key, ['hardware', 'tools', 'avr', 'bin'], 
                                         items=[tool_binary], human_name=tool_binary)

    def setup_flags(self, board_key):
        board = self.e.board_model(board_key)
        mcu = '-mmcu=' + board['build']['mcu']
        self.e['cflags'] = SpaceList([
            mcu,
            '-ffunction-sections',
            '-fdata-sections',
            '-g',
            '-Os', 
            '-w',
            '-DF_CPU=' + board['build']['f_cpu'],
            '-DARDUINO=' + str(self.e.arduino_lib_version.as_int()),
            '-I' + self.e['arduino_core_dir'],
        ])

        if self.e.arduino_lib_version.major:
            variant_dir = os.path.join(self.e.arduino_variants_dir, 
                                       board['build']['variant'])
            self.e.cflags.append('-I' + variant_dir)

        self.e['cxxflags'] = SpaceList(['-fno-exceptions'])
        self.e['elfflags'] = SpaceList(['-Os', '-Wl,--gc-sections', mcu])

        self.e['names'] = {
            'obj': '%s.o',
            'lib': 'lib%s.a',
            'cpp': '%s.cpp',
            'deps': '%s.d',
        }

    def create_jinja(self, verbose):
        templates_dir = os.path.join(os.path.dirname(__file__), '..', 'make')
        self.jenv = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            undefined=StrictUndefined, # bark on Undefined render
            extensions=['jinja2.ext.do'])

        # inject @filters from ino.filters
        for name, f in inspect.getmembers(ino.filters, lambda x: getattr(x, 'filter', False)):
            self.jenv.filters[name] = f

        # inject globals
        self.jenv.globals['e'] = self.e
        self.jenv.globals['v'] = '' if verbose else '@'
        self.jenv.globals['slash'] = os.path.sep
        self.jenv.globals['SpaceList'] = SpaceList

    def render_template(self, source, target, **ctx):
        template = self.jenv.get_template(source)
        contents = template.render(**ctx)
        out_path = os.path.join(self.e['build_dir'], target)
        with open(out_path, 'wt') as f:
            f.write(contents)

        return out_path

    def make(self, makefile, **kwargs):
        makefile = self.render_template(makefile + '.jinja', makefile, **kwargs)
        ret = subprocess.call(['make', '-f', makefile, 'all'])
        if ret != 0:
            raise Abort("Make failed with code %s" % ret)

    def recursive_inc_lib_flags(self, libdirs):
        flags = SpaceList()
        for d in libdirs:
            flags.append('-I' + d)
            flags.extend('-I' + subd for subd in list_subdirs(d, recursive=True, exclude=['examples']))
        return flags

    def _scan_dependencies(self, dir, lib_dirs, inc_flags):
        output_filepath = os.path.join(self.e.build_dir, os.path.basename(dir), 'dependencies.d')
        self.make('Makefile.deps', inc_flags=inc_flags, src_dir=dir, output_filepath=output_filepath)
        self.e['deps'].append(output_filepath)

        # search for dependencies on libraries
        # for this scan dependency file generated by make
        # with regexes to find entries that start with
        # libraries dirname
        regexes = dict((lib, re.compile(r'\s' + lib + re.escape(os.path.sep))) for lib in lib_dirs)
        used_libs = set()
        with open(output_filepath) as f:
            for line in f:
                for lib, regex in regexes.iteritems():
                    if regex.search(line):
                        used_libs.add(lib)

        return used_libs

    def scan_dependencies(self):
        self.e['deps'] = SpaceList()

        lib_dirs = [self.e.arduino_core_dir] + list_subdirs(self.e.lib_dir) + list_subdirs(self.e.arduino_libraries_dir)
        inc_flags = self.recursive_inc_lib_flags(lib_dirs)

        used_libs = self._scan_dependencies(self.e.src_dir, lib_dirs, inc_flags)
        scanned_libs = set()
        while scanned_libs != used_libs:
            for lib_dir in list(used_libs - scanned_libs):
                used_libs |= self._scan_dependencies(lib_dir, lib_dirs, inc_flags)
                scanned_libs.add(lib_dir)

        self.e['used_libs'] = list(used_libs)
        self.e['cflags'].extend(self.recursive_inc_lib_flags(used_libs))

    def run(self, args):
        self.discover()
        self.setup_flags(args.board_model)
        self.create_jinja(verbose=args.verbose)
        self.make('Makefile.sketch')
        self.scan_dependencies()
        self.make('Makefile')
