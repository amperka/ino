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
        self.e.find_arduino_dir('arduino_core_dir', 
                                ['hardware', 'arduino', 'cores', 'arduino'], 
                                ['WProgram.h'], 
                                'Arduino core library')

        self.e.find_tool('cc', ['avr-gcc'], human_name='avr-gcc')
        self.e.find_tool('cxx', ['avr-g++'], human_name='avr-g++')
        self.e.find_tool('ar', ['avr-ar'], human_name='avr-ar')
        self.e.find_tool('objcopy', ['avr-objcopy'], human_name='avr-objcopy')

        self.e['cflags'] = SpaceList([
            '-ffunction-sections',
            '-fdata-sections',
            '-mmcu=atmega328p',
            '-g',
            '-Os', 
            '-w',
            '-DF_CPU=16000000',
            '-DARDUINO=22',
            '-I' + self.e['arduino_core_dir'],
        ])

        self.e['cxxflags'] = SpaceList([
            '-fno-exceptions'
        ])

        self.e['elfflags'] = SpaceList([
            '-Os', 
            '-Wl,--gc-sections', 
            '-mmcu=atmega328p',
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

        subprocess.call(['make', '-f', makefile_path, 'all'])
