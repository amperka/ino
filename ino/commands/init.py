# -*- coding: utf-8; -*-

import os.path
import shutil

from configobj import ConfigObj

from ino.commands.base import Command
from ino.exc import Abort
from ino.utils import format_available_options, list_subdirs


class Init(Command):
    """
    Setup a new project in the current directory.

    The directory must be empty.
    """

    name = 'init'
    help_line = "Setup a new project in the current directory"

    default_template = 'empty'

    def setup_arg_parser(self, parser):
        super(Init, self).setup_arg_parser(parser)
        parser.add_argument('-t', '--template', default=self.default_template, 
                            help='Project template to use')

        parser.epilog = "Available probject templates:\n\n"

        template_items = []
        for tdir in list_subdirs(self.e.templates_dir):
            try:
                description = ConfigObj(os.path.join(tdir, 'manifest.ini'))['description']
            except KeyError:
                description = ''
            template_items.append((os.path.basename(tdir), description))

        parser.epilog += format_available_options(template_items, head_width=12, 
                                                  default=self.default_template)

    def run(self, args):
        try:
            copytree(os.path.join(self.e['templates_dir'], args.template),
                     '.', ignore=lambda *args: ['manifest.ini'])
        except shutil.Error as e:
            raise Abort(str(e))


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
