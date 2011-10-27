# -*- coding: utf-8; -*-

from __future__ import absolute_import

import os.path
import subprocess

from time import sleep
from serial import Serial
from serial.serialutil import SerialException

from ino.commands.base import Command
from ino.exc import Abort


class Upload(Command):

    name = 'upload'

    def setup_arg_parser(self, parser):
        parser.add_argument('-p', '--serial-port', metavar='PORT', default='/dev/ttyACM0', 
                            help='Serial port to upload firmware to\n(default: %(default)s)')

        try:
            boards = self.e.board_models()
        except Abort:
            boards = {}

        parser.add_argument('-m', '--board-model', metavar='MODEL', default='uno', choices=boards.keys(),
                            help='Arduino board model. See below.')

        parser.add_argument('-d', '--arduino-dist', metavar='PATH',
                            help='Path to Arduino distribution, e.g. ~/Downloads/arduino-0022.\nTry to guess if not specified')

    def epilog(self):
        try:
            boards = self.e.board_models()
        except Abort:
            return "Board description file (boards.txt) not found, so board model list is unavailable.\n" \
                    "Use --arduino-dist option to specify its location."

        import ino.filters
        c = ino.filters.colorize
        default_mark = c('[DEFAULT] ', 'red')
        boards = ['%s: %s%s' % (c('%12s' % key, 'cyan'), default_mark if key == 'uno' else '', val['name']) 
                  for key, val in boards.iteritems()]

        return '\n'.join(['Supported Arduino board models:\n'] + boards)

    def discover(self):
        self.e.find_tool('stty', ['stty'])
        self.e.find_arduino_tool('avrdude', ['hardware', 'tools'], ['avrdude'])
        self.e.find_arduino_file('avrdude.conf', ['hardware', 'tools'], ['avrdude.conf'])
    
    def run(self, args):
        self.discover()
        port = args.serial_port
        board = self.e.board_models()[args.board_model]

        protocol = board['upload']['protocol']
        if protocol == 'stk500':
            # if v1 is not specifid explicitly avrdude will
            # try v2 first and fail
            protocol = 'stk500v1'

        if not os.path.exists(port):
            raise Abort("%s doesn't exist. Is Arduino connected?" % port)

        ret = subprocess.call([self.e['stty'], '-F', port, 'hupcl'])
        if ret:
            raise Abort("stty failed")

        # pulse on dtr
        try:
            s = Serial(port, 115200)
        except SerialException as e:
            raise Abort(str(e))

        s.setDTR(False)
        sleep(0.1)
        s.setDTR(True)

        subprocess.call([
            self.e['avrdude'],
            '-C', self.e['avrdude.conf'],
            '-p', board['build']['mcu'],
            '-P', port,
            '-c', protocol,
            '-b', board['upload']['speed'],
            '-D',
            '-U', 'flash:w:%s:i' % self.e['hex_path'],
        ])
