#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


f=$1

echo " "
echo " "
echo " handling $1 "

rm -fr $f.proc
echo " " > $f.proc

date

rm -fr $f.info
grep "^##" $f >& $f.info

rm -fr $f.?????*tmp

## first the 15 self comparisons ...
## possible types are now:
##	B: CLIN CNVR GNAB SAMP
##	C: CLIN CNVR SAMP
##	N: CLIN CNVR GEXP GNAB METH MIRN RPPA SAMP

echo " starting self-comparisons "
date

grep "^B:CLIN:" $f | grep "	B:CLIN:" >& $f.BCLIN.tmp &
grep "^B:CNVR:" $f | grep "	B:CNVR:" >& $f.BCNVR.tmp 
grep "^B:GNAB:" $f | grep "	B:GNAB:" >& $f.BGNAB.tmp &
grep "^B:SAMP:" $f | grep "	B:SAMP:" >& $f.BSAMP.tmp 

grep "^C:CLIN:" $f | grep "	C:CLIN:" >& $f.CCLIN.tmp &
grep "^C:CNVR:" $f | grep "	C:CNVR:" >& $f.CCNVR.tmp 
grep "^C:SAMP:" $f | grep "	C:SAMP:" >& $f.CSAMP.tmp &

grep "^N:CLIN:" $f | grep "	N:CLIN:" >& $f.NCLIN.tmp
grep "^N:CNVR:" $f | grep "	N:CNVR:" >& $f.NCNVR.tmp &
grep "^N:GEXP:" $f | grep "	N:GEXP:" >& $f.NGEXP.tmp 
grep "^N:GNAB:" $f | grep "	N:GNAB:" >& $f.NGNAB.tmp &
grep "^N:METH:" $f | grep "	N:METH:" >& $f.NMETH.tmp 
grep "^N:MIRN:" $f | grep "	N:MIRN:" >& $f.NMIRN.tmp &
grep "^N:RPPA:" $f | grep "	N:RPPA:" >& $f.NRPPA.tmp 
grep "^N:SAMP:" $f | grep "	N:SAMP:" >& $f.NSAMP.tmp &

## next it's B:CLIN x the other 14 ...

echo " B:CLIN vs others ... "
date

grep "B:CLIN:" $f | grep "B:CNVR:" >& $f.BCLIN.BCNVR.tmp 
grep "B:CLIN:" $f | grep "B:GNAB:" >& $f.BCLIN.BGNAB.tmp &
grep "B:CLIN:" $f | grep "B:SAMP:" >& $f.BCLIN.BSAMP.tmp 
grep "B:CLIN:" $f | grep "C:CLIN:" >& $f.BCLIN.CCLIN.tmp &
grep "B:CLIN:" $f | grep "C:CNVR:" >& $f.BCLIN.CCNVR.tmp 
grep "B:CLIN:" $f | grep "C:SAMP:" >& $f.BCLIN.CSAMP.tmp &
grep "B:CLIN:" $f | grep "N:CLIN:" >& $f.BCLIN.NCLIN.tmp 
grep "B:CLIN:" $f | grep "N:CNVR:" >& $f.BCLIN.NCNVR.tmp &
grep "B:CLIN:" $f | grep "N:GEXP:" >& $f.BCLIN.NGEXP.tmp 
grep "B:CLIN:" $f | grep "N:GNAB:" >& $f.BCLIN.NGNAB.tmp &
grep "B:CLIN:" $f | grep "N:METH:" >& $f.BCLIN.NMETH.tmp 
grep "B:CLIN:" $f | grep "N:MIRN:" >& $f.BCLIN.NMIRN.tmp &
grep "B:CLIN:" $f | grep "N:RPPA:" >& $f.BCLIN.NRPPA.tmp 
grep "B:CLIN:" $f | grep "N:SAMP:" >& $f.BCLIN.NSAMP.tmp &

## next it's B:CNVR x the other 13 ...

echo " B:CNVR vs others ... "
date

grep "B:CNVR:" $f | grep "B:GNAB:" >& $f.BCNVR.BGNAB.tmp 
grep "B:CNVR:" $f | grep "B:SAMP:" >& $f.BCNVR.BSAMP.tmp &
grep "B:CNVR:" $f | grep "C:CLIN:" >& $f.BCNVR.CCLIN.tmp 
grep "B:CNVR:" $f | grep "C:CNVR:" >& $f.BCNVR.CCNVR.tmp &
grep "B:CNVR:" $f | grep "C:SAMP:" >& $f.BCNVR.CSAMP.tmp 
grep "B:CNVR:" $f | grep "N:CLIN:" >& $f.BCNVR.NCLIN.tmp &
grep "B:CNVR:" $f | grep "N:CNVR:" >& $f.BCNVR.NCNVR.tmp 
grep "B:CNVR:" $f | grep "N:GEXP:" >& $f.BCNVR.NGEXP.tmp &
grep "B:CNVR:" $f | grep "N:GNAB:" >& $f.BCNVR.NGNAB.tmp 
grep "B:CNVR:" $f | grep "N:METH:" >& $f.BCNVR.NMETH.tmp &
grep "B:CNVR:" $f | grep "N:MIRN:" >& $f.BCNVR.NMIRN.tmp 
grep "B:CNVR:" $f | grep "N:RPPA:" >& $f.BCNVR.NRPPA.tmp &
grep "B:CNVR:" $f | grep "N:SAMP:" >& $f.BCNVR.NSAMP.tmp

## next it's B:GNAB x the other 12 ...

echo " B:GNAB vs others ... "
date

grep "B:GNAB:" $f | grep "B:SAMP:" >& $f.BGNAB.BSAMP.tmp &
grep "B:GNAB:" $f | grep "C:CLIN:" >& $f.BGNAB.CCLIN.tmp 
grep "B:GNAB:" $f | grep "C:CNVR:" >& $f.BGNAB.CCNVR.tmp &
grep "B:GNAB:" $f | grep "C:SAMP:" >& $f.BGNAB.CSAMP.tmp 
grep "B:GNAB:" $f | grep "N:CLIN:" >& $f.BGNAB.NCLIN.tmp &
grep "B:GNAB:" $f | grep "N:CNVR:" >& $f.BGNAB.NCNVR.tmp 
grep "B:GNAB:" $f | grep "N:GEXP:" >& $f.BGNAB.NGEXP.tmp &
grep "B:GNAB:" $f | grep "N:GNAB:" >& $f.BGNAB.NGNAB.tmp 
grep "B:GNAB:" $f | grep "N:METH:" >& $f.BGNAB.NMETH.tmp &
grep "B:GNAB:" $f | grep "N:MIRN:" >& $f.BGNAB.NMIRN.tmp 
grep "B:GNAB:" $f | grep "N:RPPA:" >& $f.BGNAB.NRPPA.tmp &
grep "B:GNAB:" $f | grep "N:SAMP:" >& $f.BGNAB.NSAMP.tmp

## next it's B:SAMP x the other 11 ...

echo " B:SAMP vs others ... "
date

grep "B:SAMP:" $f | grep "C:CLIN:" >& $f.BSAMP.CCLIN.tmp &
grep "B:SAMP:" $f | grep "C:CNVR:" >& $f.BSAMP.CCNVR.tmp 
grep "B:SAMP:" $f | grep "C:SAMP:" >& $f.BSAMP.CSAMP.tmp &
grep "B:SAMP:" $f | grep "N:CLIN:" >& $f.BSAMP.NCLIN.tmp 
grep "B:SAMP:" $f | grep "N:CNVR:" >& $f.BSAMP.NCNVR.tmp &
grep "B:SAMP:" $f | grep "N:GEXP:" >& $f.BSAMP.NGEXP.tmp 
grep "B:SAMP:" $f | grep "N:GNAB:" >& $f.BSAMP.NGNAB.tmp &
grep "B:SAMP:" $f | grep "N:METH:" >& $f.BSAMP.NMETH.tmp 
grep "B:SAMP:" $f | grep "N:MIRN:" >& $f.BSAMP.NMIRN.tmp &
grep "B:SAMP:" $f | grep "N:RPPA:" >& $f.BSAMP.NRPPA.tmp 
grep "B:SAMP:" $f | grep "N:SAMP:" >& $f.BSAMP.NSAMP.tmp &

## next it's C:CLIN x the other 10 ...

echo " C:CLIN vs others ... "
date

grep "C:CLIN:" $f | grep "C:CNVR:" >& $f.CCLIN.CCNVR.tmp 
grep "C:CLIN:" $f | grep "C:SAMP:" >& $f.CCLIN.CSAMP.tmp &
grep "C:CLIN:" $f | grep "N:CLIN:" >& $f.CCLIN.NCLIN.tmp 
grep "C:CLIN:" $f | grep "N:CNVR:" >& $f.CCLIN.NCNVR.tmp &
grep "C:CLIN:" $f | grep "N:GEXP:" >& $f.CCLIN.NGEXP.tmp 
grep "C:CLIN:" $f | grep "N:GNAB:" >& $f.CCLIN.NGNAB.tmp &
grep "C:CLIN:" $f | grep "N:METH:" >& $f.CCLIN.NMETH.tmp 
grep "C:CLIN:" $f | grep "N:MIRN:" >& $f.CCLIN.NMIRN.tmp &
grep "C:CLIN:" $f | grep "N:RPPA:" >& $f.CCLIN.NRPPA.tmp 
grep "C:CLIN:" $f | grep "N:SAMP:" >& $f.CCLIN.NSAMP.tmp &

## next it's C:CNVR x the other 9 ...

echo " C:CNVR vs others ... "
date

grep "C:CNVR:" $f | grep "C:SAMP:" >& $f.CCNVR.CSAMP.tmp 
grep "C:CNVR:" $f | grep "N:CLIN:" >& $f.CCNVR.NCLIN.tmp &
grep "C:CNVR:" $f | grep "N:CNVR:" >& $f.CCNVR.NCNVR.tmp 
grep "C:CNVR:" $f | grep "N:GEXP:" >& $f.CCNVR.NGEXP.tmp &
grep "C:CNVR:" $f | grep "N:GNAB:" >& $f.CCNVR.NGNAB.tmp 
grep "C:CNVR:" $f | grep "N:METH:" >& $f.CCNVR.NMETH.tmp &
grep "C:CNVR:" $f | grep "N:MIRN:" >& $f.CCNVR.NMIRN.tmp 
grep "C:CNVR:" $f | grep "N:RPPA:" >& $f.CCNVR.NRPPA.tmp &
grep "C:CNVR:" $f | grep "N:SAMP:" >& $f.CCNVR.NSAMP.tmp

## next it's C:SAMP x the other 8 ...

echo " C:SAMP vs others ... "
date

grep "C:SAMP:" $f | grep "N:CLIN:" >& $f.CSAMP.NCLIN.tmp &
grep "C:SAMP:" $f | grep "N:CNVR:" >& $f.CSAMP.NCNVR.tmp 
grep "C:SAMP:" $f | grep "N:GEXP:" >& $f.CSAMP.NGEXP.tmp &
grep "C:SAMP:" $f | grep "N:GNAB:" >& $f.CSAMP.NGNAB.tmp 
grep "C:SAMP:" $f | grep "N:METH:" >& $f.CSAMP.NMETH.tmp &
grep "C:SAMP:" $f | grep "N:MIRN:" >& $f.CSAMP.NMIRN.tmp 
grep "C:SAMP:" $f | grep "N:RPPA:" >& $f.CSAMP.NRPPA.tmp &
grep "C:SAMP:" $f | grep "N:SAMP:" >& $f.CSAMP.NSAMP.tmp

## next it's N:CLIN x the other 7 ...

echo " N:CLIN vs others ... "
date

grep "N:CLIN:" $f | grep "N:CNVR:" >& $f.NCLIN.NCNVR.tmp &
grep "N:CLIN:" $f | grep "N:GEXP:" >& $f.NCLIN.NGEXP.tmp 
grep "N:CLIN:" $f | grep "N:GNAB:" >& $f.NCLIN.NGNAB.tmp &
grep "N:CLIN:" $f | grep "N:METH:" >& $f.NCLIN.NMETH.tmp 
grep "N:CLIN:" $f | grep "N:MIRN:" >& $f.NCLIN.NMIRN.tmp &
grep "N:CLIN:" $f | grep "N:RPPA:" >& $f.NCLIN.NRPPA.tmp 
grep "N:CLIN:" $f | grep "N:SAMP:" >& $f.NCLIN.NSAMP.tmp &

## next it's N:CNVR x the other 6 ...

echo " N:CNVR vs others ... "
date

grep "N:CNVR:" $f | grep "N:GEXP:" >& $f.NCNVR.NGEXP.tmp 
grep "N:CNVR:" $f | grep "N:GNAB:" >& $f.NCNVR.NGNAB.tmp &
grep "N:CNVR:" $f | grep "N:METH:" >& $f.NCNVR.NMETH.tmp 
grep "N:CNVR:" $f | grep "N:MIRN:" >& $f.NCNVR.NMIRN.tmp &
grep "N:CNVR:" $f | grep "N:RPPA:" >& $f.NCNVR.NRPPA.tmp 
grep "N:CNVR:" $f | grep "N:SAMP:" >& $f.NCNVR.NSAMP.tmp &

## next it's N:GEXP x the other 5 ...

echo " N:GEXP vs others ... "
date

grep "N:GEXP:" $f | grep "N:GNAB:" >& $f.NGEXP.NGNAB.tmp 
grep "N:GEXP:" $f | grep "N:METH:" >& $f.NGEXP.NMETH.tmp &
grep "N:GEXP:" $f | grep "N:MIRN:" >& $f.NGEXP.NMIRN.tmp 
grep "N:GEXP:" $f | grep "N:RPPA:" >& $f.NGEXP.NRPPA.tmp &
grep "N:GEXP:" $f | grep "N:SAMP:" >& $f.NGEXP.NSAMP.tmp

## next it's N:GNAB x the other 4 ...

echo " N:GNAB vs others ... "
date

grep "N:GNAB:" $f | grep "N:METH:" >& $f.NGNAB.NMETH.tmp &
grep "N:GNAB:" $f | grep "N:MIRN:" >& $f.NGNAB.NMIRN.tmp 
grep "N:GNAB:" $f | grep "N:RPPA:" >& $f.NGNAB.NRPPA.tmp &
grep "N:GNAB:" $f | grep "N:SAMP:" >& $f.NGNAB.NSAMP.tmp

## next it's N:METH x the other 3 ...

echo " N:METH vs others ... "
date

grep "N:METH:" $f | grep "N:MIRN:" >& $f.NMETH.NMIRN.tmp &
grep "N:METH:" $f | grep "N:RPPA:" >& $f.NMETH.NRPPA.tmp 
grep "N:METH:" $f | grep "N:SAMP:" >& $f.NMETH.NSAMP.tmp &

## next it's N:MIRN x the other 2 ...

echo " N:MIRN vs others ... "
date

grep "N:MIRN:" $f | grep "N:RPPA:" >& $f.NMIRN.NRPPA.tmp 
grep "N:MIRN:" $f | grep "N:SAMP:" >& $f.NMIRN.NSAMP.tmp

## next it's N:RPPA x the other 1 ...

echo " N:RPPA vs others ... "
date

grep "N:RPPA:" $f | grep "N:SAMP:" >& $f.NRPPA.NSAMP.tmp


echo " "
echo " done with grep'ing ... "
echo " "


echo " " >> $f.proc
echo " " >> $f.proc
ls -alt $f.?????*tmp >> $f.proc
echo " " >> $f.proc
echo " " >> $f.proc
wc -l $f.?????*tmp | grep -v " 0 " | sort -nr >> $f.proc
echo " " >> $f.proc
echo " " >> $f.proc

echo " sorting the individual files ... "
for t in $f.?????*tmp
   do
	echo $t
	sort -grk 5 --temporary-directory=/local/sreynold/scratch/ $t >& $t.sort
   done

echo " concatenating at most 1 million pairs of each type ... "
rm -fr $f.short
rm -fr $f.short.sort
echo " " > $f.short
for t in $f.?????*tmp.sort
    do
        echo $t
	head -1000000 $t >> $f.short
    done

echo " now sorting the short concatenation ... "
sort -grk 5 --temporary-directory=/local/sreynold/scratch/ $f.short >& $f.short.sort

date

rm -fr $f.?????.tmp
rm -fr $f.?????.tmp.sort
rm -fr $f.?????.?????.tmp
rm -fr $f.?????.?????.tmp.sort
rm -fr $f.short

echo " and last but not least, removing unmapped features ... "
python ~/code/new_pipeline/filterPWPV.py $f.short.sort 

grep -iv "pathway" $f.short.sort.mapped | grep -v "	nan	" >& $f.short.sort.mapped.noPathway

date

echo " "
echo " "
