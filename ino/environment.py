# -*- coding: utf-8; -*-

import os.path


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
