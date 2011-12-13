# -*- coding: utf-8; -*-

import subprocess

from ino.commands.base import Command


class Serial(Command):
    """
    Open a serial monitor to communicate with the device.

    At the moment `picocom' is used as a program started by this command.
    Use Ctrl+A Ctrl+X to exit.
    """

    name = 'serial'
    help_line = "Open a serial monitor"

    def setup_arg_parser(self, parser):
        super(Serial, self).setup_arg_parser(parser)
        parser.add_argument('-p', '--serial-port', metavar='PORT',
                            help='Serial port to communicate with\nTry to guess if not specified')
        parser.add_argument('-b', '--baud-rate', metavar='RATE', type=int, default=9600, 
                            help='Communication baud rate, should match value set in Serial.begin() on Arduino')

    def run(self, args):
        serial_monitor = self.e.find_tool('serial', ['picocom'], human_name='Serial monitor (picocom)')
        serial_port = args.serial_port or self.e.guess_serial_port()

        subprocess.call([
            serial_monitor,
            serial_port,
            '-b', str(args.baud_rate),
            '-l',
        ])
