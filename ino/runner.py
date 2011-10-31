#!/usr/bin/env python
# -*- coding: utf-8; -*-

"""\
Ino is a command-line toolkit for working with Arduino hardware.

It is intended to replace Arduino IDE UI for those who prefer to work in
terminal or want to integrate Arduino development in a 3rd party IDE.

Ino can build sketches, libraries, upload firmwares, establish
serial-communication. For this it is split in a bunch of subcommands, like git
or mercurial do. The full list is provided below. You may run any of them with
--help to get further help. E.g.:

    ino build --help
"""

import sys
import os.path
import argparse
import inspect

from configobj import ConfigObj

import ino.commands

from ino.commands.base import Command
from ino.exc import Abort
from ino.filters import colorize
from ino.environment import Environment
from ino.argparsing import FlexiFormatter


def configure():
    etc = ConfigObj('/etc/ino.ini')
    home = ConfigObj(os.path.expanduser('~/.inorc'))
    cwd = ConfigObj('ino.ini')
    cfg = etc
    cfg.merge(home)
    cfg.merge(cwd)
    return cfg


def main():
    e = Environment()
    e.load()

    conf = configure()
    conf_scalars = dict((key, conf[key]) for key in conf.scalars)

    try:
        current_command = sys.argv[1]
    except IndexError:
        current_command = None

    parser = argparse.ArgumentParser(prog='ino', formatter_class=FlexiFormatter, description=__doc__)
    subparsers = parser.add_subparsers()
    is_command = lambda x: inspect.isclass(x) and issubclass(x, Command) and x != Command
    commands = [cls(e) for _, cls in inspect.getmembers(ino.commands, is_command)]
    for cmd in commands:
        p = subparsers.add_parser(cmd.name, formatter_class=FlexiFormatter, help=cmd.help_line)
        if current_command != cmd.name:
            continue
        cmd.setup_arg_parser(p)
        conf_defaults = conf_scalars.copy()
        conf_defaults.update(conf.get(cmd.name, {}))
        p.set_defaults(func=cmd.run, **conf_defaults)

    args = parser.parse_args()
    e.process_args(args)

    if current_command not in 'clean init' and not os.path.isdir(e.build_dir):
        os.mkdir(e.build_dir)

    try:
        args.func(args)
    except Abort as exc:
        print colorize(str(exc), 'red')
        sys.exit(1)
    except KeyboardInterrupt:
        print 'Terminated by user'
    finally:
        e.dump()
