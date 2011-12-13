# -*- coding: utf-8; -*-

from __future__ import absolute_import

import os.path
import subprocess
import platform

from time import sleep
from serial import Serial
from serial.serialutil import SerialException

from ino.commands.base import Command
from ino.exc import Abort


class Upload(Command):
    """
    Upload built firmware to the device.

    The firmware must be already explicitly built with `ino build'. If current
    device firmare reads/writes serial port extensively, upload may fail. In
    that case try to retry few times or upload just after pushing Reset button
    on Arduino board.
    """

    name = 'upload'
    help_line = "Upload built firmware to the device"

    def setup_arg_parser(self, parser):
        super(Upload, self).setup_arg_parser(parser)
        parser.add_argument('-p', '--serial-port', metavar='PORT',
                            help='Serial port to upload firmware to\nTry to guess if not specified')

        self.e.add_board_model_arg(parser)
        self.e.add_arduino_dist_arg(parser)

    def discover(self):
        self.e.find_tool('stty', ['stty'])
        if platform.system() == 'Linux':
            self.e.find_arduino_tool('avrdude', ['hardware', 'tools'])
            self.e.find_arduino_file('avrdude.conf', ['hardware', 'tools'])
        else:
            self.e.find_arduino_tool('avrdude', ['hardware', 'tools', 'avr', 'bin'])
            self.e.find_arduino_file('avrdude.conf', ['hardware', 'tools', 'avr', 'etc'])
    
    def run(self, args):
        self.discover()
        port = args.serial_port or self.e.guess_serial_port()
        board = self.e.board_model(args.board_model)

        protocol = board['upload']['protocol']
        if protocol == 'stk500':
            # if v1 is not specifid explicitly avrdude will
            # try v2 first and fail
            protocol = 'stk500v1'

        if not os.path.exists(port):
            raise Abort("%s doesn't exist. Is Arduino connected?" % port)

        # send a hangup signal when the last process closes the tty
        file_switch = '-f' if platform.system() == 'Darwin' else '-F'
        ret = subprocess.call([self.e['stty'], file_switch, port, 'hupcl'])
        if ret:
            raise Abort("stty failed")

        # pulse on DTR
        try:
            s = Serial(port, 115200)
        except SerialException as e:
            raise Abort(str(e))
        s.setDTR(False)
        sleep(0.1)
        s.setDTR(True)

        # call avrdude to upload .hex
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
