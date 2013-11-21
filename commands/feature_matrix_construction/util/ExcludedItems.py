#!/usr/bin/env python
#
# Output file of excluded TCGA samples base on
# 1. TSV file of Annotations from TCGAs annotation manager
# 2. Set of terms for blacklisting, single Annotation "Classification"s or a ("Classification","Category") pairs
#
# Output is to standard out, and contains the *excluded* samples
# The TSV file is obtained from downloading from https://tcga-data.nci.nih.gov/annotations/
# or by processing Annotation server JSON output with json_AnnotationsMangerTCGA_to_tsv.py (Kalle Leinonen)
# The Classification and Annotation fields are assumed to be in columns 5 and 6 of TSV (no check performed)
#
import sys
import re

if (len(sys.argv) != 3):
    print 'error!  usage:  ExcludedSamples.py <SampleTSV> <Blacklisted Annotations File>\n'
    sys.exit()

samptsv = sys.argv[1]
blacktermfile = sys.argv[2]

try:
    slines = open(samptsv).read().split('\n')
except:
    print 'error! failed to open or read from <%s> ' % samptsv
    sys.exit(-1)

sys.stderr.write('')

header = slines[0]  # header will be used for output
slines = slines[1:-1]
nslines = len(slines)
sys.stderr.write('Found %d entries in sample tsv file \n' % nslines)

blines = open(blacktermfile).read().split('\n')
blines = blines[:-1]
nblines = len(blines)
sys.stderr.write('Found %d annotations for exclude list \n' % nblines)

sys.stderr.write('')

singles = []  # list of single Annotation Classifications for exclusion
# list of single Annotation Classifications + Annotation Categories for
# exclusion
doubles = []
for line in blines:
    toks = line.split('\t')
    if len(toks) == 1:
        singles.append(toks[0])
    if len(toks) == 2:
        doubles.append(toks[0] + ',' + toks[1])

print header  # Original header
numEx = 0
for line in slines:
    toks = line.split('\t')
    acat = toks[4].strip("\"")  # Annotation Classification
    aclass = toks[5].strip("\"")  # Annotation Category
    aa = acat + ',' + aclass  # Both
    if acat in singles:
        print line
        numEx += 1
    if aa in doubles:
        print line
        numEx += 1

sys.stderr.write('%d lines written out based on exclusion rules \n' % numEx)
sys.stderr.write('')
