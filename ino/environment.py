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

    def find_dir(self, key, items, places, human_name=None):
        if key in self:
            return
        human_name = human_name or key
        print 'Searching for', human_name, '...',
        for p in places:
            if any(os.path.exists(os.path.join(p, i)) for i in items):
                print colorize(p, 'green')
                self[key] = p
                return
        print colorize('FAILED', 'red')
        raise Abort("%s not found. Searched in following places: %s" %
                    (human_name, ''.join(['\n  - ' + p for p in places])))

    def find_tool(self, key, items, places=None, human_name=None):
        if key in self:
            return
        human_name = human_name or key
        places = places or ['$PATH']

        # expand env variables in `places` and split on colons
        places = itertools.chain.from_iterable(os.path.expandvars(p).split(os.pathsep) for p in places)
        places = list(places)

        print 'Searching for', human_name, '...',
        for p in places:
            for i in items:
                path = os.path.join(p, i)
                if os.path.exists(path):
                    print colorize(path, 'green')
                    self[key] = path
                    return
        print colorize('FAILED', 'red')
        raise Abort("%s not found. Searched in following places: %s" %
                    (human_name, ''.join(['\n  - ' + p for p in places])))
