#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# -*- mode: python; indent-tabs-mode nil; tab-width 4; python-indent 4; -*-

"""usage: gidget [options] <command>

Options:
    -h, --help    Show this screen
    --version

gidget commands are:
    help
    list
    describe
    add
    remove
    run

"""

import sys
from docopt import docopt


if __name__ == '__main__':

    # print detailed help by default
    if len(sys.argv) < 2:
        sys.argv.append("--help")

    print docopt(__doc__,
                 version='gidget version 0.0.1',
                 options_first=True)
