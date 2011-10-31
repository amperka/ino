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
        parser.add_argument('-p', '--serial-port', metavar='PORT', default='/dev/ttyACM0', 
                            help='Serial port to upload firmware to\n(default: %(default)s)')

        self.e.add_board_model_arg(parser)
        self.e.add_arduino_dist_arg(parser)

    def discover(self):
        self.e.find_tool('stty', ['stty'])
        self.e.find_arduino_tool('avrdude', ['hardware', 'tools'])
        self.e.find_arduino_file('avrdude.conf', ['hardware', 'tools'])
    
    def run(self, args):
        self.discover()
        port = args.serial_port
        board = args.board_model

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
