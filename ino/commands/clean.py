# -*- coding: utf-8; -*-

import os.path
import shutil

from ino.commands.base import Command


class Clean(Command):
    """
    Remove all intermediate compilation files and directories completely.

    In fact `.build' directory is simply removed.
    """

    name = 'clean'
    help_line = "Remove intermediate compilation files completely"

    def run(self, args):
        if os.path.isdir(self.e.build_dir):
            shutil.rmtree(self.e.build_dir)
