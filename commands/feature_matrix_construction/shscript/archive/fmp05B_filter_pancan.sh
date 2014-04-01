#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

## this script should be called with the following parameters:
##      date, eg '29jan13'
##      one or more tumor types, eg: 'prad thca skcm stad'
curDate=$1
tumor=$2

if [ -z "$curDate" ]
    then
        echo " this script must be called with a date string of some kind, eg 28feb13 "
        exit
fi
if [ -z "$tumor" ]
    then
        echo " this script must be called with at least one tumor type "
        exit
fi

echo " "
echo " "
echo " *******************"
echo " *" $curDate
echo " *******************"

args=("$@")
for ((i=1; i<$#; i++))
    do
        tumor=${args[$i]}

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
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq.$curDate.tsv \
		$tumor.mirn.tmpA.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.mirn.tmpA.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.bcgsc.ca__illuminaga_mirnaseq__mirnaseq.$curDate.tsv \
		$tumor.mirn.tmpB.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.mirn.tmpB.log

	## a) merge 
	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
		$tumor.mirn.tmpA.tsv \
		$tumor.mirn.tmpB.tsv \
		$tumor.mirn.tmpData1.tsv >& merge.mirn.$curDate.log
	## b) annotate
	rm -fr annotate.mirn.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.mirn.tmpData1.tsv hg19 \
		$tumor.mirn.tmpData2.tsv >& annotate.mirn.$curDate.log
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
	rm $tumor.cnvr.tmpData?.tsv 

	## almost always, the SNP data comes from the Broad ... but *sometimes* it comes from WashU
	## data from the Broad should take precedence!
	if [ -f $tumor.broad.mit.edu__genome_wide_snp_6__snp.$curDate.tsv ]
	    then
		rm -fr filterSamp.cnvr.log
		python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
			$tumor.broad.mit.edu__genome_wide_snp_6__snp.$curDate.tsv \
			$tumor.cnvr.tmpData1.tsv \
			../aux/$tumor.whitelist.pancan.tsv white strict \
			$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.cnvr.log
	    else
		if [ -f $tumor.genome.wustl.edu__genome_wide_snp_6__snp.$curDate.tsv ]
		    then
			rm -fr filterSamp.cnvr.log
			python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
				$tumor.genome.wustl.edu__genome_wide_snp_6__snp.$curDate.tsv \
				$tumor.cnvr.tmpData1.tsv \
				../aux/$tumor.whitelist.pancan.tsv white strict \
				$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.cnvr.log
		fi
	fi

	## proceed only if we have some sort of copy-number data
	if [ -f $tumor.cnvr.tmpData1.tsv ]
	    then
		rm -fr annotate.cnvr.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
			$tumor.cnvr.tmpData1.tsv hg19 \
			$tumor.cnvr.tmpData3.tsv >& annotate.cnvr.$curDate.log
	fi

	## .......................................
	## next we handle the methylation data ...
	echo " handling methylation data ... "
	## z) filter using black and white lists ...
	rm -fr filterSamp.meth.tmp?.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
                $tumor.jhu-usc.edu__humanmethylation450__methylation.$curDate.tsv \
		$tumor.meth.tmpA.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.meth.tmpA.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.jhu-usc.edu__humanmethylation27__methylation.$curDate.tsv \
		$tumor.meth.tmpB.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.meth.tmpB.log

	## a) merge 
	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
		$tumor.meth.tmpA.tsv \
		$tumor.meth.tmpB.tsv \
		$tumor.meth.tmpData1.tsv >& merge.meth.$curDate.log
	## b) annotate
	rm -fr annotate.meth.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.meth.tmpData1.tsv hg19 \
		$tumor.meth.tmpData2.tsv >& annotate.meth.$curDate.log
	## c) highVar
	rm -fr highVar.meth.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
		$tumor.meth.tmpData2.tsv \
		$tumor.meth.tmpData3.tsv \
		0.75 IDR >& highVar.meth.$curDate.log 

	## .......................................
	## the RPPA data we will only annotate and filter out black-listed samples
	echo " handling RPPA data ... "
	rm $tumor.rppa.tmpData?.tsv 
	rm -fr filterSamp.rppa.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.mdanderson.org__mda_rppa_core__protein_exp.$curDate.tsv \
		$tumor.rppa.tmpData1.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.rppa.log

	rm -fr annotate.rppa.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.rppa.tmpData1.tsv hg19 \
		$tumor.rppa.tmpData3.tsv >& annotate.rppa.$curDate.log

	## ...................................................
	## and the MSI calls don't need any pre-processing ...
	echo " handling MSI calls ... "
	rm $tumor.msat.tmpData3.tsv
	cp $tumor.nationwidechildrens.org__microsat_i__fragment_analysis.$curDate.tsv $tumor.msat.tmpData3.tsv

	## ...................................
	## and finally the mRNA expression ...
	## 	NEW 20dec12 : two 'gexp' matrices will be created (if possible)
	##	one using "array" data and one using "seq" data
	echo " handling mRNA expression (ARRAY data) ... "

	## z) filter using black and white lists ...
	rm -fr filterSamp.gexp.ary.tmp?.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__agilentg4502a_07_3__transcriptome.$curDate.tsv \
		$tumor.gexp.ary.tmpA.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.gexp.ary.tmpA.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__agilentg4502a_07_2__transcriptome.$curDate.tsv \
		$tumor.gexp.ary.tmpB.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.gexp.ary.tmpB.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__agilentg4502a_07_1__transcriptome.$curDate.tsv \
		$tumor.gexp.ary.tmpC.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.gexp.ary.tmpC.log

	## a) merge 
	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
		$tumor.gexp.ary.tmpA.tsv \
		$tumor.gexp.ary.tmpB.tsv \
		$tumor.gexp.ary.tmpC.tsv \
		$tumor.gexp.ary.tmpData1.tsv >& merge.gexp.ary.$curDate.log

	sed -e '3,$s/:	/:array	/' $tumor.gexp.ary.tmpData1.tsv >& gexp.ary.tmpData1b.tsv

	## b) annotate
	rm -fr annotate.gexp.ary.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.gexp.ary.tmpData1b.tsv hg19 \
		$tumor.gexp.ary.tmpData2.tsv >& annotate.gexp.ary.$curDate.log
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
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
                $tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$curDate.tsv \
		$tumor.gexp.seq.tmpA.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.gexp.seq.tmpA.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpB.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.gexp.seq.tmpB.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpC.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.gexp.seq.tmpC.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpD.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.gexp.seq.tmpD.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpE.tsv \
		../aux/$tumor.whitelist.pancan.tsv white strict \
		$tumor.blacklist.samples.$curDate.tsv black loose >& filterSamp.gexp.seq.tmpE.log

	## a) merge 
	if [ -f $tumor.gexp.seq.tmpA.tsv ] || [ -f $tumor.gexp.seq.tmpB.tsv ] || -f [ $tumor.gexp.seq.tmpC.tsv ]
	    then
		echo "         merging seq A B C "
		python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
			$tumor.gexp.seq.tmpA.tsv \
			$tumor.gexp.seq.tmpB.tsv \
			$tumor.gexp.seq.tmpC.tsv \
			$tumor.gexp.seq.tmpData1.tsv >& merge.gexp.seq.$curDate.log
	    else
		echo "         merging seq D E "
		python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
			$tumor.gexp.seq.tmpD.tsv \
			$tumor.gexp.seq.tmpE.tsv \
			$tumor.gexp.seq.tmpData1.tsv >& merge.gexp.seq.$curDate.log
	    fi
	## b) annotate
	rm -fr annotate.gexp.seq.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.gexp.seq.tmpData1.tsv hg19 \
		$tumor.gexp.seq.tmpData2.tsv >& annotate.gexp.seq.$curDate.log
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

    done

echo " "
echo " fmp05B_filter script is FINISHED !!! "
date
echo " "
echo " now updating gene lists "
$TCGAFMP_ROOT_DIR/shscript/make_gene_listsB.sh $curDate $tumor
echo " "
echo " "

