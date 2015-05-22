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

## although for the pancan analysis, we only care about the NGEXP.NGEXP 

d=$1

echo " "
echo " "
echo " processing temp files in $1 "

date

echo " sorting the individual files ... "
for t in $d/post_proc_all.NGEXP.NGEXP.tmp
   do
	echo $t
	sort -grk 5 --temporary-directory=/local/sreynold/scratch/ $t >& $t.sort
	head -1000000 $t.sort >& $t.sort.top1M
   done

rm -fr $d/post_proc_all.*.*.tmp
## rm -fr $d/*.pw 
## rm -fr $d/runList.txt

date

echo " "
echo " "

