# -*- coding: utf-8; -*-

import os.path
import itertools


class SpaceList(list):
    def __add__(self, other):
        return SpaceList(super(SpaceList, self).__add__(other))

    def __str__(self):
        return ' '.join(map(str, self))

    def paths(self):
        return SpaceList(getattr(x, 'path', x) for x in self)


class FileMap(dict):
    __iter__ = dict.iteritems

    def sources(self):
        return SpaceList(self.iterkeys())

    def targets(self):
        return SpaceList(self.itervalues())

    def iterpaths(self):
        for source, target in self:
            yield (source.path, target.path)

    def target_paths(self):
        return SpaceList(x.path for x in self.targets())


def list_subdirs(dirname, recursive=False, exclude=[]):
    entries = [e for e in os.listdir(dirname) if e not in exclude and not e.startswith('.')]
    paths = [os.path.join(dirname, e) for e in entries]
    dirs = filter(os.path.isdir, paths)
    if recursive:
        sub = itertools.chain.from_iterable(
            list_subdirs(d, recursive=True, exclude=exclude) for d in dirs)
        dirs.extend(sub)
    return dirs


def format_available_options(items, head_width, head_color='cyan', 
                             default=None, default_mark="[DEFAULT]", 
                             default_mark_color='red'):
    from ino.filters import colorize
    default_mark = colorize(default_mark + ' ', default_mark_color)
    lines = ['%s: %s%s' % (colorize('%%%ds' % head_width % key, head_color), 
                           default_mark if key == default else '', 
                           val) 
             for key, val in items]
    return '\n'.join(lines)
