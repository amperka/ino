# -*- coding: utf-8; -*-

import sys
import re

from ino.commands.base import Command
from ino.exc import Abort


class Preprocess(Command):
    """
    Preprocess an .ino or .pde sketch file and produce ready-to-compile .cpp source.

    Ino mimics steps that are performed by official Arduino Software to
    produce similar result:

        * Either #include <Arduino.h> or <WProgram.h> is prepended
        * Function prototypes are added at the beginning of file
    """

    name = 'preproc'
    help_line = "Transform a sketch file into valid C++ source"

    def setup_arg_parser(self, parser):
        super(Preprocess, self).setup_arg_parser(parser)
        self.e.add_arduino_dist_arg(parser)
        parser.add_argument('sketch', help='Input sketch file name')
        parser.add_argument('-o', '--output', default='-', help='Output source file name (default: use stdout)')

    def run(self, args):
        if args.output == '-':
            out = sys.stdout
        else:
            out = open(args.output, 'wt')

        sketch = open(args.sketch, 'rt').read()

        header = 'Arduino.h' if self.e.arduino_lib_version.major else 'WProgram.h'
        out.write('#include <%s>\n' % header)
        out.write('\n'.join(self.prototypes(sketch)))
        out.write('\n#line 1 "%s"\n' % args.sketch)
        out.write(sketch)

    def prototypes(self, src):
        src = self.collapse_braces(self.strip(src))
        regex = re.compile("[\\w\\[\\]\\*]+\\s+[&\\[\\]\\*\\w\\s]+\\([&,\\[\\]\\*\\w\\s]*\\)(?=\\s*\\{)")
        matches = regex.findall(src)
        return [m + ';' for m in matches]

    def collapse_braces(self, src):
        """
        Remove the contents of all top-level curly brace pairs {}.
        """
        result = []
        nesting = 0;

        for c in src:
            if not nesting:
                result.append(c)
            if c == '{':
                nesting += 1
            elif c == '}':
                nesting -= 1
                result.append(c)
        
        return ''.join(result)

    def strip(self, src):
        """
        Strips comments, pre-processor directives, single- and double-quoted
        strings from a string.
        """
        # single-quoted character
        p = "('.')"
        
        # double-quoted string
        p += "|(\"(?:[^\"\\\\]|\\\\.)*\")"
        
        # single and multi-line comment
        p += "|(//.*?$)|(/\\*[^*]*(?:\\*(?!/)[^*]*)*\\*/)"
        
        # pre-processor directive
        p += "|" + "(^\\s*#.*?$)"

        regex = re.compile(p, re.MULTILINE)
        return regex.sub(' ', src)
