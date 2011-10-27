# -*- coding: utf-8; -*-

import shutil

from ino.commands.base import Command


class Clean(Command):

    name = 'clean'

    def run(self, args):
        shutil.rmtree(self.e['build_dir'])
