# -*- coding: utf-8; -*-

class SpaceList(list):
    def __str__(self):
        return ' '.join(map(str, self))
