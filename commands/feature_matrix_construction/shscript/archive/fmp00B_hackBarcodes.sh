#!/bin/bash

## HACK ... there are 4 SKCM samples that were incorrectly identified
## as primaries and need to be reclassified as metastases

inFile=$1

## removing all of this because it turns out that we are just going
## to blacklist these samples!  (SMR 07feb14)

## if [ -f $inFile ]
##     then
##         echo " editing barcodes in " $inFile
##         rm -fr xx yy
##         cp $inFile $inFile.bkp
##         cp $inFile xx
##         sed -e '1,$s/A4Z6-01A/A4Z6-06A/g' xx | \
##             sed -e '1,$s/A1X3-01A/A1X3-06A/g' | \
##             sed -e '1,$s/A2OG-01A/A2OG-06A/g' | \
##             sed -e '1,$s/A2OH-01A/A2OH-06A/g' | \
##             sed -e '1,$s/A4Z6-01/A4Z6-06/g' | \
##             sed -e '1,$s/A1X3-01/A1X3-06/g' | \
##             sed -e '1,$s/A2OG-01/A2OG-06/g' | \
##             sed -e '1,$s/A2OH-01/A2OH-06/g' >& yy
##         cp yy $inFile
##     else
##         echo " FILE NOT FOUND " $inFile
##     fi
