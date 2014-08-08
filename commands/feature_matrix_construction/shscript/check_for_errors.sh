#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/gidget_util.sh


## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'

WRONGARGS=1
if [ $# != 1 ]
    then
        echo " Usage   : `basename $0` <curDate> "
        echo " Example : `basename $0` 28oct13 "
        exit $WRONGARGS
fi

curDate=$1

echo " "
echo " "
echo " ***********"
echo " *" $curDate "* "
echo " ***********"

cd $TCGAFMP_DATA_DIR
echo " "
pwd
echo " "

echo " "
echo " checking parse (xml and Firehose) log files ... "
grep -i "error" */$curDate/parse*.$curDate.log | grep -v "ERROR in path\.list" | sort | uniq

echo " "
echo " checking cleanClin log files ... "
grep -i "error" */$curDate/cleanClin.$curDate.log | grep -v "returning NA" | sort | uniq

echo " "
echo " checking level3 log files ... "
grep -i "error" */$curDate/level3.*.$curDate.log | grep -v " nothing returned from SDRFs " | sort | uniq

echo " "
echo " data contents in level3 data files ..."
grep -i "finished in writeTSV_dataMatrix" */level3.*.$curDate.log | sort | uniq

echo " "
echo " checking filterSamp log files ... "
grep -i "error" */$curDate/filterSamp*.$curDate.log | sort | uniq

echo " "
echo " checking annotate log files ... "
grep -i "error" */$curDate/annotate.*.$curDate.log | sort | uniq

echo " "
echo " checking highVar log files ... "
grep -i "error" */$curDate/highVar.*.$curDate.log | grep -v " QQ " | sort | uniq

echo " "
echo " checking merge log files ... "
grep -i "error" */$curDate/*.newMerge*.$curDate.log | sort | uniq

echo " "
echo " checking j log files ... "
grep -i "error" */$curDate/*.$curDate.j.log | sort | uniq

echo " "
echo " checking jc log files ... "
grep -i "error" */$curDate/*.$curDate.jc.log | sort | uniq

echo " "
echo " checking jct log files ... "
grep -i "error" */$curDate/*.$curDate.jct.log | sort | uniq

echo " "
echo " checking jctm log files ... "
grep -i "error" */$curDate/*.$curDate.jctm.log | sort | uniq

echo " "
echo " checking jctmg log files ... "
grep -i "error" */$curDate/*.$curDate.jctmg.log | sort | uniq

echo " "
echo " checking split log files ... "
grep -i "error" */$curDate/*.$curDate.*split.log | sort | uniq

echo " "
echo " checking merge-NT log files ... "
grep -i "error" */$curDate/*.???.$curDate.*.NT.log | sort | uniq

