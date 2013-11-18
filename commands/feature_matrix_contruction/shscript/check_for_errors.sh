#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

## this script should be called with a current date string such as 14jan13 (ddmmmyy)
curDate=$1

if [ -z "$curDate" ]
    then
        echo " this script must be called with a date string of some kind, eg 28feb13 "
        exit
fi

echo " "
echo " "
echo " ***********"
echo " *" $curDate "* "
echo " ***********"

cd /titan/cancerregulome14/TCGAfmp_outputs/
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

