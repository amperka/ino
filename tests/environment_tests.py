# -*- coding: utf-8; -*-

from nose.tools import assert_equal

from ino.environment import Version


class TestVersion(object):
    def test_parsing(self):
        assert_equal(Version.parse('0022'), (0, 22, 0))
        assert_equal(Version.parse('0022ubuntu0.1'), (0, 22, 0))
        assert_equal(Version.parse('0022-macosx-20110822'), (0, 22, 0))
        assert_equal(Version.parse('1.0'), (1, 0, 0))
        assert_equal(Version.parse('1:1.0.5+dfsg2-1'), (1, 0, 5))

    def test_int_conversion(self):
        assert_equal(Version(0, 22, 0).as_int(), 22)
        assert_equal(Version(1, 0, 0).as_int(), 100)
        assert_equal(Version(1, 0, 5).as_int(), 105)
        assert_equal(Version(1, 5, 1).as_int(), 151)
