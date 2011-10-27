# -*- coding: utf-8; -*-

import os.path
import fnmatch


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
