#!/bin/bash

echo " "
date
echo " "

curDate=$1

cd /titan/cancerregulome14/TCGAfmp_outputs/

for f in */$curDate/*.gexp.???.tmpData2.tsv
    do
	echo " "
	rm -fr t?
	g=${f/tmpData2.tsv/list}
	echo $f
	echo $g
	grep "^N:GEXP:" $f | cut -f1 >& t1
	sed -e '1,$s/:/	/g' t1 | cut -f3 | sort >& t2
	wc -l t2
	rm -fr $g
	mv t2 $g
	rm -fr t?
    done
