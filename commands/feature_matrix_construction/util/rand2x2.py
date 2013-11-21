# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import miscClin
import miscMath

import math
import numpy
import random
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getSignif(n00, n01, n10, n11, MI, rho, numRand=100):

    nTot = n00 + n01 + n10 + n11
    print " counts : ", n00, n01, n10, n11, nTot

    miThresh = MI
    rhoThresh = abs(rho)

    px0 = float(n00 + n01) / float(nTot)
    py0 = float(n00 + n10) / float(nTot)
    print " marginal probabilities : ", px0, py0

    cardx = 2
    cardy = 2

    numRho = 0
    numMI = 0

    vHX = numpy.zeros(numRand)
    vHY = numpy.zeros(numRand)
    vMI = numpy.zeros(numRand)
    vP = numpy.zeros(numRand)

    v00 = numpy.zeros(numRand)
    v01 = numpy.zeros(numRand)
    v10 = numpy.zeros(numRand)
    v11 = numpy.zeros(numRand)

    # random testing ...
    print " beginning random simulation ... ", numRand
    for iRand in range(numRand):

        ## vx = [0] * nTot
        ## vy = [0] * nTot

        vx = numpy.zeros(nTot, dtype=numpy.int)
        vy = numpy.zeros(nTot, dtype=numpy.int)

        for ii in range(nTot):
            rx = random.random()
            ry = random.random()
            vx[ii] = int((rx < px0))
            vy[ii] = int((ry < py0))

            if (vx[ii]):
                if (vy[ii]):
                    v11[iRand] += 1
                else:
                    v10[iRand] += 1
            else:
                if (vy[ii]):
                    v01[iRand] += 1
                else:
                    v00[iRand] += 1

        (HofX, maxHX) = miscClin.calcEntropy(vx, cardx)
        (HofY, maxHY) = miscClin.calcEntropy(vy, cardy)
        HofXgivenY = miscClin.calcCondEntropy(vx, cardx, vy, cardy)
        xyMI = HofX - HofXgivenY

        vHX[iRand] = HofX
        vHY[iRand] = HofY
        vMI[iRand] = xyMI

        rhoP = miscMath.PearsonCorr(vx, vy)
        vP[iRand] = rhoP

        if (abs(rhoP) >= rhoThresh):
            numRho += 0.5
        if (xyMI >= miThresh):
            numMI += 1.0

    print ' 2x2 table entry stats : '
    print ' 00 : ', v00.mean(), math.sqrt(v00.var())
    print ' 01 : ', v01.mean(), math.sqrt(v01.var())
    print ' 10 : ', v10.mean(), math.sqrt(v10.var())
    print ' 11 : ', v11.mean(), math.sqrt(v11.var())

    p_MI = (float(numMI) / float(numRand))
    p_rho = (float(numRho) / float(numRand))

    print ' numRand=%d   numMI=%d   numRho=%d ' % (numRand, numMI, numRho)
    print ' MI  p-value = %f ' % p_MI
    print ' rho p-value = %f ' % p_rho
    print ' HX stats  : ', vHX.mean(), math.sqrt(vHX.var())
    print ' HY stats  : ', vHY.mean(), math.sqrt(vHY.var())
    print ' MI stats  : ', vMI.mean(), math.sqrt(vMI.var())
    print ' rho stats : ',  vP.mean(), math.sqrt(vP.var())

    return (p_MI, p_rho)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def permutationTest(ivec1, ivec2, MI, rho, numRand=100):

    miThresh = MI
    rhoThresh = abs(rho)

    nTot = len(ivec1)
    if (len(ivec2) != nTot):
        print " ERROR in permutationTest "
        sys.exit(-1)

    print " in permutation test ... ", nTot, MI, rho, numRand

    numRho = 0
    numMI = 0

    vHX = numpy.zeros(numRand)
    vHY = numpy.zeros(numRand)
    vMI = numpy.zeros(numRand)
    vP = numpy.zeros(numRand)
    vS = numpy.zeros(numRand)

    # random testing ...
    print " beginning random simulation ... ", numRand
    for iRand in range(numRand):

        ir = range(nTot)
        random.shuffle(ir)

        vx = numpy.zeros(nTot, dtype=numpy.int)
        vy = numpy.zeros(nTot, dtype=numpy.int)

        for ii in range(nTot):
            vx[ii] = ivec1[ii]
            vy[ii] = ivec2[ir[ii]]

        cardx = max(vx) + 1
        cardy = max(vy) + 1

        (HofX, maxHX) = miscClin.calcEntropy(vx, cardx)
        (HofY, maxHY) = miscClin.calcEntropy(vy, cardy)
        HofXgivenY = miscClin.calcCondEntropy(vx, cardx, vy, cardy)
        xyMI = HofX - HofXgivenY

        vHX[iRand] = HofX
        vHY[iRand] = HofY
        vMI[iRand] = xyMI

        rhoP = miscMath.PearsonCorr(vx, vy)
        vP[iRand] = rhoP

        if (abs(rhoP) >= rhoThresh):
            numRho += 0.5
        if (xyMI >= miThresh):
            numMI += 1.0

    p_MI = (float(numMI) / float(numRand))
    p_rho = (float(numRho) / float(numRand))

    print ' numRand=%d   numMI=%d   numRho=%d ' % (numRand, numMI, numRho)
    print ' MI  p-value = %f ' % p_MI
    print ' rho p-value = %f ' % p_rho
    print ' HX stats   : ', vHX.mean(), math.sqrt(vHX.var())
    print ' HY stats   : ', vHY.mean(), math.sqrt(vHY.var())
    print ' MI stats   : ', vMI.mean(), math.sqrt(vMI.var())
    print ' rhoP stats : ',  vP.mean(), math.sqrt(vP.var())

    return (p_MI, p_rho)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def permutationTest_prho(zvec1, zvec2, rho, numRand=100):

    rhoThresh = abs(rho)

    nTot = len(zvec1)
    if (len(zvec2) != nTot):
        print " ERROR in permutationTest "
        sys.exit(-1)

    print " in permutation test ... ", nTot, rho, numRand

    numRho = 0

    vP = numpy.zeros(numRand)
    vS = numpy.zeros(numRand)

    # random testing ...
    print " beginning random simulation ... ", numRand
    for iRand in range(numRand):

        ir = range(nTot)
        random.shuffle(ir)

        vx = numpy.zeros(nTot)
        vy = numpy.zeros(nTot)

        for ii in range(nTot):
            vx[ii] = zvec1[ii]
            vy[ii] = zvec2[ir[ii]]

        cardx = max(vx) + 1
        cardy = max(vy) + 1

        rhoP = miscMath.PearsonCorr(vx, vy)
        vP[iRand] = rhoP

        if (abs(rhoP) >= rhoThresh):
            numRho += 0.5

    p_rho = (float(numRho) / float(numRand))

    print ' numRand=%d   numRho=%d ' % (numRand, numRho)
    print ' rho p-value = %f ' % p_rho
    print ' rhoP stats : ',  vP.mean(), math.sqrt(vP.var())

    return (p_rho)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def t_statistic(num, rho):

    if (num < 10):
        return (-1.)

    rho2 = rho * rho
    try:
        t = abs(rho) * math.sqrt((num - 2) / (1. - rho2))
    except:
        tryRho = 0.9999
        tryRho2 = 0.9998
        try:
            t = abs(tryRho) * math.sqrt((num - 2) / (1. - tryRho2))
        except:
            print " ERROR in t_statistic ... ", num, rho
            sys.exit(-1)

    if (t > 1000):
        t = 1000.
    return (t)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

    n00 = 54
    n01 = 4
    n10 = 5
    n11 = 5
    nTot = n00 + n01 + n10 + n11
    print " counts : ", n00, n01, n10, n11, nTot

    miThresh = 0.108
    rhoThresh = 0.450

    px0 = 0.5  # px1 = 1. - px0
    py0 = 0.5  # py1 = 1. - py0

    px0 = float(n00 + n01) / float(nTot)
    py0 = float(n00 + n10) / float(nTot)
    print " marginal probabilities : ", px0, py0

    cardx = 2
    cardy = 2

    numRand = 100000
    ## numRand = 100
    numRho = 0
    numMI = 0

    vHX = numpy.zeros(numRand)
    vHY = numpy.zeros(numRand)
    vMI = numpy.zeros(numRand)
    vP = numpy.zeros(numRand)

    v00 = numpy.zeros(numRand)
    v01 = numpy.zeros(numRand)
    v10 = numpy.zeros(numRand)
    v11 = numpy.zeros(numRand)

    # random testing ...
    for iRand in range(numRand):

        ## vx = [0] * nTot
        ## vy = [0] * nTot

        vx = numpy.zeros(nTot, dtype=numpy.int)
        vy = numpy.zeros(nTot, dtype=numpy.int)

        for ii in range(nTot):
            rx = random.random()
            ry = random.random()
            vx[ii] = int((rx < px0))
            vy[ii] = int((ry < py0))

            if (vx[ii]):
                if (vy[ii]):
                    v11[iRand] += 1
                else:
                    v10[iRand] += 1
            else:
                if (vy[ii]):
                    v01[iRand] += 1
                else:
                    v00[iRand] += 1

        (HofX, maxHX) = miscClin.calcEntropy(vx, cardx)
        (HofY, maxHY) = miscClin.calcEntropy(vy, cardy)
        HofXgivenY = miscClin.calcCondEntropy(vx, cardx, vy, cardy)
        xyMI = HofX - HofXgivenY

        vHX[iRand] = HofX
        vHY[iRand] = HofY
        vMI[iRand] = xyMI

        rhoP = miscMath.PearsonCorr(vx, vy)
        vP[iRand] = rhoP

        if (abs(rhoP) >= rhoThresh):
            numRho += 0.5
        if (xyMI >= miThresh):
            numMI += 1.0

    print " 2x2 table entry stats : "
    print ' 00 : ', v00.mean(), math.sqrt(v00.var())
    print ' 01 : ', v01.mean(), math.sqrt(v01.var())
    print ' 10 : ', v10.mean(), math.sqrt(v10.var())
    print ' 11 : ', v11.mean(), math.sqrt(v11.var())

    p_MI = (float(numMI) / float(numRand))
    p_rho = (float(numRho) / float(numRand))

    print ' numRand=%d   numMI=%d   numRho=%d ' % (numRand, numMI, numRho)
    print ' MI  p-value = %f ' % p_MI
    print ' rho p-value = %f ' % p_rho
    print ' HX stats  : ', vHX.mean(), math.sqrt(vHX.var())
    print ' HY stats  : ', vHY.mean(), math.sqrt(vHY.var())
    print ' MI stats  : ', vMI.mean(), math.sqrt(vMI.var())
    print ' rho stats : ',  vP.mean(), math.sqrt(vP.var())

    # fixed testing ...
    vx = numpy.zeros(nTot, dtype=numpy.int)
    vy = numpy.zeros(nTot, dtype=numpy.int)

    ii = 0
    for jj in range(n00):
        vx[ii] = 0
        vy[ii] = 0
        ii += 1

    for jj in range(n01):
        vx[ii] = 0
        vy[ii] = 1
        ii += 1

    for jj in range(n10):
        vx[ii] = 1
        vy[ii] = 0
        ii += 1

    for jj in range(n11):
        vx[ii] = 1
        vy[ii] = 1
        ii += 1

    (HofX, maxHX) = miscClin.calcEntropy(vx, cardx)
    (HofY, maxHY) = miscClin.calcEntropy(vy, cardy)
    HofXgivenY = miscClin.calcCondEntropy(vx, cardx, vy, cardy)
    xyMI = HofX - HofXgivenY

    rhoP = miscMath.PearsonCorr(vx, vy)

    print " fixed : "
    print " H(X)=%6.3f  H(Y)=%6.3f  MI(X;Y)=%6.3f  rhoP=%6.3f " % (HofX, HofY, xyMI, rhoP)
    print " MI ratios : %6.3f  %6.3f " % (xyMI / HofX, xyMI / HofY)


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
