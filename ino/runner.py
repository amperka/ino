#!/usr/bin/env python
# -*- coding: utf-8; -*-

import sys
import os.path
import argparse
import inspect

import ino.commands

from ino.commands.base import Command, CommandError


class Environment(dict):
    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__()
        self['templates_dir'] = os.path.join(os.path.dirname(__file__), '..', 'templates')

        self['src_dir'] = 'src'
        self['build_dir'] = build_dir = '.build'
        if not os.path.isdir(build_dir):
            os.mkdir(build_dir)

def main():
    parser = argparse.ArgumentParser(description='Arduino command line environment')
    subparsers = parser.add_subparsers()
    is_command = lambda x: inspect.isclass(x) and issubclass(x, Command) and x != Command
    env = Environment()
    commands = [cls(env) for _, cls in inspect.getmembers(ino.commands, is_command)]
    for cmd in commands:
        p = subparsers.add_parser(cmd.name)
        cmd.setup_arg_parser(p)
        p.set_defaults(func=cmd.run)
    args = parser.parse_args()

    try:
        args.func(args)
    except CommandError as e:
        print e
        sys.exit(1)


if __name__ == '__main__':
    main()
