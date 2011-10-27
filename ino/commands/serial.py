# -*- coding: utf-8; -*-

import subprocess

from ino.commands.base import Command


class Serial(Command):

    name = 'serial'

    def setup_arg_parser(self, parser):
        parser.add_argument('-p', '--serial-port', metavar='PORT', default='/dev/ttyACM0', 
                            help='Serial port to communicate with')
        parser.add_argument('-b', '--baud-rate', metavar='RATE', type=int, default=9600, 
                            help='Communication baud rate, should match value set in Serial.begin() on Arduino')

    def run(self, args):
        serial_monitor = 'picocom'
        subprocess.call([
            serial_monitor,
            args.serial_port,
            '-b', str(args.baud_rate),
            '-l',
        ])
