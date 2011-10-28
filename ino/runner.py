#!/usr/bin/env python
# -*- coding: utf-8; -*-

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

    parser = argparse.ArgumentParser(prog='ino', description='Arduino command line environment')
    subparsers = parser.add_subparsers()
    is_command = lambda x: inspect.isclass(x) and issubclass(x, Command) and x != Command
    commands = [cls(e) for _, cls in inspect.getmembers(ino.commands, is_command)]
    for cmd in commands:
        p = subparsers.add_parser(cmd.name, formatter_class=FlexiFormatter)
        cmd.setup_arg_parser(p)
        conf_defaults = conf_scalars.copy()
        conf_defaults.update(conf.get(cmd.name, {}))
        p.set_defaults(func=cmd.run, **conf_defaults)

    args = parser.parse_args()
    e.process_args(args)

    try:
        args.func(args)
    except Abort as exc:
        print colorize(str(exc), 'red')
        sys.exit(1)
    except KeyboardInterrupt:
        print 'Terminated by user'
    finally:
        e.dump()


if __name__ == '__main__':
    main()
