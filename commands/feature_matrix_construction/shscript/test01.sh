#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


curDate=$1
snapshotName=$2

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

if [ -z "$snapshotName" ]
    then
	echo " using default dcc-snapshot "
    else
	echo " using this specific snapshot: " $snapshotName
fi

args=("$@")
for ((i=2; i<  $#; i++)) 
    do
        echo "argument #$((i+1)): ${args[$i]}"
    done

echo " "
echo " last argument : " ${args[($#)-1]}
echo " "

