#!/usr/bin/env python

import base64
import commands
import numpy
import random
import sys
import time
import urllib2

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


def get_next_line_tokens(fh):

    aLine = fh.readline()

    if (len(aLine) == 0):
        return (-1, [])

    if (len(aLine) > 0):
        if (aLine[-1] == '\n'):
            aLine = aLine[:-1]
    if (len(aLine) > 0):
        if (aLine[-1] == '\r'):
            aLine = aLine[:-1]

    tokenList = aLine.split('\t')
    numTokens = len(tokenList)
    return (numTokens, tokenList)

#------------------------------------------------------------------------------


def file_size(fh):

    # get current position
    curPos = fh.tell()

    # next go to the end of the file
    fh.seek(0, 2)
    endPos = fh.tell()
    numBytes = endPos

    # now go back to what was the current position
    fh.seek(curPos)

    return (numBytes)

#------------------------------------------------------------------------------


def num_lines(fh):

    # get current position
    curPos = fh.tell()

    # next go to the beginning of the file
    fh.seek(0)

    # then loop over all of the lines and count ...
    numLines = 0
    for aLine in fh:
        numLines += 1

    # finally, go back to where we were before ...
    fh.seek(curPos)

    return (numLines)

#------------------------------------------------------------------------------


def num_cols(fh, delChar=''):

    # get current position
    curPos = fh.tell()

    # read one line
    aLine = fh.readline()

    # split into tokens
    if (delChar == ''):
        tokenList = aLine.split()
    else:
        tokenList = aLine.split(delChar)
    numTokens = len(tokenList)

    # go back to where we were before
    fh.seek(curPos)

    return (numTokens)

#------------------------------------------------------------------------------


def make_random_fname(lenRname=8):

    alpha = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    rname = ''
    for ii in range(lenRname):
        rname += random.choice(alpha)

    # print rname
    rname += '.' + str(time.time()) + '.scratch'
    # print rname

    return (rname)

#------------------------------------------------------------------------------


def delete_file(fname):

    cmdString = "rm -f " + fname
    (status, output) = commands.getstatusoutput(cmdString)

    return (status)

#------------------------------------------------------------------------------


def extract_column(fname, ithCol):

    # print ' in extract_column : ', fname, ithCol

    try:
        fh = file(fname)
    except:
        print ' error opening file in extract_column : ', fname
        return ([])

    numLines = num_lines(fh)

    z = numpy.zeros(numLines)

    numTokens = -1

    for iLine in range(numLines):
        aLine = fh.readline()
        tokenList = aLine.split()
        if (numTokens == -1):
            numTokens = len(tokenList)
        else:
            if (len(tokenList) != numTokens):
                continue
        if (ithCol >= numTokens):
            print ' error in extract_column : ', fname, ithCol, len(tokenList)
            return ([])
        z[iLine] = float(tokenList[ithCol])

    fh.close()

    # print len(z)
    # print z[:10], z[-10:]

    return (z)

#------------------------------------------------------------------------------


def read_list_from_file(aFile):

    try:
        fh = file(aFile, 'r')
    except:
        print " ERROR opening file <%s> in read_list_from_file "
        sys.exit(-1)

    aList = []
    for aLine in fh:
        aLine = aLine.strip()
        tokenList = aLine.split()
        for aToken in tokenList:
            if (aToken not in aList):
                aList += [aToken]

    fh.close()
    return (aList)

#------------------------------------------------------------------------------


def open_input_file_for_reading(aFile):

    if (aFile.endswith('.gz')):
        bFile = aFile[:-3]
        cmdString = "gunzip %s" % aFile
        (status, output) = commands.getstatusoutput(cmdString)
        if (status != 0):
            print ' ERROR ??? failed to unzip <%s> ' % aFile
            try:
                fh = file(bFile)
                return (fh, 0)
            except:
                print ' ERROR ??? failed to open <%s> ' % bFile
        else:
            try:
                fh = file(bFile)
                return (fh, 1)
            except:
                print ' ERROR ??? failed to open <%s> ' % bFile

    else:
        fh = file(aFile)
        return (fh, 0)

    print ' ERROR in open_input_file_for_reading ... FAILED TO OPEN FILE '
    return (-1, -1)

    print ' ERROR ??? should not get here ??? '
    sys.exit(-1)

#------------------------------------------------------------------------------
