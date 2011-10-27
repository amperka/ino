# -*- coding: utf-8; -*-

import os.path
import itertools

from ino.filters import colorize
from ino.exc import Abort


class Environment(dict):

    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    build_dir = '.build'
    src_dir = 'src'
    hex_filename = 'firmware.hex'

    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)
        if not os.path.isdir(self.build_dir):
            os.mkdir(self.build_dir)

    def __getitem__(self, key):
        try:
            return super(Environment, self).__getitem__(key)
        except KeyError as e:
            try:
                return getattr(self, key)
            except AttributeError:
                raise e

    def __getattr__(self, attr):
        try:
            return super(Environment, self).__getitem__(attr)
        except KeyError:
            raise AttributeError("Environment has no attribute %r" % attr)

    @property
    def hex_path(self):
        return os.path.join(self.build_dir, self.hex_filename)

    def _find(self, key, items, places, human_name, join):
        if key in self:
            return self[key]

        human_name = human_name or key

        # expand env variables in `places` and split on colons
        places = itertools.chain.from_iterable(os.path.expandvars(p).split(os.pathsep) for p in places)
        places = list(places)

        print 'Searching for', human_name, '...',
        for p in places:
            for i in items:
                path = os.path.join(p, i)
                if os.path.exists(path):
                    result = path if join else p
                    print colorize(result, 'green')
                    self[key] = result
                    return result

        print colorize('FAILED', 'red')
        raise Abort("%s not found. Searched in following places: %s" %
                    (human_name, ''.join(['\n  - ' + p for p in places])))

    def find_dir(self, key, items, places, human_name=None):
        return self._find(key, items, places, human_name, join=False)

    def find_tool(self, key, items, places=None, human_name=None):
        return self._find(key, items, places or ['$PATH'], human_name, join=True)
