# -*- coding: utf-8; -*-

import os.path
import inspect
import subprocess
import jinja2

from jinja2.runtime import StrictUndefined

import ino.filters

from ino.commands.base import Command
from ino.utils import SpaceList
from ino.exc import Abort


class Build(Command):

    name = 'build'

    def setup_arg_parser(self, parser):
        try:
            boards = self.e.board_models()
        except Abort:
            boards = {}

        parser.add_argument('-m', '--board-model', metavar='MODEL', default='uno', choices=boards.keys(),
                            help='Arduino board model. See below.')

        parser.add_argument('-d', '--arduino-dist', metavar='PATH',
                            help='Path to Arduino distribution, e.g. ~/Downloads/arduino-0022.\nTry to guess if not specified')

        parser.add_argument('-t', '--template', 
                            help='Jinja2 makefile template to use.\nUse built-in default if not specified')

    def epilog(self):
        try:
            boards = self.e.board_models()
        except Abort:
            return "Board description file (boards.txt) not found, so board model list is unavailable.\n" \
                    "Use --arduino-dist option to specify its location."

        c = ino.filters.colorize
        default_mark = c('[DEFAULT] ', 'red')
        boards = ['%s: %s%s' % (c('%12s' % key, 'cyan'), default_mark if key == 'uno' else '', val['name']) 
                  for key, val in boards.iteritems()]

        return '\n'.join(['Supported Arduino board models:\n'] + boards)

    def discover(self):
        self.e.find_arduino_dir('arduino_core_dir', 
                                ['hardware', 'arduino', 'cores', 'arduino'], 
                                ['WProgram.h'], 
                                'Arduino core library')

        self.e.find_tool('cc', ['avr-gcc'], human_name='avr-gcc')
        self.e.find_tool('cxx', ['avr-g++'], human_name='avr-g++')
        self.e.find_tool('ar', ['avr-ar'], human_name='avr-ar')
        self.e.find_tool('objcopy', ['avr-objcopy'], human_name='avr-objcopy')

    def setup_flags(self, board):
        self.e['cflags'] = SpaceList([
            '-ffunction-sections',
            '-fdata-sections',
            '-mmcu=' + board['build']['mcu'],
            '-g',
            '-Os', 
            '-w',
            '-DF_CPU=' + board['build']['f_cpu'],
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
        self.setup_flags(self.e.board_models()[args.board_model])

        jenv = self.create_jinja()
        template = args.template or os.path.join(os.path.dirname(__file__), '..', 'Makefile.jinja')
        with open(template) as f:
            template = jenv.from_string(f.read())

        makefile_contents = template.render()
        makefile_path = os.path.join(self.e['build_dir'], 'Makefile')
        with open(makefile_path, 'wt') as f:
            f.write(makefile_contents)

        subprocess.call(['make', '-f', makefile_path, 'all'])
