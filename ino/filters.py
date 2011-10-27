# -*- coding: utf-8; -*-

import sys
import os.path
import fnmatch
import functools

from ino.utils import FileMap


class GlobFile(object):
    def __init__(self, filename, dirname):
        self.filename = filename
        self.dirname = dirname

    @property
    def path(self):
        return os.path.join(self.dirname, self.filename)

    def __str__(self):
        return self.filename


def filter(f):
    f.filter = True
    return f


@filter
def glob(dir, *patterns):
    result = []
    for f in os.listdir(dir):
        if any(fnmatch.fnmatch(f, p) for p in patterns):
            result.append(GlobFile(f, dir))
    return result


@filter
def pjoin(base, *parts):
    return os.path.join(str(base), *map(str, parts))


def xname(filepath, basename_fmt):
    head, tail = os.path.split(str(filepath))
    basename, _ = os.path.splitext(tail)
    return os.path.join(head, basename_fmt % basename)


@filter
def objname(filepath):
    return xname(filepath, '%s.o')


@filter
def libname(filepath):
    return xname(filepath, 'lib%s.a')


@filter
def filemap(sources, target_dir, rename_rule):
    return FileMap((source, GlobFile(xname(source, rename_rule), target_dir)) 
                   for source in sources)


@filter
def colorize(s, color):
    if not sys.stdout.isatty():
        return s

    ccodes = {
        'cyan':     '96',
        'purple':   '95',
        'blue':     '94',
        'green':    '92',
        'yellow':   '93',
        'red':      '91',
    }

    return ''.join([
        '\033[', ccodes[color], 'm', 
        s,
        '\033[0m'
    ])
