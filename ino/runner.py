#!/usr/bin/env python
# -*- coding: utf-8; -*-

import argparse
import inspect

import ino.commands


class Environment(object):
    pass


def main():
    parser = argparse.ArgumentParser(description='Arduino command line environment')
    subparsers = parser.add_subparsers()
    is_command = lambda x: inspect.isclass(x) and \
            issubclass(x, ino.commands.Command) and x != ino.commands.Command
    env = Environment()
    commands = [cls(env) for _, cls in inspect.getmembers(ino.commands, is_command)]
    for cmd in commands:
        p = subparsers.add_parser(cmd.name)
        cmd.setup_arg_parser(p)
        p.set_defaults(func=cmd.run)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
