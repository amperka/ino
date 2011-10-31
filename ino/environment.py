# -*- coding: utf-8; -*-

import os.path
import itertools
import argparse
import pickle

from collections import OrderedDict

from ino.filters import colorize
from ino.utils import format_available_options
from ino.exc import Abort


class Environment(dict):

    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    build_dir = '.build'
    src_dir = 'src'
    lib_dir = 'lib'
    hex_filename = 'firmware.hex'

    arduino_dist_dir = None
    arduino_dist_dir_guesses = [
        '/usr/local/share/arduino',
        '/usr/share/arduino',
    ]

    default_board_model = 'uno'

    def dump(self):
        if not os.path.isdir(self.build_dir):
            return
        with open(self.dump_filepath, 'wb') as f:
            pickle.dump(self.items(), f)

    def load(self):
        if not os.path.exists(self.dump_filepath):
            return
        with open(self.dump_filepath, 'rb') as f:
            try:
                self.update(pickle.load(f))
            except:
                print colorize('Environment dump exists (%s), but failed to load' % 
                               self.dump_filepath, 'yellow')

    @property
    def dump_filepath(self):
        return os.path.join(self.build_dir, 'environment.pickle')

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
        places = map(os.path.expanduser, places)

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
        return self._find(key, items or ['.'], places, human_name, join=False)

    def find_file(self, key, items, places=None, human_name=None):
        return self._find(key, items, places, human_name, join=True)

    def find_tool(self, key, items, places=None, human_name=None):
        return self.find_file(key, items, places or ['$PATH'], human_name)

    def find_arduino_dir(self, key, dirname_parts, items=None, human_name=None):
        return self.find_dir(key, items, self._arduino_dist_places(dirname_parts), human_name)

    def find_arduino_file(self, key, dirname_parts, human_name=None):
        return self.find_file(key, [key], self._arduino_dist_places(dirname_parts), human_name)

    def find_arduino_tool(self, key, filename_parts, human_name=None):
        return self.find_arduino_file(key, filename_parts, human_name)

    def _arduino_dist_places(self, dirname_parts):
        """
        For `dirname_parts` like [a, b, c] return list of
        search paths within Arduino distribution directory like:
            /user/specified/path/a/b/c
            /usr/local/share/arduino/a/b/c
            /usr/share/arduino/a/b/c
        """
        places = []
        if 'arduino_dist_dir' in self:
            places.append(self['arduino_dist_dir'])
        places.extend(self.arduino_dist_dir_guesses)
        return [os.path.join(p, *dirname_parts) for p in places]

    def board_models(self):
        if 'board_models' in self:
            return self['board_models']

        boards_txt = self.find_arduino_file('boards.txt', ['hardware', 'arduino'], 
                                            human_name='Board description file (boards.txt)')

        self['board_models'] = BoardModelDict()
        with open(boards_txt) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                multikey, val = line.split('=')
                multikey = multikey.split('.')

                subdict = self['board_models']
                for key in multikey[:-1]:
                    if key not in subdict:
                        subdict[key] = {}
                    subdict = subdict[key]

                subdict[multikey[-1]] = val

        return self['board_models']
    
    def add_board_model_arg(self, parser):
        try:
            boards = self.board_models()
        except Abort:
            boards = {}

        parser.add_argument('-m', '--board-model', metavar='MODEL', 
                            default=self.default_board_model,
                            type=boards,
                            choices=boards.keys(),
                            help='Arduino board model. See below.')

        if boards:
            board_map = [(key, val['name']) for key, val in boards.iteritems()]
            epilog = 'Supported Arduino board models:\n\n'
            epilog += format_available_options(board_map, head_width=12, default=self.default_board_model)
        else:
            epilog = "Board description file (boards.txt) not found, so board model list is unavailable.\n" \
                     "Use --arduino-dist option to specify its location."

        parser.epilog = epilog + (parser.epilog or '')

    def add_arduino_dist_arg(self, parser):
        parser.add_argument('-d', '--arduino-dist', metavar='PATH', 
                            help='Path to Arduino distribution, e.g. ~/Downloads/arduino-0022.\nTry to guess if not specified')

    def process_args(self, args):
        arduino_dist = getattr(args, 'arduino_dist', None)
        if arduino_dist:
            self['arduino_dist_dir'] = arduino_dist


class BoardModelDict(OrderedDict):
    def __call__(self, model):
        try:
            return self[model]
        except KeyError:
            raise argparse.ArgumentTypeError("%s is not a valid board model" % model)

    def __hash__(self):
        return hash(tuple(self.keys()))
