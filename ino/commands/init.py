# -*- coding: utf-8; -*-

import os.path
import shutil

from ino.commands.base import Command, CommandError


class Init(Command):

    name = 'init'

    def setup_arg_parser(self, parser):
        parser.add_argument('-t', '--template', default='blink', help='Project template to use')

    def run(self, args):
        try:
            copytree(os.path.join(self.e['templates_dir'], args.template), '.')
        except shutil.Error as e:
            raise CommandError(str(e))


def copytree(src, dst, symlinks=False, ignore=None):
    """
    Tweaked version of shutil.copy tree that allows to copy
    to current directory
    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if dst == '.':
        if os.listdir(dst):
            raise shutil.Error('Current directory is not empty')
    else:
        os.makedirs(dst)

    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                shutil.copy2(srcname, dstname)
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
    if errors:
        raise shutil.Error(errors)
