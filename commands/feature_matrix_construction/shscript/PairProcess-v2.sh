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
if [[ $# != 5 ]] && [[ $# != 6 ]]
    then
        echo " "
        echo " Usage   : `basename $0` <curDate> <tumorType> <mRNAtype> <tsvExtension> <REflag=RE/noRE> [config-file] "
        echo " Example : `basename $0` 28oct13  brca  seq  TP.tsv "
        echo " "
        echo " NOTES : "
        echo "     mRNAtype should be either seq or array "
        echo "     tsvExtension should be something like tsv or TP.tsv or TM.tsv "
        echo "     REflag should be either RE or noRE "
        echo "     config-file is optional and by default will be obtained from "
        echo "         either <tumorType>/aux/PairProcess_config.csv or from the root "
        echo "         shscript directory.  If you want to use a different config-file, "
        echo "         then give the complete path-name as a command-line option. "
        echo " "
        exit $WRONGARGS
fi

curDate=$1
tumor=$2
mRNAtype=$3
tsvExt=$4
REflag=$5
if (( $# == 6 ))
    then
        cFile=$6
    else
        if [ -f $TCGAFMP_DATA_DIR/$tumor/aux/PairProcess_config.csv ]
            then
                cFile=$TCGAFMP_DATA_DIR/$tumor/aux/PairProcess_config.csv
            else
                cFile=$TCGAFMP_ROOT_DIR/shscript/PairProcess_config.csv
        fi
fi

# tweak the mRNAtype
echo $mRNAtype
if [[ $mRNAtype == "array" ]]
    then
        mRNAtype="ary"
    else
        mRNAtype="seq"
    fi
echo $mRNAtype

# check the REflag
echo $REflag
if [[ $REflag != "noRE" ]]
    then
        REflag="RE"
    fi
echo $REflag

echo " "
echo " RUNNING with " $curDate $tumor $mRNAtype $tsvExt $REflag $cFile
echo " "

FNF=2
tsvFile=$TCGAFMP_DATA_DIR/$tumor/$curDate/$tumor.$mRNAtype.$curDate.$tsvExt
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

string1="$TCGAFMP_ROOT_DIR/main/run-pairwise-v2.py --pvalue "
string2=" --byType --type1 "
string3=" --type2 "
if [[ $REflag == "noRE" ]]
    then
        echo "     NOTE: pairwise will be invoked WITHOUT RE option "
        string4=" --tsvFile "
    else
        echo "     NOTE: pairwise will be invoked WITH RE option "
        string4=" --forRE --tsvFile "
    fi

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
curDir=`pwd`

tsvFile=$tumor.$mRNAtype.$curDate.$tsvExt
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

if [[ $REflag == "RE" ]]
    then
        print " echo doing the RE processing step "
        rm -fr $f.pwpv.forRE
        cat $f.????.????.pwpv.forRE >& $TCGAFMP_LOCAL_SCRATCH/$f.1a
        wc -l $TCGAFMP_LOCAL_SCRATCH/$f.1a
        sort -grk 5 --temporary-directory=$TCGAFMP_LOCAL_SCRATCH \
            $TCGAFMP_LOCAL_SCRATCH/$f.1a | uniq >& $TCGAFMP_LOCAL_SCRATCH/$f.1b
        mv $TCGAFMP_LOCAL_SCRATCH/$f.1b $f.pwpv.forRE
        wc -l $f.pwpv.forRE
        rm -fr $TCGAFMP_LOCAL_SCRATCH/$f.1a
    else
        print " echo SKIPPING the RE processing step "
    fi

echo " "
date
echo " "

rm -fr $f.pwpv
cat $f.????.????.pwpv >& $TCGAFMP_LOCAL_SCRATCH/$f.2a
wc -l $TCGAFMP_LOCAL_SCRATCH/$f.2a
## sort -grk 5 --temporary-directory=$TCGAFMP_LOCAL_SCRATCH $TCGAFMP_LOCAL_SCRATCH/$f.2a | uniq >& $TCGAFMP_LOCAL_SCRATCH/$f.2b
## mv $TCGAFMP_LOCAL_SCRATCH/$f.2b $f.pwpv
mv $TCGAFMP_LOCAL_SCRATCH/$f.2a $f.pwpv
wc -l $f.pwpv
rm -fr $TCGAFMP_LOCAL_SCRATCH/$f.2?

echo " "
date
echo " "


if [[ $REflag == "RE" ]]
    then

        echo " creating the RE META file "

        ## now we are going to create a META file if one does not already exist ...
        cd $TCGAFMP_DATA_DIR/$tumor/$curDate
        if [ ! -d "META" ]
            then
                mkdir META
                chmod g+w META
        fi
        cd META
        rm -fr t1?
        cp $TCGAFMP_ROOT_DIR/config/META.sample t1
        
        tsvFile=$TCGAFMP_DATA_DIR/$tumor/$curDate/$tumor.$mRNAtype.$curDate.$tsvExt
        sed -e 's,FULL_TSV_PATH_NAME_HERE,'"$tsvFile"',g' t1 >& t2
        
        pwName=${tsvFile/.tsv/.pwpv.forRE}
        sed -e 's,FULL_PATH_TO_PWPV_FOR_RE_FILE_HERE,'"$pwName"',g' t2 >& t3
        
        ##dsName=$tumor.$curDate.$tsvExt
        justExt=${tsvExt/.tsv/}
        if [ "$justExt"="tsv" ]
            then
                dsName=$tumor"_"$curDate
            else
                dsName=$tumor"_"$curDate"_"$justExt
        fi
        sed -e 's,DATA_SET_LABEL_HERE,'"$dsName"',g' t3 >& t4
        
        utName=`echo $tumor | tr [:lower:] [:upper:]`
        sed -e 's,TUMOR_TYPE_HERE,'"$utName"',g' t4 >& t5
        
        fsName=${tsvFile/.tsv/.featScoresV2.txt}
        sed -e 's,PATH_TO_SCORES_FILE_HERE,'"$fsName"',g' t5 >& t6
        
        mv t6 META.$tumor.$curDate.$tsvExt
        rm -fr t?

    fi

cd $curDir

