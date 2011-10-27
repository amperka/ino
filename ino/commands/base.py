# -*- coding: utf-8; -*-


class Command(object):
    name = None

    def __init__(self, environment):
        self.e = environment

    def setup_arg_parser(self, parser):
        pass

    def run(self, args):
        raise NotImplementedError
