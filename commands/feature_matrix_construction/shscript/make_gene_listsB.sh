#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


# TODO: additional parameter checking for below
curDate=$1
curTumor=$2

cd $TCGAFMP_DATA_DIR
cd $curTumor
cd $curDate

## this script outputs the list of gene symbols 
## from: stad.gexp.seq.tmpData2.tsv
## to:   stad.gexp.seq.list

for f in *.gexp.???.tmpData2.tsv
    do
	rm -fr t?
	g=${f/tmpData2.tsv/list}
        echo " getting list of gene symbols from " $f
	grep "^N:GEXP:" $f | cut -f1 >& t1
	sed -e '1,$s/:/	/g' t1 | cut -f3 | sort >& t2
	wc -l t2
	rm -fr $g
	mv t2 $g
	rm -fr t?
    done

