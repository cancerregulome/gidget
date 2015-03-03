#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## now we assume that in the input specified directory, we have
## one enormous file called post_proc_all.tsv and then all of 
## the feature type "pair" files, eg
##	post_proc_all.NMETH.NRPPA.tmp
##	post_proc_all.NCNVR.NGEXP.tmp
## etc ...

d=$1

echo " "
echo " "
echo " processing temp files in $1 "

## uName=`whoami`
## tDir='/tmp/'$uName'/pw_scratch'
## if [ ! -d $tDir ]
##     then
##         mkdir -p $tDir
##     fi
tDir=$TCGAFMP_LOCAL_SCRATCH
echo " using temp scratch directory " $tDir

date

echo " sorting the individual files ... "
for t in $d/post_proc_all.*.*.tmp
   do
	echo $t
        sort -grk 5,5 -k 1,2 --temporary-directory=$tDir $t | uniq >& $t.sort
   done

date

echo " concatenating at most 1 million pairs of each type ... "
rm -fr $d/post_proc_all.short
echo " " > $d/post_proc_all.short
for t in $d/post_proc_all.*.*.tmp.sort
    do
        echo $t
	head -1000000 $t >> $d/post_proc_all.short
    done

date

echo " now sorting the short concatenation ... "
rm -fr $d/post_proc_all.short.sort
sort -grk 5,5 -k1,2 --temporary-directory=$tDir $d/post_proc_all.short | uniq >& $d/post_proc_all.short.sort

date

echo " deleting .tmp and .tmp.sort and .pw files "
rm -fr $d/post_proc_all.*.*.tmp.sort
rm -fr $d/post_proc_all.*.*.tmp
## rm -fr $d/*.pw 
## rm -fr $d/runList.txt

echo " and last but not least, removing unmapped features ... "
python $TCGAFMP_ROOT_DIR/main/filterPWPV.py $d/post_proc_all.short.sort 

grep -iv "pathway" $d/post_proc_all.short.sort.mapped | grep -v "	nan	" >& $d/post_proc_all.short.sort.mapped.noPathway

date

echo " "
echo " "

