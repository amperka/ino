# -*- coding: utf-8; -*-

import textwrap


class Command(object):
    name = None
    help_line = None

    def __init__(self, environment):
        self.e = environment

    def setup_arg_parser(self, parser):
        if self.__doc__:
            parser.description = textwrap.dedent(self.__doc__)

    def run(self, args):
        raise NotImplementedError
