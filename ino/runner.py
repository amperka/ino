#!/usr/bin/env python
# -*- coding: utf-8; -*-

import sys
import os.path
import argparse
import inspect

import ino.commands

from ino.commands.base import Command
from ino.exc import Abort
from ino.filters import colorize
from ino.environment import Environment
from ino.argparsing import FlexiFormatter


def main():
    e = Environment()

    parser = argparse.ArgumentParser(prog='ino', description='Arduino command line environment')
    subparsers = parser.add_subparsers()
    is_command = lambda x: inspect.isclass(x) and issubclass(x, Command) and x != Command
    commands = [cls(e) for _, cls in inspect.getmembers(ino.commands, is_command)]
    for cmd in commands:
        p = subparsers.add_parser(cmd.name, formatter_class=FlexiFormatter)
        cmd.setup_arg_parser(p)
        p.set_defaults(func=cmd.run)

    args = parser.parse_args()

    try:
        args.func(args)
    except Abort as e:
        print colorize(str(e), 'red')
        sys.exit(1)
    except KeyboardInterrupt:
        print 'Terminated by user'


if __name__ == '__main__':
    main()
