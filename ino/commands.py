# -*- coding: utf-8; -*-

import os.path
import shutil
import jinja2
import subprocess


class Command(object):
    name = None

    def __init__(self, env):
        self.env = env

    def setup_arg_parser(self, parser):
        pass

    def run(self, args):
        raise NotImplementedError


def command(name):
    def decorator(cls):
        cls.name = name
        return cls
    return decorator


class CommandError(Exception):
    pass


def copytree(src, dst, symlinks=False, ignore=None):
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


@command('init')
class Init(Command):
    def setup_arg_parser(self, parser):
        parser.add_argument('-t', '--template', default='blink', help='Project template to use')

    def run(self, args):
        try:
            copytree(os.path.join(self.env['templates_dir'], args.template), '.')
        except shutil.Error as e:
            raise CommandError(str(e))


@command('build')
class Build(Command):
    def setup_arg_parser(self, parser):
        parser.add_argument('-t', '--template', help='Jinja makefile template to use')

    def run(self, args):
        jinja_env = jinja2.Environment()
        template = args.template or os.path.join(os.path.dirname(__file__), 'Makefile.jinja')
        with open(template) as f:
            template = jinja_env.from_string(f.read())
        makefile_contents = template.render(env=self.env)
        makefile_path = os.path.join(self.env['build_dir'], 'Makefile')
        with open(makefile_path, 'wt') as f:
            f.write(makefile_contents)
        p = subprocess.Popen(['make', '-f', makefile_path])


@command('upload')
class Upload(Command):
    def setup_arg_parser(self, parser):
        parser.add_argument('-d', '--device', help='USB-device to upload firmware to')

    def run(self, args):
        pass


@command('serial')
class Serial(Command):
    def setup_arg_parser(self, parser):
        parser.add_argument('-d', '--device', help='USB-device to upload firmware to')

    def run(self, args):
        pass
