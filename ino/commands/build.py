# -*- coding: utf-8; -*-

import os.path
import inspect
import subprocess
import jinja2

from jinja2.runtime import StrictUndefined

import ino.filters

from ino.commands.base import Command
from ino.utils import SpaceList




class Build(Command):

    name = 'build'

    def setup_arg_parser(self, parser):
        parser.add_argument('-t', '--template', help='Jinja makefile template to use')

    def discover(self):
        self.e['arduino_core_dir'] = '/usr/local/share/arduino/hardware/arduino/cores/arduino'
        self.e['cc'] = 'avr-gcc'
        self.e['cxx'] = 'avr-g++'
        self.e['ar'] = 'avr-ar'
        self.e['objcopy'] = 'avr-objcopy'

        self.e['cflags'] = SpaceList([
            '-ffunction-sections',
            '-fdata-sections',
            '-g', '-gstabs',
            '-Os', 
            '-Wl,--gc-sections',
            '-mmcu=atmega328p',
            '-DF_CPU=16000000',
            '-DARDUINO=22',
            '-lm',
            '-I' + self.e['arduino_core_dir'],
        ])

        self.e['names'] = {
            'obj': '%s.o',
            'lib': 'lib%s.a',
        }

    def create_jinja(self):
        jenv = jinja2.Environment(
            undefined=StrictUndefined, # bark on Undefined render
            extensions=['jinja2.ext.do'])

        # inject @filters from ino.filters
        for name, f in inspect.getmembers(ino.filters, lambda x: getattr(x, 'filter', False)):
            jenv.filters[name] = f

        # inject globals
        jenv.globals['e'] = self.e
        jenv.globals['SpaceList'] = SpaceList

        return jenv

    def run(self, args):
        self.discover()

        jenv = self.create_jinja()
        template = args.template or os.path.join(os.path.dirname(__file__), '..', 'Makefile.jinja')
        with open(template) as f:
            template = jenv.from_string(f.read())

        makefile_contents = template.render()
        makefile_path = os.path.join(self.e['build_dir'], 'Makefile')
        with open(makefile_path, 'wt') as f:
            f.write(makefile_contents)

        p = subprocess.Popen(['make', '-f', makefile_path, 'all'])
