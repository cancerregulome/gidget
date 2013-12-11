import copy
import csv
import sys

__author__ = 'anorberg'

import tsv
import re

"""
Trivial script to reprocess a MAF file such that:
1. Comment lines are removed.
2. All lines are the same length.
"""


def noComment(fileLike, commentPattern):
    pattern = re.compile(commentPattern)
    for line in fileLike:
        if not pattern.match(line):
            yield line


def main(argv=sys.argv):
    output = sys.stdout
    input = sys.stdin
    if len(argv) > 2:
        if argv[2] != '-':
            output = open(argv[2], "w")
    if len(argv) > 1:
        if argv[1] != '-':
            input = open(argv[1], "rU")

    cleanwriter = copy.copy(csv.excel_tab)
    cleanwriter.lineterminator = "\n"
    tsv.fixRaggedTable(noComment(input, "#"), output, cleanwriter)

if __name__ == "__main__":
    main()
