#!/bin/bash

## NOTE: only the highVarTSV calls (the final step for each platform) is sent to
## run in the background because otherwise each step depends on the previous step
## in this portion of the pipeline

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

## this script should be called with a current date string such as 14jan13 (ie ddmmmyy)
curDate=$1

if [ -z "$curDate" ]
    then
        echo " this script must be called with a date string of some kind, eg 28feb13 "
        exit
fi

echo " "
echo " "
echo " ***********"
echo " *" $curDate "* "
echo " ***********"

## for tumor in blca brca cesc cntl coad dlbc esca gbm hnsc kich kirc kirp laml lcll lgg lihc lnnh luad lusc ov paad prad read sarc skcm stad thca ucec
for tumor in skcm stad thca ucec

    do

	cd $TCGAFMP_DATA_DIR/$tumor

	echo " "
	echo " "
	date
	echo " Tumor Type " $tumor
	date

	cd $curDate

	## NEW as of 01 nov 2012 ... after the "annotate" step, we will also filter
	## the individual files based on the black-list from the annotations manager

	## NOTE: within data types (eg mRNA expression, methylation, microRNA),
	## if there are duplicate samples/values between separate input data
	## matrices, the first value will take precedence ... so these files
	## are listed in order of most-recent-platform first

	## .....................................
	## first we handle the microRNA data ...
	## a) merge 
	echo " handling microRNA data ... "
	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
		$tumor.bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq.$curDate.tsv \
		$tumor.bcgsc.ca__illuminaga_mirnaseq__mirnaseq.$curDate.tsv \
		$tumor.mirn.tmpData1.tsv
	## b) annotate
	rm -fr annotate.mirn.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.mirn.tmpData1.tsv hg19 \
		$tumor.mirn.tmpData2a.tsv >& annotate.mirn.$curDate.log
	rm -fr filterSamp.mirn.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.mirn.tmpData2a.tsv $tumor.blacklist.samples.$curDate.tsv black \
		$tumor.mirn.tmpData2.tsv >& filterSamp.mirn.$curDate.log
	## c) highVar
	rm -fr highVar.mirn?.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
		$tumor.mirn.tmpData2.tsv \
		$tumor.mirn.tmpData2b.tsv \
		0.75 NZC >& highVar.mirn1.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
		$tumor.mirn.tmpData2b.tsv \
		$tumor.mirn.tmpData3.tsv \
		0.75 IDR >& highVar.mirn2.$curDate.log &

	## ......................................
	## the SNP data we will only annotate and remove black-listed samples
	echo " handling copy-number data ... "
	rm $tumor.cnvr.tmpData?.tsv 

	## almost always, the SNP data comes from the Broad ... but *sometimes* it comes from WashU
	if [ -f $tumor.broad.mit.edu__genome_wide_snp_6__snp.$curDate.tsv ]
	    then
		cp $tumor.broad.mit.edu__genome_wide_snp_6__snp.$curDate.tsv $tumor.cnvr.tmpData1.tsv
	    else
		if [ -f $tumor.genome.wustl.edu__genome_wide_snp_6__snp.$curDate.tsv ]
		    then
			cp $tumor.genome.wustl.edu__genome_wide_snp_6__snp.$curDate.tsv $tumor.cnvr.tmpData1.tsv
		fi
	fi

	## proceed only if we have some sort of copy-number data
	if [ -f $tumor.cnvr.tmpData1.tsv ]
	    then
		rm -fr annotate.cnvr.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
			$tumor.cnvr.tmpData1.tsv hg19 \
			$tumor.cnvr.tmpData2a.tsv >& annotate.cnvr.$curDate.log
		rm -fr filterSamp.cnvr.$curDate.log
		python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
			$tumor.cnvr.tmpData2a.tsv $tumor.blacklist.samples.$curDate.tsv black \
			$tumor.cnvr.tmpData2.tsv >& filterSamp.cnvr.$curDate.log
		cp $tumor.cnvr.tmpData2.tsv $tumor.cnvr.tmpData3.tsv
	fi

	## .......................................
	## next we handle the methylation data ...
	## a) merge 
	echo " handling methylation data ... "
	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
                $tumor.jhu-usc.edu__humanmethylation450__methylation.$curDate.tsv \
		$tumor.jhu-usc.edu__humanmethylation27__methylation.$curDate.tsv \
		$tumor.meth.tmpData1.tsv
	## b) annotate
	rm -fr annotate.meth.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.meth.tmpData1.tsv hg19 \
		$tumor.meth.tmpData2a.tsv >& annotate.meth.$curDate.log
	rm -fr filterSamp.meth.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.meth.tmpData2a.tsv $tumor.blacklist.samples.$curDate.tsv black \
		$tumor.meth.tmpData2.tsv >& filterSamp.meth.$curDate.log
	## c) highVar
	rm -fr highVar.meth.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
		$tumor.meth.tmpData2.tsv \
		$tumor.meth.tmpData3.tsv \
		0.75 IDR >& highVar.meth.$curDate.log &

	## .......................................
	## the RPPA data we will only annotate and filter out black-listed samples
	echo " handling RPPA data ... "
	rm $tumor.rppa.tmpData?.tsv 
	cp $tumor.mdanderson.org__mda_rppa_core__protein_exp.$curDate.tsv $tumor.rppa.tmpData1.tsv
	rm -fr annotate.rppa.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.rppa.tmpData1.tsv hg19 \
		$tumor.rppa.tmpData2a.tsv >& annotate.rppa.$curDate.log
	rm -fr filterSamp.rppa.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.rppa.tmpData2a.tsv $tumor.blacklist.samples.$curDate.tsv black \
		$tumor.rppa.tmpData2.tsv >& filterSamp.rppa.$curDate.log
	cp $tumor.rppa.tmpData2.tsv $tumor.rppa.tmpData3.tsv

	## ...................................................
	## and the MSI calls don't need any pre-processing ...
	echo " handling MSI calls ... "
	rm $tumor.msat.tmpData3.tsv
	cp $tumor.nationwidechildrens.org__microsat_i__fragment_analysis.$curDate.tsv $tumor.msat.tmpData3.tsv

	## ...................................
	## and finally the mRNA expression ...
	## 	NEW 20dec12 : two 'gexp' matrices will be created (if possible)
	##	one using "array" data and one using "seq" data

	## a) merge 
	echo " handling mRNA expression (ARRAY data) ... "
	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
		$tumor.unc.edu__agilentg4502a_07_3__transcriptome.$curDate.tsv \
		$tumor.unc.edu__agilentg4502a_07_2__transcriptome.$curDate.tsv \
		$tumor.unc.edu__agilentg4502a_07_1__transcriptome.$curDate.tsv \
		$tumor.gexp.ary.tmpData1.tsv
	## b) annotate
	rm -fr annotate.gexp.ary.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.gexp.ary.tmpData1.tsv hg19 \
		$tumor.gexp.ary.tmpData2a.tsv >& annotate.gexp.ary.$curDate.log
	rm -fr filterSamp.gexp.ary.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.gexp.ary.tmpData2a.tsv $tumor.blacklist.samples.$curDate.tsv black \
		$tumor.gexp.ary.tmpData2.tsv >& filterSamp.gexp.ary.$curDate.log
	## c) highVar
	rm -fr highVar.gexp.ary.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
		$tumor.gexp.ary.tmpData2.tsv \
		$tumor.gexp.ary.tmpData3.tsv \
		0.75 IDR >& highVar.gexp.ary.$curDate.log &

	## a) merge 
	echo " handling mRNA expression (SEQUENCING data) ... "
	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
                $tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$curDate.tsv \
		$tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
		$tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv \
		$tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
		$tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpData1.tsv
	## b) annotate
	rm -fr annotate.gexp.seq.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/annotateTSV.py \
		$tumor.gexp.seq.tmpData1.tsv hg19 \
		$tumor.gexp.seq.tmpData2a.tsv >& annotate.gexp.seq.$curDate.log
	rm -fr filterSamp.gexp.seq.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.gexp.seq.tmpData2a.tsv $tumor.blacklist.samples.$curDate.tsv black \
		$tumor.gexp.seq.tmpData2.tsv >& filterSamp.gexp.seq.$curDate.log
	## c) highVar
	rm -fr highVar.gexp.seq.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/highVarTSV.py \
		$tumor.gexp.seq.tmpData2.tsv \
		$tumor.gexp.seq.tmpData3.tsv \
		0.75 IDR >& highVar.gexp.seq.$curDate.log &



	echo " "
	echo " "
	echo " looking at the sizes of the tmpData1 files ... "
	for f in $tumor.*.tmpData1.tsv
	    do
		python $TCGAFMP_ROOT_DIR/main/quickLook.py $f | grep -i "summary"
	    done

	## no point in looking at the tmpData3 files because those jobs are 
	## still running in the background ...

    done

echo " "
echo " fmp05_filter script is FINISHED !!! "
date
echo " "
echo " now updating gene lists "
$TCGAFMP_ROOT_DIR/shscript/make_gene_lists.sh $curDate
echo " "
echo " "

