#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh

if [[ "$PYTHONPATH" != *"gidget"* ]]; then
    echo " "
    echo " your PYTHONPATH should include paths to gidget/commands/... directories "
    echo " "
    exit 99
fi

## this script should be called with the following parameters:
##      date, eg '29jan13'
##      tumor, eg: 'brca'
##      tsvExtension, eg: 'TP.tsv'

WRONGARGS=1
if [[ $# != 3 ]] && [[ $# != 4 ]]
    then
        echo " "
        echo " Usage   : `basename $0` <curDate> <tumorType> <tsvExtension> [config-file] "
        echo " Example : `basename $0` 28oct13  brca  TP.tsv "
        echo " "
        echo " NOTE that the config-file is optional and by default will be obtained from "
        echo " either <tumorType>/aux/PairProcess_config.csv or from the root shscript directory. "
        echo " If you want to use a different config-file, then give the complete path-name as a command-line option. "
        echo " "
        exit $WRONGARGS
fi

curDate=$1
tumor=$2
tsvExt=$3
if (( $# == 4 ))
    then
        ## cFile=$TCGAFMP_DATA_DIR/$tumor/aux/$4
        cFile=$4
    else
	if [ -f $TCGAFMP_DATA_DIR/$tumor/aux/PairProcess_config.csv ]
	    then
	        cFile=$TCGAFMP_DATA_DIR/$tumor/aux/PairProcess_config.csv
	    else
	        cFile=$TCGAFMP_ROOT_DIR/shscript/PairProcess_config.csv
	fi
fi

echo " "
echo " using config file " $cFile
echo " "

FNF=2
tsvFile=$TCGAFMP_DATA_DIR/$tumor/$curDate/$tumor.seq.$curDate.$tsvExt
echo $tsvFile
if [ ! -f $tsvFile ]
    then
        echo " "
        echo " ERROR file not found !!! "
        echo " $tsvFile "
        echo " "
        exit $FNF
fi

echo " "

string1="$TCGAFMP_ROOT_DIR/main/run_pwRK3.py --pvalue "
string2=" --byType --type1 "
string3=" --type2 "
string4=" --forRE --tsvFile "

h=${tsvFile/.tsv/}
echo " h = " $h
rm -fr $h.????.????.pwpv
rm -fr $h.????.????.pwpv.forRE

echo " "
echo " "

for p in `cat $cFile`
    do

        IFS=',' read -a tokens <<< "${p}"
        dtype1=${tokens[0]}
        dtype2=${tokens[1]}
        stringency=${tokens[2]}

        echo " "
        echo " "
        echo " ********************************************************************** "
        date
        echo "Processing: "${dtype1},${dtype2},$stringency
        cstring=$string1$stringency$string2${dtype1}$string3${dtype2}$string4$tsvFile
        echo $cstring
        eval $cstring

    done

echo " "
echo " "

echo " ***************************** "
echo " Number of output pair files : "
ls -alt $h.????.????.pwpv | wc -l
ls -alt $h.????.????.pwpv.forRE | wc -l
echo " "
echo " ***************************** "

cd $TCGAFMP_DATA_DIR/$tumor/$curDate/
echo " now working in: " `pwd`

tsvFile=$tumor.seq.$curDate.$tsvExt
f=${tsvFile/.tsv/}
echo " f = " $f
echo " "
echo " "
date
echo " Now for the post-processing "
echo " "
date
echo " handling $f "

rm -fr $TCGAFMP_LOCAL_SCRATCH/$f.??

rm -fr $f.pwpv.forRE
rm -fr $f.pwpv

cat $f.????.????.pwpv.forRE >& $TCGAFMP_LOCAL_SCRATCH/$f.1a
wc -l $TCGAFMP_LOCAL_SCRATCH/$f.1a
sort -grk 5 --temporary-directory=$TCGAFMP_LOCAL_SCRATCH $TCGAFMP_LOCAL_SCRATCH/$f.1a | uniq >& $TCGAFMP_LOCAL_SCRATCH/$f.1b
mv $TCGAFMP_LOCAL_SCRATCH/$f.1b $f.pwpv.forRE
wc -l $f.pwpv.forRE

echo " "
date
echo " "

cat $f.????.????.pwpv >& $TCGAFMP_LOCAL_SCRATCH/$f.2a
wc -l $TCGAFMP_LOCAL_SCRATCH/$f.2a
sort -grk 5 --temporary-directory=$TCGAFMP_LOCAL_SCRATCH $TCGAFMP_LOCAL_SCRATCH/$f.2a | uniq >& $TCGAFMP_LOCAL_SCRATCH/$f.2b
mv $TCGAFMP_LOCAL_SCRATCH/$f.2b $f.pwpv
wc -l $f.pwpv

echo " "
date
echo " "


