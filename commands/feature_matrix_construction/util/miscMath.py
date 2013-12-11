#!/usr/bin/env python

import math
import numpy
import random
import scipy.stats
import sys

#------------------------------------------------------------------------------


def ln(x):

    if (x < 1.e-300):
        return (-696.969)
    else:
        return (math.log(x))

#------------------------------------------------------------------------------


def log2(x, strictFlag=0):

    if (strictFlag):
        if (x < 1.e-300):
            print " ERROR !!! cannot log a negative number !!! ", x
            sys.exit(-1)

    return (ln(x) / ln(2.))

#------------------------------------------------------------------------------


def make_window(wLen, wType):

    w = numpy.ones(wLen)

    if (wType == "Rect"):
        return (w)

    elif (wType == "Hann"):
        for ii in range(wLen):
            phi = (2. * math.pi * float(ii)) / float(wLen - 1)
            w[ii] = 0.5 * (1. - math.cos(phi))
        return (w)

    elif (wType == "Hamming"):
        for ii in range(wLen):
            phi = (2. * math.pi * float(ii)) / float(wLen - 1)
            w[ii] = 0.53836 - (0.46164 * math.cos(phi))
        return (w)

    elif (wType == "Nuttall"):
        for ii in range(wLen):
            phi1 = (2. * math.pi * float(ii)) / float(wLen - 1)
            phi2 = 2. * phi1
            phi3 = 3. * phi1
            w[ii] = 0.355768 - (0.487396 * math.cos(phi1) ) + \
                (0.144232 * math.cos(phi2) ) - \
                (0.012604 * math.cos(phi3))
        return (w)

    elif (wType == "Blackman-Nuttall"):
        for ii in range(wLen):
            phi1 = (2. * math.pi * float(ii)) / float(wLen - 1)
            phi2 = 2. * phi1
            phi3 = 3. * phi1
            w[ii] = 0.3635819 - (0.4891775 * math.cos(phi1) ) + \
                (0.1365995 * math.cos(phi2) ) - \
                (0.0106411 * math.cos(phi3))
        return (w)

    else:
        print ' ERROR in make_window ... invalid window type : ', wType
        sys.exit(-1)

#------------------------------------------------------------------------------


def linear_regression(xVals, yVals):

    numVals = len(xVals)
    if (numVals != len(yVals)):
        print ' ERROR in linearRegression '
        sys.exit(-1)

    xMu = xVals.mean()
    yMu = yVals.mean()

    xVar = xVals.var()
    yVar = yVals.var()

    xSS = xVar * numVals
    ySS = yVar * numVals

    xySS = -numVals * xMu * yMu
    # print ' xySS ... init ', xySS
    for ii in range(numVals):
        xySS += (xVals[ii] * yVals[ii])
        # print ' xySS ... ', ii, xVals[ii], yVals[ii], xySS

    if (0):
        print '         N : ', numVals
        print '         x : ', xMu, math.sqrt(xVar)
        print '         y : ', yMu, math.sqrt(yVar)
        print '         xy : ', (xySS / float(numVals))
        print '         xySS = %f   xSS = %f ' % (xySS, xSS)
        print '         %f ' % (xySS / xSS)

    # for y = a + b x :
    b = xySS / xSS
    a = yMu - (b * xMu)

    # if we have essentially zero slope (ySS=0) then we might get problems
    # here ...
    try:
        r = math.sqrt(xySS * xySS / (xSS * ySS))
    except:
        if (ySS < 1.e-9):
            print ' possible error in linear regression ??? '
            print xSS, yXX, xySS
            r = 1.
        else:
            print ' ERROR in linear Regression ??? '
            print xSS, ySS, xySS
            print xVals
            print yVals
            sys.exit(-1)

    # print '                 offset =', a
    # print '                  slope =', b
    # print '                      r =', r
    if (0):
        if (numpy.isnan(r)):
            print numVals
            print xMu, yMu
            print xVar, yVar
            print xSS, ySS, xySS
            print a, b, r

            if (numpy.isnan(yMu)):
                for ii in range(len(yVals)):
                    print ii, yVals[ii]

    return (a, b, r)

#------------------------------------------------------------------------------


def linear_regression2(xVals, yVals):

    numVals = len(xVals)
    if (numVals != len(yVals)):
        print ' ERROR in linearRegression '
        sys.exit(-1)

    print ' N : ', numVals

    xMu = xVals.mean()
    yMu = yVals.mean()

    fTop = 0.
    fBot = 0.
    for ii in range(numVals):
        fTop += ((xVals[ii] - xMu) * (yVals[ii] - yMu))
        fBot += ((xVals[ii] - xMu) * (xVals[ii] - xMu))

    b1 = fTop / fBot
    b0 = yMu - (b1 * xMu)

    print b1, b0

    sys.exit(-1)


#------------------------------------------------------------------------------

def windowed_DFT(x, size, wType):

    bigN = len(x)

    # we will either truncate or zero-pad the input vector ...
    # NOTE that it the windowing MUST be done BEFORE zero-padding !!
    # but if we are truncating, we truncate FIRST, and THEN window ...

    if (bigN < size):
        # print '     --> NOTE : zero-padding vector out from %d to %d \n' % (
        # bigN, size )

        w = make_window(bigN, wType)
        wx = w * x

        numZeroes = size - bigN
        numZleft = numZeroes / 2
        numZright = numZeroes - numZleft

        zLeft = numpy.zeros(numZleft)
        zRight = numpy.zeros(numZright)
        x = numpy.hstack((zLeft, wx, zRight))

        bigN = len(x)

    elif (bigN > size):
        # print '     --> NOTE : trimming vector down from %d to %d \n' % (
        # bigN, size )

        x = x[0:size]
        bigN = len(x)

        w = miscMath.make_window(bigN, wType)
        x = w * x

    # finally we can do the FFT and then return the magnitude only ...
    Nhalf = (bigN / 2) + 1
    tmpZ = numpy.fft.fft(x)
    bigX = abs(tmpZ[0:Nhalf])

    return (bigX)

#------------------------------------------------------------------------------


def make_two_sided(x):

    revX = x[:0:-1]
    newX = numpy.hstack((revX, x))

    return (newX)

#------------------------------------------------------------------------------
# this function computes the dot-product between two vectors x and y which
# must be of the same length ...


def dotProduct(x, y):

    if not (len(x) == len(y)):
        print ' ERROR in dotProduct ... %d = %d ??? ' % (len(x), len(y))
        return

    if (0):
        for ii in range(len(x)):
            print ' %6d  %10.5f  %10.5f ' % (ii, x[ii], y[ii])

    dp = 0.
    for ii in range(len(x)):
        if (x[ii] != 0):
            if (y[ii] != 0):
                dp += (x[ii] * y[ii])

    return (dp)


#------------------------------------------------------------------------------

def calcCorrelation(x, y):

    from math import sqrt

    if (len(x) != len(y)):
        print ' ERROR in correlation ... %d = %d ??? ' % (len(x), len(y))
        return

    meanX = x.mean()
    meanY = y.mean()

    meanXY = dotProduct(x, y) / float(len(x))
    meanXX = dotProduct(x, x) / float(len(x))
    meanYY = dotProduct(y, y) / float(len(x))

    rhoXY = (meanXY - (meanX * meanY))
    rhoXY /= sqrt(meanXX - (meanX * meanX))
    rhoXY /= sqrt(meanYY - (meanY * meanY))

    return (rhoXY)

#------------------------------------------------------------------------------


def slidingCorrelation(x, y, kMax):

    if (len(x) < len(y)):
        a = x
        b = y
    else:
        a = y
        b = x

    aLen = len(a)
    bLen = len(b)

    kkStart = -kMax
    kkStop = kMax + (bLen - aLen)

    if (0):
        print ' in slidingCorrelation ... '
        print aLen, bLen, kkStart, kkStop
        print ' short vector A : '
        for jj in range(aLen):
            print jj, a[jj]
        print ' long vector B : '
        for ii in range(bLen):
            print ii, b[ii]

    dpMaxNeg = 0.
    dpMaxPos = 0.
    bestKneg = 0
    bestKpos = 0

    useNorm = 0

    # print ' looping over : ', kkStart, kkStop+1
    for kk in range(kkStart, kkStop + 1):
        dp = 0.
        nn = 0
        for ii in range(bLen):
            jj = ii - kk
            if (jj < 0):
                continue
            if (jj >= aLen):
                continue
            dp += (b[ii] * a[jj])
            # print ii, jj, b[ii], a[jj], dp
            nn += 1

        # print kk, dp

        if (nn > 0):
            dpNorm = dp / float(nn)
        else:
            dpNorm = 0.

        if (useNorm):
            dpUse = dpNorm
        else:
            dpUse = dp

        if (dpUse > dpMaxPos):
            dpMaxPos = dpUse
            bestKpos = kk

        if (dpUse < dpMaxNeg):
            dpMaxNeg = dpUse
            bestKneg = kk

    dpMaxNeg = abs(dpMaxNeg)

    # print '         from slidingCorrelation : ', dpMaxPos, bestKpos,
    # dpMaxNeg, bestKneg
    return (dpMaxPos, bestKpos, dpMaxNeg, bestKneg)

#------------------------------------------------------------------------------


def reverseVec(x):

    y = numpy.zeros(len(x))
    for ii in range(len(x)):
        y[ii] = x[-ii]

    return (y)

#------------------------------------------------------------------------------


def normVec(x):

    meanX = x.mean()
    sigmaX = x.std()
    # print '         >>>> in normVec : ', len(x), meanX, sigmaX
    for ii in range(len(x)):
        x[ii] = (x[ii] - meanX) / sigmaX

    return (x)

#------------------------------------------------------------------------------


def smoothVec(x, nWin):

    halfWin = nWin / 2
    if (halfWin < 1):
        return (x)

    numX = len(x)
    tmpX = numpy.zeros(numX)

    for ii in range(numX):
        j1 = max(0, ii - halfWin)
        j2 = min(ii + halfWin + 1, numX)
        tmpSum = 0.
        for jj in range(j1, j2):
            tmpSum += x[jj]
        tmpX[ii] = tmpSum / float(j2 - j1)

    return (tmpX)

#------------------------------------------------------------------------------
# there are lots of ways to downsample :
#	dsFlag=0	take every Nth sample
#	dsFlag=1	average groups of N samples
#	dsFlag=2	max over groups of N samples


def downSampleVec(x, dsN, dsFlag):

    numIn = len(x)
    numOut = int((float(numIn) / float(dsN)) + 0.5)

    outVec = numpy.zeros(numOut)

    for ii in range(numOut):

        j1 = ii * dsN
        j2 = min((j1 + dsN), numIn)
        jMid = (j1 + j2) / 2

        sumJJ = 0.
        numJJ = 0
        maxJJ = x[j1]

        if (dsFlag != 0):
            for jj in range(j1, j2):
                if (dsFlag == 1):
                    sumJJ += x[jj]
                    numJJ += 1
                elif (dsFlag == 2):
                    if (maxJJ < x[jj]):
                        maxJJ = x[jj]

        if (dsFlag == 0):
            outVec[ii] = x[jMid]
        elif (dsFlag == 1):
            outVec[ii] = sumJJ / float(numJJ)
        elif (dsFlag == 2):
            outVec[ii] = maxJJ
        else:
            print ' ERROR in downSampleVec : invalid dsFlag '
            print dsN, dsFlag
            sys.exit(-1)

    return (outVec)

#------------------------------------------------------------------------------


def PearsonCorr(x, y):

    if (len(x) != len(y)):
        print ' FATAL ERROR in miscMath.PearsonCorr ... ', len(x), len(y)
        sys.exit(-1)

    (r, p) = scipy.stats.pearsonr(numpy.array(x), numpy.array(y))

    return (r, p)

#------------------------------------------------------------------------------


def SpearmanCorr(x, y):

    if (len(x) != len(y)):
        print ' FATAL ERROR in miscMath.SpearmanCorr ... ', len(x), len(y)
        sys.exit(-1)

    (r, p) = scipy.stats.spearmanr(numpy.array(x), numpy.array(y))

    return (r, p)

#------------------------------------------------------------------------------


def lnFactorial(n):

    # print ' in lnFactorial ... ', n

    # if n is not too big, calculate ...
    logNfact = 0
    if (n < 100):
        for kk in range(1, n + 1):
            logNfact += math.log(float(kk))
        # print '         exact : ', logNfact, math.exp(logNfact)
        return (logNfact)

    # Stirling's approximation :
    part1 = math.log(math.sqrt(2. * math.pi * float(n)))
    part2 = float(n) * math.log((float(n) / math.e))
    logNfact = part1 + part2

    # print '         approx logNfact : ', logNfact

    return (logNfact)

#------------------------------------------------------------------------------


def Factorial(n):

    return (math.exp(lnFactorial(n)))

#------------------------------------------------------------------------------


def getGammaShapeScale(zMean, zSigma):

    if (zMean <= 0.):
        print ' ERROR in getGammaShapeScale ... mean must be positive !!! ', zMean
        sys.exit(-1)

    zVar = zSigma * zSigma
    bScale = zVar / zMean
    aShape = zMean / bScale

    return (aShape, bScale)

#------------------------------------------------------------------------------


def generateGammaRVs(aShape, bScale, count, histDelta):

    rVec = numpy.zeros(count)
    rMax = 0.
    for ii in range(count):
        rVec[ii] = random.gammavariate(aShape, bScale)
        if (rMax < rVec[ii]):
            rMax = rVec[ii]

    # build the histogram ...
    deltaR = histDelta
    rMinHist = 0.
    rMaxHist = rMax + 2. * deltaR
    numBins = (rMaxHist - rMinHist) / deltaR
    numBins = int(numBins) + 2

    rHist = numpy.zeros(numBins)

    print ' making histogram ... ', deltaR, rMaxHist
    for ii in range(count):
        iBin = int((rVec[ii] - rMinHist) / deltaR + 0.0001)
        rHist[iBin] += 1

    for iBin in range(numBins):
        rHist[iBin] /= float(count)

    return (rVec, rHist)

#------------------------------------------------------------------------------


def getBetaAlphaBeta(zMean, zSigma):

    if (zMean <= 0.):
        print ' ERROR in getBetaAlphaBeta ... mean must be positive !!! ', zMean
        sys.exit(-1)

    zVar = zSigma * zSigma
    alpha = zMean * ((zMean * (1. - zMean) / zVar) - 1.)
    beta = (1. - zMean) * ((zMean * (1. - zMean) / zVar) - 1.)

    return (alpha, beta)

#------------------------------------------------------------------------------


def generateBetaRVs(alpha, beta, count, histDelta):

    rVec = numpy.zeros(count)
    rMax = 0.
    for ii in range(count):
        rVec[ii] = random.betavariate(alpha, beta)
        if (rMax < rVec[ii]):
            rMax = rVec[ii]

    # build the histogram ...
    deltaR = histDelta
    rMinHist = 0.
    rMaxHist = rMax + 2. * deltaR
    numBins = (rMaxHist - rMinHist) / deltaR
    numBins = int(numBins) + 2

    rHist = numpy.zeros(numBins)

    print ' making histogram ... ', deltaR, rMaxHist
    for ii in range(count):
        iBin = int((rVec[ii] - rMinHist) / deltaR + 0.0001)
        rHist[iBin] += 1

    for iBin in range(numBins):
        rHist[iBin] /= float(count)

    return (rVec, rHist)

#------------------------------------------------------------------------------


def generateLogNormalRVs(mu, sigma, count, histDelta):

    rVec = numpy.zeros(count)
    rMax = 0.
    for ii in range(count):
        rVec[ii] = random.lognormvariate(mu, sigma)
        if (rMax < rVec[ii]):
            rMax = rVec[ii]

    # build the histogram ...
    deltaR = histDelta
    rMinHist = 0.
    rMaxHist = rMax + 2. * deltaR
    numBins = (rMaxHist - rMinHist) / deltaR
    numBins = int(numBins) + 2

    rHist = numpy.zeros(numBins)

    # print ' making histogram ... ', deltaR, rMaxHist
    for ii in range(count):
        iBin = int((rVec[ii] - rMinHist) / deltaR + 0.0001)
        rHist[iBin] += 1

    for iBin in range(numBins):
        rHist[iBin] /= float(count)

    return (rVec, rHist)

#------------------------------------------------------------------------------


def ltqnorm(p):
    """
    Modified from the author's original perl code (original comments follow below)
    by dfield@yahoo-inc.com.  May 3, 2004.

    Lower tail quantile for standard normal distribution function.

    This function returns an approximation of the inverse cumulative
    standard normal distribution function.  I.e., given P, it returns
    an approximation to the X satisfying P = Pr{Z <= X} where Z is a
    random variable from the standard normal distribution.

    The algorithm uses a minimax approximation by rational functions
    and the result has a relative error whose absolute value is less
    than 1.15e-9.

    Author:      Peter J. Acklam
    Time-stamp:  2000-07-19 18:26:14
    E-mail:      pjacklam@online.no
    WWW URL:     http://home.online.no/~pjacklam
    """

    if p <= 0 or p >= 1:
        # The original perl code exits here, we'll throw an exception instead
        raise ValueError(
            "Argument to ltqnorm %f must be in open interval (0,1)" % p)

    # Coefficients in rational approximations.
    a = (-3.969683028665376e+01,  2.209460984245205e+02,
         -2.759285104469687e+02,  1.383577518672690e+02,
         -3.066479806614716e+01,  2.506628277459239e+00)
    b = (-5.447609879822406e+01,  1.615858368580409e+02,
         -1.556989798598866e+02,  6.680131188771972e+01,
         -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00,  2.938163982698783e+00)
    d = (7.784695709041462e-03,  3.224671290700398e-01,
         2.445134137142996e+00,  3.754408661907416e+00)

    # Define break-points.
    plow = 0.02425
    phigh = 1 - plow

    # Rational approximation for lower region:
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)

    # Rational approximation for upper region:
    if phigh < p:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)

    # Rational approximation for central region:
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)

#------------------------------------------------------------------------------


def normInv(p, mu, sigma):

    z = ltqnorm(p)
    return (z * sigma + mu)

#------------------------------------------------------------------------------
# this function returns the Gaussian PDF at x for N(mu,sigma)


def normPDF(x, mu, sigma):

    p = math.exp ( (-1. * (x - mu) * (x - mu)) / (2. * sigma * sigma) ) \
        / math.sqrt(2. * math.pi * sigma * sigma)

    if (p == 0):
        lnP = lnNormPDF(x, mu, sigma)
        log10P = lnP / math.log(10.)
        print '    --> normPDF result is 0 ... log10(p) = ', log10P

    return (p)

#------------------------------------------------------------------------------


def lnNormPDF(x, mu, sigma):

    lnP = -1. * math.log(math.sqrt(2. * math.pi) * sigma)
    lnP -= ((x - mu) * (x - mu) / (2. * sigma * sigma))

    return (lnP)

#------------------------------------------------------------------------------
# this function returns the cumulative distribution function for N(mu,sigma)


def normCDF(x, mu, sigma):

    p = 0.5 * (1 + Erf((x - mu) / (sigma * math.sqrt(2.))))
    return (p)

#------------------------------------------------------------------------------
# this function returns the complementary CDF for N(mu,sigma) at x
# note that for x > 0.4 sigma, the complementary CDF is always less than
# the PDF(x) so that can be used as a conservative upper bound ...
#	at x = 1.6 sigma, CCDF(x) ~ PDF(x)/2.
# 	at x = 5.0 sigma, CCDF(x) ~ PDF(x)/5.
#	at x = 8.0 sigma, CCDF(x) ~ PDF(x)/8.


def normCCDF(x, mu, sigma):

    print ' in normCCDF ... '
    p = 0.5 * (Erfc((x - mu) / (sigma * math.sqrt(2.))))

    if (p == 0.):
        print '     --> cumCDF p = zero '
        q = normPDF(x, mu, sigma)
        if (q == 0):
            print '         --> even the PDF is zero ! ', q
            lnQ = lnNormPDF(x, mu, sigma)
            print '             log_10(p) = ', (lnQ / math.log(10.))
            return (p)
        else:
            print '         PDF value = ', q
            dx = sigma / 10.
            z = x
            qSum = 0.
            done = 0
            while not done:
                q = normPDF(z, mu, sigma)
                if (q == 0):
                    done = 1
                qSum += (q * dx)
                # print '         integrating ... ', z, q, qSum
                z += dx
            print '         after integrating : ', qSum
            return (qSum)

    return (p)

#------------------------------------------------------------------------------

'''error function and complementary error function
'''

# /*
# * ====================================================
# * Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
# *
# * Developed at SunPro, a Sun Microsystems, Inc. business.
# * Permission to use, copy, modify, and distribute this
# * software is freely granted, provided that this notice
# * is preserved.
# * ====================================================
# */
#
# /* double erf(double x)
# * double erfc(double x)
# * original code from: http://sourceware.org/cgi-bin/cvsweb.cgi/~checkout~/src/newlib/libm/math/s_erf.c?rev=1.1.1.1&cvsroot=src
# * 		     x
# *		      2      |\
# *     erf(x)  =  ---------  | exp(-t*t)dt
# *	 	   sqrt(pi) \|
# *			     0
# *
# *     erfc(x) =  1-erf(x)
# *  Note that
# *		erf(-x) = -erf(x)
# *		erfc(-x) = 2 - erfc(x)
# *
# * Method:
# *	1. For |x| in [0, 0.84375]
# *	    erf(x)  = x + x*R(x^2)
# *          erfc(x) = 1 - erf(x)           if x in [-.84375,0.25]
# *                  = 0.5 + ((0.5-x)-x*R)  if x in [0.25,0.84375]
# *	   where R = P/Q where P is an odd poly of degree 8 and
# *	   Q is an odd poly of degree 10.
# *						 -57.90
# *			| R - (erf(x)-x)/x | <= 2
# *
# *
# *	   Remark. The formula is derived by noting
# *          erf(x) = (2/sqrt(pi))*(x - x^3/3 + x^5/10 - x^7/42 + ....)
# *	   and that
# *          2/sqrt(pi) = 1.128379167095512573896158903121545171688
# *	   is close to one. The interval is chosen because the fix
# *	   point of erf(x) is near 0.6174 (i.e., erf(x)=x when x is
# *	   near 0.6174), and by some experiment, 0.84375 is chosen to
# * 	   guarantee the error is less than one ulp for erf.
# *
# *      2. For |x| in [0.84375,1.25], let s = |x| - 1, and
# *         c = 0.84506291151 rounded to single (24 bits)
# *         	erf(x)  = sign(x) * (c  + P1(s)/Q1(s))
# *         	erfc(x) = (1-c)  - P1(s)/Q1(s) if x > 0
# *			  1+(c+P1(s)/Q1(s))    if x < 0
# *         	|P1/Q1 - (erf(|x|)-c)| <= 2**-59.06
# *	   Remark: here we use the taylor series expansion at x=1.
# *		erf(1+s) = erf(1) + s*Poly(s)
# *			 = 0.845.. + P1(s)/Q1(s)
# *	   That is, we use rational approximation to approximate
# *			erf(1+s) - (c = (single)0.84506291151)
# *	   Note that |P1/Q1|< 0.078 for x in [0.84375,1.25]
# *	   where
# *		P1(s) = degree 6 poly in s
# *		Q1(s) = degree 6 poly in s
# *
# *      3. For x in [1.25,1/0.35(~2.857143)],
# *         	erfc(x) = (1/x)*exp(-x*x-0.5625+R1/S1)
# *         	erf(x)  = 1 - erfc(x)
# *	   where
# *		R1(z) = degree 7 poly in z, (z=1/x^2)
# *		S1(z) = degree 8 poly in z
# *
# *      4. For x in [1/0.35,28]
# *         	erfc(x) = (1/x)*exp(-x*x-0.5625+R2/S2) if x > 0
# *			= 2.0 - (1/x)*exp(-x*x-0.5625+R2/S2) if -6<x<0
# *			= 2.0 - tiny		(if x <= -6)
# *         	erf(x)  = sign(x)*(1.0 - erfc(x)) if x < 6, else
# *         	erf(x)  = sign(x)*(1.0 - tiny)
# *	   where
# *		R2(z) = degree 6 poly in z, (z=1/x^2)
# *		S2(z) = degree 7 poly in z
# *
# *      Note1:
# *	   To compute exp(-x*x-0.5625+R/S), let s be a single
# *	   precision number and s := x; then
# *		-x*x = -s*s + (s-x)*(s+x)
# *	        exp(-x*x-0.5626+R/S) =
# *			exp(-s*s-0.5625)*exp((s-x)*(s+x)+R/S);
# *      Note2:
# *	   Here 4 and 5 make use of the asymptotic series
# *			  exp(-x*x)
# *		erfc(x) ~ ---------- * ( 1 + Poly(1/x^2) )
# *			  x*sqrt(pi)
# *	   We use rational approximation to approximate
# *      	g(s)=f(1/x^2) = log(erfc(x)*x) - x*x + 0.5625
# *	   Here is the error bound for R1/S1 and R2/S2
# *      	|R1/S1 - f(x)|  < 2**(-62.57)
# *      	|R2/S2 - f(x)|  < 2**(-61.52)
# *
# *      5. For inf > x >= 28
# *         	erf(x)  = sign(x) *(1 - tiny)  (raise inexact)
# *         	erfc(x) = tiny*tiny (raise underflow) if x > 0
# *			= 2 - tiny if x<0
# *
# *      7. Special case:
# *         	erf(0)  = 0, erf(inf)  = 1, erf(-inf) = -1,
# *         	erfc(0) = 1, erfc(inf) = 0, erfc(-inf) = 2,
# *	   	erfc/erf(NaN) is NaN
# */

## from math import *

tiny = 1e-300
half = 5.00000000000000000000e-01
one = 1.00000000000000000000e+00
two = 2.00000000000000000000e+00
erx = 8.45062911510467529297e-01

# Coefficients for approximation to  erf on [0,0.84375]

efx = 1.28379167095512586316e-01
efx8 = 1.02703333676410069053e+00
pp0 = 1.28379167095512558561e-01
pp1 = -3.25042107247001499370e-01
pp2 = -2.84817495755985104766e-02
pp3 = -5.77027029648944159157e-03
pp4 = -2.37630166566501626084e-05
qq1 = 3.97917223959155352819e-01
qq2 = 6.50222499887672944485e-02
qq3 = 5.08130628187576562776e-03
qq4 = 1.32494738004321644526e-04
qq5 = -3.96022827877536812320e-06


def erf1(x):
    '''erf(x) for x in [0,0.84375]'''
    e, i = math.frexp(x)
    if abs(i) > 28:
        if abs(i) > 57:
            return 0.125 * (8.0 * x + efx8 * x)
        return x + efx * x
    z = x * x
    r = pp0 + z * (pp1 + z * (pp2 + z * (pp3 + z * pp4)))
    s = one + z * (qq1 + z * (qq2 + z * (qq3 + z * (qq4 + z * qq5))))
    y = r / s
    return x + x * y


def erfc1(x):
    '''erfc(x)for x in [0,0.84375]'''
    e, i = math.frexp(x)
    if abs(i) > 56:
        return one - x
    z = x * x
    r = pp0 + z * (pp1 + z * (pp2 + z * (pp3 + z * pp4)))
    s = one + z * (qq1 + z * (qq2 + z * (qq3 + z * (qq4 + z * qq5))))
    y = r / s
    if (x < 0.25):
        return one - (x + x * y)
    else:
        r = x * y
        r += (x - half)
        return half - r

# Coefficients for approximation to  erf  in [0.84375,1.25]

pa0 = -2.36211856075265944077e-03
pa1 = 4.14856118683748331666e-01
pa2 = -3.72207876035701323847e-01
pa3 = 3.18346619901161753674e-01
pa4 = -1.10894694282396677476e-01
pa5 = 3.54783043256182359371e-02
pa6 = -2.16637559486879084300e-03
qa1 = 1.06420880400844228286e-01
qa2 = 5.40397917702171048937e-01
qa3 = 7.18286544141962662868e-02
qa4 = 1.26171219808761642112e-01
qa5 = 1.36370839120290507362e-02
qa6 = 1.19844998467991074170e-02


def erf2(x):
    '''erf(x) for x in [0.84375,1.25]'''
    s = math.fabs(x) - one
    P = pa0 + s * \
        (pa1 + s * (pa2 + s * (pa3 + s * (pa4 + s * (pa5 + s * pa6)))))
    Q = one + s * \
        (qa1 + s * (qa2 + s * (qa3 + s * (qa4 + s * (qa5 + s * qa6)))))
    if x >= 0:
        return erx + P / Q
    return -erx - P / Q


def erfc2(x):
    '''erfc(x) for x in [0.84375, 1.25]'''
    return one - erf2(x)

# Coefficients for approximation to  erfc in [1.25,1/0.35]

ra0 = -9.86494403484714822705e-03
ra1 = -6.93858572707181764372e-01
ra2 = -1.05586262253232909814e+01
ra3 = -6.23753324503260060396e+01
ra4 = -1.62396669462573470355e+02
ra5 = -1.84605092906711035994e+02
ra6 = -8.12874355063065934246e+01
ra7 = -9.81432934416914548592e+00
sa1 = 1.96512716674392571292e+01
sa2 = 1.37657754143519042600e+02
sa3 = 4.34565877475229228821e+02
sa4 = 6.45387271733267880336e+02
sa5 = 4.29008140027567833386e+02
sa6 = 1.08635005541779435134e+02
sa7 = 6.57024977031928170135e+00
sa8 = -6.04244152148580987438e-02


def erf3(x):
    '''erf(x) for x in [1.25,2.857142]'''
    x0 = x
    x = math.fabs(x)
    s = one / (x * x)
    R = ra0 + s * \
        (ra1 + s *
         (ra2 + s * (ra3 + s * (ra4 + s * (ra5 + s * (ra6 + s * ra7))))))
    S = one + s * \
        (sa1 + s *
         (sa2 + s * (sa3 + s * (sa4 + s * (sa5 + s * (sa6 + s * (sa7 + s * sa8)))))))
    z = math.ldexp(x0, 0)
    r = math.exp(-z * z - 0.5625) * math.exp((z - x) * (z + x) + R / S)
    if(x0 >= 0):
        return one - r / x
    else:
        return r / x - one


def erfc3(x):
    '''erfc(x) for x in [1.25,1/0.35]'''
    return one - erf3(x)

# Coefficients for approximation to  erfc in [1/.35,28]

rb0 = -9.86494292470009928597e-03
rb1 = -7.99283237680523006574e-01
rb2 = -1.77579549177547519889e+01
rb3 = -1.60636384855821916062e+02
rb4 = -6.37566443368389627722e+02
rb5 = -1.02509513161107724954e+03
rb6 = -4.83519191608651397019e+02
sb1 = 3.03380607434824582924e+01
sb2 = 3.25792512996573918826e+02
sb3 = 1.53672958608443695994e+03
sb4 = 3.19985821950859553908e+03
sb5 = 2.55305040643316442583e+03
sb6 = 4.74528541206955367215e+02
sb7 = -2.24409524465858183362e+01


def erf4(x):
    '''erf(x) for x in [1/.35,6]'''
    x0 = x
    x = math.fabs(x)
    s = one / (x * x)
    R = rb0 + s * \
        (rb1 + s * (rb2 + s * (rb3 + s * (rb4 + s * (rb5 + s * rb6)))))
    S = one + s * \
        (sb1 + s *
         (sb2 + s * (sb3 + s * (sb4 + s * (sb5 + s * (sb6 + s * sb7))))))
    z = math.ldexp(x0, 0)
    r = math.exp(-z * z - 0.5625) * math.exp((z - x) * (z + x) + R / S)
    if(z >= 0):
        return one - r / x
    else:
        return r / x - one


def erfc4(x):
    '''erfc(x) for x in [2.857142,6]'''
    return one - erf4(x)


def erf5(x):
    '''erf(x) for |x| in [6,inf)'''
    if x > 0:
        return one - tiny
    return tiny - one


def erfc5(x):
    '''erfc(x) for |x| in [6,inf)'''
    if (x > 0):
        return tiny * tiny
    return two - tiny

#
##inf = float('inf')
##nan = float('nan')
#
inf = float(9e999)


def Erf(x):
    '''return the error function of x'''
    f = float(x)
    if (f == inf):
        return 1.0
    elif (f == -inf):
        return -1.0
# elif (f is nan):
# return nan
    else:
        if (abs(x) < 0.84375):
            return erf1(x)
        elif (0.84375 <= abs(x) < 1.25):
            return erf2(x)
        elif (1.25 <= abs(x) < 2.857142):
            return erf3(x)
        elif (2.857142 <= abs(x) < 6):
            return erf4(x)
        elif (abs(x) >= 6):
            return erf5(x)


def Erfc(x):
    '''return the complementary of error function of x'''
    f = float(x)
    if (f == inf):
        return 0.0
    elif (f is -inf):
        return 2.0
# elif (f == nan):
# return nan
    else:
        if (abs(x) < 0.84375):
            return erfc1(x)
        elif (0.84375 <= abs(x) < 1.25):
            return erfc2(x)
        elif (1.25 <= abs(x) < 2.857142):
            return erfc3(x)
        elif (2.857142 <= abs(x) < 6):
            return erfc4(x)
        elif (abs(x) >= 6):
            return erfc5(x)

#------------------------------------------------------------------------------

# accuracy == success rate


def computeAccuracy(numTP, numTN, numFP, numFN):
    return (float(numTP + numTN) / float(numTP + numTN + numFP + numFN))

# precision == positive predictive value


def computePrecision(numTP, numFP):
    try:
        return (float(numTP) / float(numTP + numFP))
    except:
        return (-1)

# negative predictive value


def computeNegativePredictiveValue(numTN, numFN):
    try:
        return (float(numTN) / float(numFN + numTN))
    except:
        return (-1)

# sensitivity == recall


def computeSensitivity(numTP, numFN):
    try:
        return (float(numTP) / float(numTP + numFN))
    except:
        return (-1)

# specificity


def computeSpecificity(numTN, numFP):
    try:
        return (float(numTN) / float(numFP + numTN))
    except:
        return (-1)

# Matthews Correlation Coefficient


def computeMatthewsCorrCoeff(numTP, numTN, numFP, numFN):
    a = float(numTP * numTN) - float(numFP * numFN)
    b = math.sqrt(float(numTP + numFP) * float(numTP + numFN)
                  * float(numTN + numFP) * float(numTN + numFN))
    try:
        return ((a / b))
    except:
        return (-1)

#------------------------------------------------------------------------------


def computeMAD(x):

    # print " in computeMAD ... ", len(x)
    # print x

    numX = len(x)
    if (numX < 5):
        return (-1)

    medianVal = numpy.median(x)

    tmpV = numpy.zeros(numX)
    for iX in range(numX):
        tmpV[iX] = abs(x[iX] - medianVal)

    madVal = numpy.median(tmpV)

    return (madVal, medianVal)

#------------------------------------------------------------------------------


def computeIQR(x):

    numX = len(x)
    if (numX < 5):
        return (-1)

    tmpV = numpy.zeros(numX)
    for iX in range(numX):
        tmpV[iX] = x[iX]
    tmpV.sort()

    i25 = int(len(x) * 0.25 + 0.4999)
    i75 = int(len(x) * 0.75 + 0.4999)

    iqrVal = abs(tmpV[i25] - tmpV[i75])

    return (iqrVal, tmpV[i75])

#------------------------------------------------------------------------------


def computeIDR(x):

    numX = len(x)
    if (numX < 5):
        return (-1)

    tmpV = numpy.zeros(numX)
    for iX in range(numX):
        tmpV[iX] = x[iX]
    tmpV.sort()

    i10 = int(len(x) * 0.10 + 0.4999)
    i90 = int(len(x) * 0.90 + 0.4999)

    # print " in computeIDR : ", i10, i90, len(tmpV), tmpV[i10], tmpV[i90]
    idrVal = abs(tmpV[i10] - tmpV[i90])

    # return the inter-decile range as well as the 90th %ile value
    return (idrVal, tmpV[i90])

#------------------------------------------------------------------------------


def computeITR(x):

    numX = len(x)
    if (numX < 10):
        return (-1)

    tmpV = numpy.zeros(numX)
    for iX in range(numX):
        tmpV[iX] = x[iX]
    tmpV.sort()

    i05 = int(len(x) * 0.05 + 0.4999)
    i95 = int(len(x) * 0.95 + 0.4999)

    # print " in computeITR : ", i05, i95, len(tmpV), tmpV[i05], tmpV[i95]
    itrVal = abs(tmpV[i05] - tmpV[i95])

    # return the inter-twentile (?) range as well as the 95th %ile value
    return (itrVal, tmpV[i95])

#------------------------------------------------------------------------------
