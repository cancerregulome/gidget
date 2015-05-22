#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      date, eg '29jan13'
##      snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##      one or more tumor types, eg: 'prad thca skcm stad'

WRONGARGS=1
if [ $# != 1 ]
    then
        echo " Usage   : `basename $0` <tumorType> "
        echo " Example : `basename $0` brca "
        exit $WRONGARGS
fi

tumor=$1

curwd=`pwd`


	cd $TCGAFMP_DATA_DIR/$tumor

	echo " "
	echo " "
	date
	echo " Tumor Type " $tumor
	date

	cd gnab

	## ----------------------------------------------------------------------------
	## first, we're going to do some tweaking of feature names and such and 
	## eventually write out a file called $tumor.gnab.tmpData1.tsv

	rm -fr gnab.tmp.?
	rm -fr gnab.tmp.??
	rm -fr $tumor.gnab.tmpData1.tsv

	## BUT now we actually need to remove the "A" or "B" or "C" or "D" from the end ...
	sed -e '2,$s/-01A	/-01	/' latest.gnab.txt | \
		sed -e '2,$s/-01B	/-01	/' | \
		sed -e '2,$s/-01C	/-01	/' | \
		sed -e '2,$s/-01D	/-01	/' | \
		sed -e '2,$s/-02A	/-02	/' | \
		sed -e '2,$s/-02B	/-02	/' | \
		sed -e '2,$s/-02C	/-02	/' | \
		sed -e '2,$s/-02D	/-02	/' | \
		sed -e '2,$s/-03A	/-03	/' | \
		sed -e '2,$s/-03B	/-03	/' | \
		sed -e '2,$s/-03C	/-03	/' | \
		sed -e '2,$s/-03D	/-03	/' | \
		sed -e '2,$s/-06A	/-06	/' | \
		sed -e '2,$s/-06B	/-06	/' | \
		sed -e '2,$s/-06C	/-06	/' | \
		sed -e '2,$s/-06D	/-06	/' >& gnab.tmp.1

	$TCGAFMP_ROOT_DIR/shscript/tcga_fmp_transpose.sh gnab.tmp.1 >& gnab.tmp.2

	## now for some ugly processing ...
	sed -e '1s/	/B:GNAB	/' gnab.tmp.2 | sed -e '2,$s/^/B:GNAB:/g' | sed -e '2,$s/_/:::::/' | \
		sed -e '2,$s/	/_somatic	/' | sed -e '1s/GBM-/TCGA-/g' | \
		sed -e '1s/Native-//g' | sed -e '1s/-Tumor//g' >& gnab.tmp.3
	
	## change the iarc_freq feature(s) to "N" from "B"
	grep "iarc_freq" gnab.tmp.3 | sed -e '1,$s/B:GNAB/N:GNAB/' >& gnab.tmp.3a
        grep "ja_lhood_" gnab.tmp.3 | sed -e '1,$s/B:GNAB/N:GNAB/' >& gnab.tmp.3b
        grep "ja_ddG_"   gnab.tmp.3 | sed -e '1,$s/B:GNAB/N:GNAB/' >& gnab.tmp.3c
        grep "ja_PP_"    gnab.tmp.3 | sed -e '1,$s/B:GNAB/N:GNAB/' >& gnab.tmp.3d
	
	## grab all the rest, then divide into features with decimals and features w/o
	grep -v "iarc_freq" gnab.tmp.3 | grep -v "ja_lhood_" | grep -v "ja_ddG_" | grep -v "ja_PP_" >& gnab.tmp.3e
	
        cat gnab.tmp.3e gnab.tmp.3a gnab.tmp.3b gnab.tmp.3c gnab.tmp.3d >& gnab.tmp.4
	
	## NEW: put in a step here that checks/fixes the feature names (B: vs N:)
	## and also removes any features that are *uniform*
	python $TCGAFMP_ROOT_DIR/main/fixupGnabBits.py gnab.tmp.4 gnab.tmp.5.tsv

	## NEW: make sure that the barcodes are tumor-specific barcodes ...
	python $TCGAFMP_ROOT_DIR/main/tumorBarcodes.py gnab.tmp.5.tsv $tumor.gnab.tmpData1.tsv
	
	python $TCGAFMP_ROOT_DIR/main/quickLook.py $tumor.gnab.tmpData1.tsv | grep "Summary"

	## at this point we have a file called $tumor.gnab.tmpData1.tsv

        ## keep only the "code_potential" features with at least one '1'
        rm -fr h1 g1
        head -1 $tumor.gnab.tmpData1.tsv >& h1
        grep "code_potential" $tumor.gnab.tmpData1.tsv | grep "	1" >& g1
        cat h1 g1 >& $tumor.gnab.tmpData2.tsv

        rm -fr h1 g1

        ## and annotate the gene symbols
        python $TCGAFMP_ROOT_DIR/main/annotateTSV.py $tumor.gnab.tmpData2.tsv hg19 $tumor.gnab.filter.annot.tsv NO

	cd ..
	cd ..


echo " "
echo " fmp03B_gnab_new script is FINISHED !!! "
date
echo " "

cd $curwd
