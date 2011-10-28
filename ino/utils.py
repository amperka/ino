# -*- coding: utf-8; -*-

import os.path


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


def list_subdirs(dirname):
    entries = [os.path.join(dirname, entry) for entry in os.listdir(dirname)]
    return filter(os.path.isdir, entries)
