# -*- coding: utf-8; -*-


class Command(object):
    name = None

    def __init__(self, environment):
        self.e = environment

    def setup_arg_parser(self, parser):
        pass

    def epilog(self):
        return None

    def run(self, args):
        raise NotImplementedError
