#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      one tumor type, eg 'ucec'

WRONGARGS=1
if [ $# != 2 ]
    then
        echo " Usage   : `basename $0` <curDate> <tumorType> "
        echo " Example : `basename $0` 28oct13  brca "
        exit $WRONGARGS
fi

curDate=$1
tumor=$2

echo " "
echo " "
echo " *******************"
echo `date`
echo " *" $curDate
echo " *******************"

	cd $TCGAFMP_DATA_DIR/$tumor

	echo " "
	echo " "
	echo " Tumor Type " $tumor
	date

	cd $curDate

        for sub in ary seq all
            do

                echo " "
                date
                echo "subset" $tumor $sub $curDate

		##	a) add jitter 
		##	b) copy clinical information to all samples for a given patient
	        ##      *) add custom features (new 13may13)
		##	c) add the sampleType feature
		##	d) split the feature matrix according to sampleType
	
		if [ -f $tumor.newMerge.$sub.$curDate.tsv ]
		    then

                        echo "processing" $tumor $sub $curDate
	
			rm -fr $tumor.$sub.j.$curDate.log
                        echo "     adding jitter ... "
			python $TCGAFMP_ROOT_DIR/main/jitterTSV.py \
				$tumor.newMerge.$sub.$curDate.tsv \
				$tumor.newMerge.$sub.$curDate.j.tsv >& $tumor.$sub.$curDate.j.log
		
			rm -fr $tumor.$sub.jc.$curDate.log
                        echo "     copying clinical information ... "
			python $TCGAFMP_ROOT_DIR/main/copyClinInfo.py \
				$tumor.newMerge.$sub.$curDate.j.tsv \
				$tumor.newMerge.$sub.$curDate.jc.tsv >& $tumor.$sub.$curDate.jc.log
		
			rm -fr $tumor.$sub.jct.$curDate.log tmp1.tsv
                        echo "     adding sampleType ... "
			python $TCGAFMP_ROOT_DIR/main/addSampleType.py \
				$tumor.newMerge.$sub.$curDate.jc.tsv \
				tmp1.tsv >& $tumor.$sub.$curDate.jct.log
	
	                rm -fr tmp2.tsv $tumor.$sub.$curDate.customFeat.log
                        ## echo "     adding custom features (a) ... "
	                ## python $TCGAFMP_ROOT_DIR/main/addCustomFeat2.py \
			##	  tmp1.tsv \
	                ##        tmp2.tsv >> $tumor.$sub.$curDate.customFeat.log
                        echo "     adding custom features (b) ... "
	                python $TCGAFMP_ROOT_DIR/main/addCustomFeat3.py \
				tmp1.tsv \
	                        $tumor.newMerge.$sub.$curDate.jct.tsv >> $tumor.$sub.$curDate.customFeat.log
	
		fi

            done

echo " "
echo " fmp07B_misc script is FINISHED !!! "
echo `date`
echo " "

