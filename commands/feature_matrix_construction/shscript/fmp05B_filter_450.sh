#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      one tumor type, eg 'ucec'

WRONGARGS=1
if [[ $# != 2 ]] && [[ $# != 3 ]]
    then
        echo " Usage   : `basename $0` <curDate> <tumorType> [auxName] "
        echo " Example : `basename $0` 28oct13  brca  aux "
        echo " "
        echo " Note that the new auxName option at the end is optional and will default to simply aux "
        exit $WRONGARGS
fi

curDate=$1
tumor=$2

if (( $# == 3 ))
    then
        auxName=$3
    else
        auxName=aux
fi



echo " "
echo " "
echo " *******************"
echo `date`
echo " *" $curDate
echo " *******************"


	cd $TCGAFMP_DATA_DIR/$tumor

	echo " "
	echo " "
	date
	echo " Tumor Type " $tumor
	date

	cd $curDate

	## NEW as of 01 nov 2012 ... after the "annotate" step, we will also filter
	## the individual files based on the black-list from the annotations manager
	## --> changing this 14 feb 2013 ... the "filterTSV" step for black- and/or
	##     white-lists needs to be done at the very earliest stage before
	##     the barcodes might get truncated

	## NOTE: within data types (eg mRNA expression, methylation, microRNA),
	## if there are duplicate samples/values between separate input data
	## matrices, the first value will take precedence ... so these files
	## are listed in order of most-recent-platform first

	## .....................................
	## first we handle the microRNA data ...

	echo " handling microRNA data ... "
	## z) filter using black and white lists ...
	rm -fr filterSamp.mirn.tmp?.log
        rm -fr $tumor.mirn.tmpData?.tsv
        rm -fr $tumor.mirn.tmp?.tsv

	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq.$curDate.tsv \
		$tumor.mirn.tmpA.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.mirn.tmpA.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.bcgsc.ca__illuminaga_mirnaseq__mirnaseq.$curDate.tsv \
		$tumor.mirn.tmpB.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.mirn.tmpB.log

	## a) merge 
	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
		$tumor.mirn.tmpA.tsv \
		$tumor.mirn.tmpB.tsv \
		$tumor.mirn.tmpData1.tsv >& merge.mirn.$curDate.log
	## b) annotate
	rm -fr annotate.mirn.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.mirn.tmpData1.tsv hg19 \
		$tumor.mirn.tmpData2.tsv NO >& annotate.mirn.$curDate.log
	## c) highVar
	rm -fr highVar.mirn?.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
		$tumor.mirn.tmpData2.tsv \
		$tumor.mirn.tmpData2b.tsv \
		0.75 NZC >& highVar.mirn1.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
		$tumor.mirn.tmpData2b.tsv \
		$tumor.mirn.tmpData3.tsv \
		0.75 IDR >& highVar.mirn2.$curDate.log 

	## ......................................
	## the SNP data we will only annotate and remove black-listed samples
	echo " handling copy-number data ... "
	rm -fr $tumor.cnvr.tmpData?.tsv 

	## almost always, the SNP data comes from the Broad ... but *sometimes* it comes from WashU
	## data from the Broad should take precedence!
	if [ -f $tumor.broad.mit.edu__genome_wide_snp_6__snp.$curDate.tsv ]
	    then
		rm -fr filterSamp.cnvr.log
		python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
			$tumor.broad.mit.edu__genome_wide_snp_6__snp.$curDate.tsv \
			$tumor.cnvr.tmpData1.tsv \
			$tumor.blacklist.samples.tsv black loose \
                        ../$auxName/$tumor.blacklist.loose.tsv black loose \
                        ../$auxName/$tumor.whitelist.loose.tsv white loose \
                        ../$auxName/$tumor.whitelist.strict.tsv white strict \
                        >& filterSamp.cnvr.log
	    else
		if [ -f $tumor.genome.wustl.edu__genome_wide_snp_6__snp.$curDate.tsv ]
		    then
			rm -fr filterSamp.cnvr.log
			python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
				$tumor.genome.wustl.edu__genome_wide_snp_6__snp.$curDate.tsv \
				$tumor.cnvr.tmpData1.tsv \
				$tumor.blacklist.samples.tsv black loose \
                                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                                >& filterSamp.cnvr.log
		fi
	fi

	## proceed only if we have some sort of copy-number data
	if [ -f $tumor.cnvr.tmpData1.tsv ]
	    then
		rm -fr annotate.cnvr.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
			$tumor.cnvr.tmpData1.tsv hg19 \
			$tumor.cnvr.tmpData3.tsv NO >& annotate.cnvr.$curDate.log
	fi

	## .......................................
	## next we handle the methylation data ...
	echo " handling methylation data ... "
	## z) filter using black and white lists ...
	rm -fr filterSamp.meth.tmp?.log
        rm -fr $tumor.meth.tmpData?.tsv
        rm -fr $tumor.meth.tmp?.tsv

        python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
                ../meth450k/$tumor.meth_gexp_mirn.plus.annot.tsv \
                $tumor.meth.tmpData3.tsv \
                $tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.meth.tmpA.log

        ## the typical steps a) b) and c) are no longer needed here
        ## because the data is already all prepped in the ../meth450k/ file

	## .......................................
	## the RPPA data we will only annotate and filter out black-listed samples
	echo " handling RPPA data ... "
	rm -fr $tumor.rppa.tmpData?.tsv 
	rm -fr filterSamp.rppa.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.mdanderson.org__mda_rppa_core__protein_exp.$curDate.tsv \
		$tumor.rppa.tmpData1.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.rppa.log

	rm -fr annotate.rppa.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.rppa.tmpData1.tsv hg19 \
		$tumor.rppa.tmpData3.tsv NO >& annotate.rppa.$curDate.log

	## ...................................................
	## and the MSI calls don't need any pre-processing ...
	echo " handling MSI calls ... "
	rm -fr $tumor.msat.tmpData?.tsv
	cp $tumor.nationwidechildrens.org__microsat_i__fragment_analysis.$curDate.tsv $tumor.msat.tmpData3.tsv

	## ...................................
	## and finally the mRNA expression ...
	## 	NEW 20dec12 : two 'gexp' matrices will be created (if possible)
	##	one using "array" data and one using "seq" data
	echo " handling mRNA expression (ARRAY data) ... "

	## z) filter using black and white lists ...
	rm -fr filterSamp.gexp.ary.tmp?.log
        rm -fr $tumor.gexp.ary.tmpData?.tsv
        rm -fr $tumor.gexp.ary.tmp?.tsv

	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__agilentg4502a_07_3__transcriptome.$curDate.tsv \
		$tumor.gexp.ary.tmpA.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.ary.tmpA.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__agilentg4502a_07_2__transcriptome.$curDate.tsv \
		$tumor.gexp.ary.tmpB.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.ary.tmpB.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__agilentg4502a_07_1__transcriptome.$curDate.tsv \
		$tumor.gexp.ary.tmpC.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.ary.tmpC.log

	## a) merge 
	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
		$tumor.gexp.ary.tmpA.tsv \
		$tumor.gexp.ary.tmpB.tsv \
		$tumor.gexp.ary.tmpC.tsv \
		$tumor.gexp.ary.tmpData1.tsv >& merge.gexp.ary.$curDate.log

        if [ -f $tumor.gexp.ary.tmpData1.tsv ]
            then
	        sed -e '3,$s/:	/:array	/' $tumor.gexp.ary.tmpData1.tsv >& $tumor.gexp.ary.tmpData1b.tsv
        fi

	## b) annotate
	rm -fr annotate.gexp.ary.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.gexp.ary.tmpData1b.tsv hg19 \
		$tumor.gexp.ary.tmpData2.tsv NO >& annotate.gexp.ary.$curDate.log

        ## NEW 03jul13 ... pathway-level expression features
####       --> removed for now ... 06dec13
####        rm -fr pathway.gexp.ary.$curDate.log
####        python $TCGAFMP_ROOT_DIR/main/addPathwayGEXPs.py \
####                $tumor.gexp.ary.tmpData2.tsv \
####                $tumor.gexp.ary.tmpData2b.tsv >& pathway.gexp.ary.$curDate.log

	## c) highVar
	rm -fr highVar.gexp.ary.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
		$tumor.gexp.ary.tmpData2.tsv \
		$tumor.gexp.ary.tmpData3.tsv \
		0.75 IDR >& highVar.gexp.ary.$curDate.log 

	## ----------------------------------------------------
	echo " handling mRNA expression (SEQUENCING data) ... "

	## z) filter using black and white lists ...
	rm -fr filterSamp.gexp.seq.tmp?.log
        rm -fr $tumor.gexp.seq.tmpData?.tsv
        rm -fr $tumor.gexp.seq.tmp?.tsv

	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__illuminaga_rnaseqv2__rnaseqv2.$curDate.tsv \
		$tumor.gexp.seq.tmpF.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.seq.tmpF.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$curDate.tsv \
		$tumor.gexp.seq.tmpA.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.seq.tmpA.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpB.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.seq.tmpB.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpC.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.seq.tmpC.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpD.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.seq.tmpD.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpE.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.seq.tmpE.log

	## a) merge 
	if [[ -f $tumor.gexp.seq.tmpA.tsv || -f $tumor.gexp.seq.tmpF.tsv || -f $tumor.gexp.seq.tmpB.tsv || -f $tumor.gexp.seq.tmpC.tsv ]]
	    then
		echo "         merging seq A F B C (UNC RNAseq data) "
		python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
			$tumor.gexp.seq.tmpA.tsv \
			$tumor.gexp.seq.tmpF.tsv \
			$tumor.gexp.seq.tmpB.tsv \
			$tumor.gexp.seq.tmpC.tsv \
			$tumor.gexp.seq.tmpData1.tsv >& merge.gexp.seq.$curDate.log
	    else
		echo "         merging seq D E (BCGSC RNAseq data) "
		python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
			$tumor.gexp.seq.tmpD.tsv \
			$tumor.gexp.seq.tmpE.tsv \
			$tumor.gexp.seq.tmpData1.tsv >& merge.gexp.seq.$curDate.log
	    fi
	## b) annotate
	rm -fr annotate.gexp.seq.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.gexp.seq.tmpData1.tsv hg19 \
		$tumor.gexp.seq.tmpData2.tsv NO >& annotate.gexp.seq.$curDate.log

        ## NEW 03jul13 ... pathway-level expression features
####       --> removed for now ... 06dec13
####        rm -fr pathway.gexp.seq.$curDate.log
####        python $TCGAFMP_ROOT_DIR/main/addPathwayGEXPs.py \
####                $tumor.gexp.seq.tmpData2.tsv \
####                $tumor.gexp.seq.tmpData2b.tsv >& pathway.gexp.seq.$curDate.log

	## c) highVar
	rm -fr highVar.gexp.seq.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
		$tumor.gexp.seq.tmpData2.tsv \
		$tumor.gexp.seq.tmpData3.tsv \
		0.75 IDR >& highVar.gexp.seq.$curDate.log 



	echo " "
	echo " "
	echo " looking at the sizes of the tmpData3 files ... "
	for f in $tumor.*.tmpData3.tsv
	    do
		python $TCGAFMP_ROOT_DIR/main/quickLook.py $f | grep -i "summary"
	    done


echo " "
echo " fmp05B_filter script is FINISHED !!! "
date
echo " "
echo " now updating gene lists "
$TCGAFMP_ROOT_DIR/shscript/make_gene_listsB.sh $curDate $tumor
echo " "
echo `date`
echo " "

