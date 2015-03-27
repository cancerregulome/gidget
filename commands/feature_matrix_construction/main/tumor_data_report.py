# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from env import gidgetConfigVars

import os
import path
import sys
import time

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def stripArchive ( fName ):
    ii = len(fName) - 1
    while ( fName[ii] != '/' ): ii -= 1
    return ( fName[ii+1:] )

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def dig ( aDir, threshT ):

    if ( aDir.find("Level_") > 0 ): return ( ) 
    if ( aDir.find("mage-tab") > 0 ): return ( ) 
    ## print " digging into ", aDir

    d1 = path.path ( aDir )
    numDir = len(d1.dirs())
    numFiles = len(d1.files())
    
    ## print d1
    ## print numDir, numFiles

    newFile = ""
    maxT = -1
    ## print " looping over files ... "
    for aFile in d1.files():
        if ( aFile.endswith(".tar.gz") ):
            ## print aFile
            tFile = os.path.getmtime ( aFile )
            if ( tFile > maxT ): 
                maxT = tFile
                ## print "     new maxT ", stripArchive(aFile), time.ctime(maxT)
                newFile = aFile
    if ( newFile != "" ): 
        if ( maxT > threshT ):
            print "     ", time.ctime(maxT),  stripArchive(newFile)

    for nextDir in d1.dirs():
        dig ( nextDir, threshT )


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# MAIN PROGRAM STARTS HERE
#

if __name__ == "__main__":

    if (1):
        if (len(sys.argv)!=2 and len(sys.argv)!=3):
            print " Usage: %s <tumorType> [30] "
            print "        the optional second argument is how far back to look in days "
            print " ERROR -- bad command line arguments "
            sys.exit(-1)
        else:

            zCancer = sys.argv[1].lower()
            if ( len(sys.argv) == 3 ):
                nDays = int(sys.argv[2])
            else:
                nDays = 30

    if (1):
        print " "

        topDir = gidgetConfigVars['TCGAFMP_DCC_REPOSITORIES'] + \
            "/dcc-mirror/public/tumor/" + zCancer 

        nowT = time.time()
        threshT = nowT - (nDays*24*60*60)

        print " Archives downloaded within the last %d days for %s " % ( nDays, zCancer )
        dig ( topDir, threshT )

        sys.exit(-1)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
