# -*- coding: utf-8; -*-

import os.path

from configobj import ConfigObj


class Configuration(object):
    def __init__(self, *files):
        self.cfg = ConfigObj()
        for f in files:
            self.cfg.merge(ConfigObj(os.path.expanduser(f)))

    def as_dict(self, section_name):
        section = self.cfg.get(section_name, ConfigObj())
        result = self._as_plain_dict(self.cfg)
        result.update(self._as_plain_dict(section))
        return result

    def _as_plain_dict(self, section):
        return dict((key.replace('-', '_'), section[key]) for key in section.scalars)


def configure():
    return Configuration('/etc/ino.ini', '~/.inorc', 'ino.ini')
