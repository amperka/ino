# -*- coding: utf-8; -*-

from nose.tools import assert_equal

from ino.environment import Version


class TestVersion(object):
    def test_parsing(self):
        assert_equal(Version.parse('0022'), (0, 22))
        assert_equal(Version.parse('0022ubuntu0.1'), (0, 22))
        assert_equal(Version.parse('0022-macosx-20110822'), (0, 22))
        assert_equal(Version.parse('1.0'), (1, 0))
