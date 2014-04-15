# -*- coding: utf-8; -*-

import re
import os.path
import inspect
import subprocess
import platform
import jinja2
import shlex

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

    The project is expected to have a `src' subdirectory where all its sources
    are located. This directory is scanned recursively to find
    *.[c|cpp|pde|ino] files. They are compiled and linked into resulting
    firmware hex-file.

    Also any external library dependencies are tracked automatically. If a
    source file includes any library found among standard Arduino libraries or
    a library placed in `lib' subdirectory of the project, the library gets
    built too.

    Build artifacts are placed in `.build' subdirectory of the project.
    """

    name = 'build'
    help_line = "Build firmware from the current directory project"

    default_make = 'make'
    default_cc = 'avr-gcc'
    default_cxx = 'avr-g++'
    default_ar = 'avr-ar'
    default_objcopy = 'avr-objcopy'

    default_cppflags = '-ffunction-sections -fdata-sections -g -Os -w'
    default_cflags = ''
    default_cxxflags = '-fno-exceptions'
    default_ldflags = '-Os --gc-sections'

    def setup_arg_parser(self, parser):
        super(Build, self).setup_arg_parser(parser)
        self.e.add_board_model_arg(parser)
        self.e.add_arduino_dist_arg(parser)

        parser.add_argument('--make', metavar='MAKE',
                            default=self.default_make,
                            help='Specifies the make tool to use. If '
                            'a full path is not given, searches in Arduino '
                            'directories before PATH. Default: "%(default)s".')

        parser.add_argument('--cc', metavar='COMPILER',
                            default=self.default_cc,
                            help='Specifies the compiler used for C files. If '
                            'a full path is not given, searches in Arduino '
                            'directories before PATH. Default: "%(default)s".')

        parser.add_argument('--cxx', metavar='COMPILER',
                            default=self.default_cxx,
                            help='Specifies the compiler used for C++ files. '
                            'If a full path is not given, searches in Arduino '
                            'directories before PATH. Default: "%(default)s".')

        parser.add_argument('--ar', metavar='AR',
                            default=self.default_ar,
                            help='Specifies the AR tool to use. If a full path '
                            'is not given, searches in Arduino directories '
                            'before PATH. Default: "%(default)s".')

        parser.add_argument('--objcopy', metavar='OBJCOPY',
                            default=self.default_objcopy,
                            help='Specifies the OBJCOPY to use. If a full path '
                            'is not given, searches in Arduino directories '
                            'before PATH. Default: "%(default)s".')

        parser.add_argument('-f', '--cppflags', metavar='FLAGS',
                            default=self.default_cppflags,
                            help='Flags that will be passed to the compiler. '
                            'Note that multiple (space-separated) flags must '
                            'be surrounded by quotes, e.g. '
                            '`--cppflags="-DC1 -DC2"\' specifies flags to define '
                            'the constants C1 and C2. Default: "%(default)s".')

        parser.add_argument('--cflags', metavar='FLAGS',
                            default=self.default_cflags,
                            help='Like --cppflags, but the flags specified are '
                            'only passed to compilations of C source files. '
                            'Default: "%(default)s".')

        parser.add_argument('--cxxflags', metavar='FLAGS',
                            default=self.default_cxxflags,
                            help='Like --cppflags, but the flags specified '
                            'are only passed to compilations of C++ source '
                            'files. Default: "%(default)s".')

        parser.add_argument('--ldflags', metavar='FLAGS',
                            default=self.default_ldflags,
                            help='Like --cppflags, but the flags specified '
                            'are only passed during the linking stage. Note '
                            'these flags should be specified as if `ld\' were '
                            'being invoked directly (i.e. the `-Wl,\' prefix '
                            'should be omitted). Default: "%(default)s".')

        parser.add_argument('-v', '--verbose', default=False, action='store_true',
                            help='Verbose make output')

    def discover(self, args):
        board = self.e.board_model(args.board_model)

        core_place = os.path.join(board['_coredir'], 'cores', board['build']['core'])
        core_header = 'Arduino.h' if self.e.arduino_lib_version.major else 'WProgram.h'
        self.e.find_dir('arduino_core_dir', [core_header], [core_place],
                        human_name='Arduino core library')

        if self.e.arduino_lib_version.major:
            variants_place = os.path.join(board['_coredir'], 'variants')
            self.e.find_dir('arduino_variants_dir', ['.'], [variants_place],
                            human_name='Arduino variants directory')

        self.e.find_arduino_dir('arduino_libraries_dir', ['libraries'],
                                human_name='Arduino standard libraries')

        toolset = [
            ('make', args.make),
            ('cc', args.cc),
            ('cxx', args.cxx),
            ('ar', args.ar),
            ('objcopy', args.objcopy),
        ]

        for tool_key, tool_binary in toolset:
            self.e.find_arduino_tool(
                tool_key, ['hardware', 'tools', 'avr', 'bin'], 
                items=[tool_binary], human_name=tool_binary)

    def setup_flags(self, args):
        board = self.e.board_model(args.board_model)
        mcu = '-mmcu=' + board['build']['mcu']
        # Hard-code the flags that are essential to building the sketch
        self.e['cppflags'] = SpaceList([
            mcu,
            '-DF_CPU=' + board['build']['f_cpu'],
            '-DARDUINO=' + str(self.e.arduino_lib_version.as_int()),
            '-I' + self.e['arduino_core_dir'],
        ]) 
        # Add additional flags as specified
        self.e['cppflags'] += SpaceList(shlex.split(args.cppflags))

        if 'vid' in board['build']:
            self.e['cppflags'].append('-DUSB_VID=%s' % board['build']['vid'])
        if 'pid' in board['build']:
            self.e['cppflags'].append('-DUSB_PID=%s' % board['build']['pid'])
            
        if self.e.arduino_lib_version.major:
            variant_dir = os.path.join(self.e.arduino_variants_dir, 
                                       board['build']['variant'])
            self.e.cppflags.append('-I' + variant_dir)

        self.e['cflags'] = SpaceList(shlex.split(args.cflags))
        self.e['cxxflags'] = SpaceList(shlex.split(args.cxxflags))

        # Again, hard-code the flags that are essential to building the sketch
        self.e['ldflags'] = SpaceList([mcu])
        self.e['ldflags'] += SpaceList([
            '-Wl,' + flag for flag in shlex.split(args.ldflags)
        ])

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
        out_path = os.path.join(self.e.build_dir, target)
        with open(out_path, 'wt') as f:
            f.write(contents)

        return out_path

    def make(self, makefile, **kwargs):
        makefile = self.render_template(makefile + '.jinja', makefile, **kwargs)
        ret = subprocess.call([self.e.make, '-f', makefile, 'all'])
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
                    if regex.search(line) and lib != dir:
                        used_libs.add(lib)

        return used_libs

    def scan_dependencies(self):
        self.e['deps'] = SpaceList()

        lib_dirs = [self.e.arduino_core_dir] + list_subdirs(self.e.lib_dir) + list_subdirs(self.e.arduino_libraries_dir)
        inc_flags = self.recursive_inc_lib_flags(lib_dirs)

        # If lib A depends on lib B it have to appear before B in final
        # list so that linker could link all together correctly
        # but order of `_scan_dependencies` is not defined, so...
        
        # 1. Get dependencies of sources in arbitrary order
        used_libs = list(self._scan_dependencies(self.e.src_dir, lib_dirs, inc_flags))

        # 2. Get dependencies of dependency libs themselves: existing dependencies
        # are moved to the end of list maintaining order, new dependencies are appended
        scanned_libs = set()
        while scanned_libs != set(used_libs):
            for lib in set(used_libs) - scanned_libs:
                dep_libs = self._scan_dependencies(lib, lib_dirs, inc_flags)

                i = 0
                for ulib in used_libs[:]:
                    if ulib in dep_libs:
                        # dependency lib used already, move it to the tail
                        used_libs.append(used_libs.pop(i))
                        dep_libs.remove(ulib)
                    else:
                        i += 1

                # append new dependencies to the tail
                used_libs.extend(dep_libs)
                scanned_libs.add(lib)

        self.e['used_libs'] = used_libs
        self.e['cppflags'].extend(self.recursive_inc_lib_flags(used_libs))

    def run(self, args):
        self.discover(args)
        self.setup_flags(args)
        self.create_jinja(verbose=args.verbose)
        self.make('Makefile.sketch')
        self.scan_dependencies()
        self.make('Makefile')
