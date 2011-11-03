# -*- coding: utf-8; -*-

from ino.commands.base import Command


class ListModels(Command):
    """
    Print list of supported Arduino board models.

    These could be used as a value for --board-model or -m command
    line switch for build and upload subcommands.

    Symbolic model names as well as their descriptions are fetched
    from `boards.txt' file within found Arduino distribution.
    """

    name = 'list-models'
    help_line = 'List supported Arduino board models'

    def setup_arg_parser(self, parser):
        super(ListModels, self).setup_arg_parser(parser)
        self.e.add_arduino_dist_arg(parser)

    def run(self, args):
        print self.e.board_models().format()
