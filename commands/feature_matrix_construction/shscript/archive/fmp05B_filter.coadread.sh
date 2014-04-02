#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

## this script should be called with the following parameters:
##      date, eg '29jan13'
##      one or more tumor types, eg: 'prad thca skcm stad'
curDate=$1

if [ -z "$curDate" ]
    then
        echo " this script must be called with a date string of some kind, eg 28feb13 "
        exit
fi

echo " "
echo " "
echo " *******************"
echo " *" $curDate
echo " *******************"


	cd $TCGAFMP_DATA_DIR/coadread

	echo " "
	echo " "
	date
	echo " Special handling of COAD+READ ... " 
	date

	cd $curDate

	## .....................................
	## first we handle the microRNA data ...

	echo " handling microRNA data ... "
	## a) merge 
	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
                ../../coad/$curDate/$tumor.mirn.tmpA.tsv \
                ../../coad/$curDate/$tumor.mirn.tmpB.tsv \
                ../../read/$curDate/$tumor.mirn.tmpA.tsv \
                ../../read/$curDate/$tumor.mirn.tmpB.tsv \
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
			$tumor.blacklist.samples.tsv black loose \
                        ../aux/$tumor.blacklist.loose.tsv black loose \
                        ../aux/$tumor.whitelist.loose.tsv white loose \
                        ../aux/$tumor.whitelist.strict.tsv white strict \
                        >& filterSamp.cnvr.log
	    else
		if [ -f $tumor.genome.wustl.edu__genome_wide_snp_6__snp.$curDate.tsv ]
		    then
			rm -fr filterSamp.cnvr.log
			python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
				$tumor.genome.wustl.edu__genome_wide_snp_6__snp.$curDate.tsv \
				$tumor.cnvr.tmpData1.tsv \
				$tumor.blacklist.samples.tsv black loose \
                                ../aux/$tumor.blacklist.loose.tsv black loose \
                                ../aux/$tumor.whitelist.loose.tsv white loose \
                                ../aux/$tumor.whitelist.strict.tsv white strict \
                                >& filterSamp.cnvr.log
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
		$tumor.blacklist.samples.tsv black loose \
                ../aux/$tumor.blacklist.loose.tsv black loose \
                ../aux/$tumor.whitelist.loose.tsv white loose \
                ../aux/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.meth.tmpA.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.jhu-usc.edu__humanmethylation27__methylation.$curDate.tsv \
		$tumor.meth.tmpB.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../aux/$tumor.blacklist.loose.tsv black loose \
                ../aux/$tumor.whitelist.loose.tsv white loose \
                ../aux/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.meth.tmpB.log

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
		$tumor.blacklist.samples.tsv black loose \
                ../aux/$tumor.blacklist.loose.tsv black loose \
                ../aux/$tumor.whitelist.loose.tsv white loose \
                ../aux/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.rppa.log

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
		$tumor.blacklist.samples.tsv black loose \
                ../aux/$tumor.blacklist.loose.tsv black loose \
                ../aux/$tumor.whitelist.loose.tsv white loose \
                ../aux/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.ary.tmpA.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__agilentg4502a_07_2__transcriptome.$curDate.tsv \
		$tumor.gexp.ary.tmpB.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../aux/$tumor.blacklist.loose.tsv black loose \
                ../aux/$tumor.whitelist.loose.tsv white loose \
                ../aux/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.ary.tmpB.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__agilentg4502a_07_1__transcriptome.$curDate.tsv \
		$tumor.gexp.ary.tmpC.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../aux/$tumor.blacklist.loose.tsv black loose \
                ../aux/$tumor.whitelist.loose.tsv white loose \
                ../aux/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.ary.tmpC.log

	## a) merge 
	python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
		$tumor.gexp.ary.tmpA.tsv \
		$tumor.gexp.ary.tmpB.tsv \
		$tumor.gexp.ary.tmpC.tsv \
		$tumor.gexp.ary.tmpData1.tsv >& merge.gexp.ary.$curDate.log

	sed -e '3,$s/:	/:array	/' $tumor.gexp.ary.tmpData1.tsv >& $tumor.gexp.ary.tmpData1b.tsv

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

	if [ -f $tumor.unc.edu__illuminaga_rnaseqv2__rnaseqv2.$curDate.tsv ]
	    then
		python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
			$tumor.unc.edu__illuminaga_rnaseqv2__rnaseqv2.$curDate.tsv \
			$tumor.gexp.seq.tmpA.tsv \
			$tumor.blacklist.samples.tsv black loose \
                        ../aux/$tumor.blacklist.loose.tsv black loose \
                        ../aux/$tumor.whitelist.loose.tsv white loose \
                        ../aux/$tumor.whitelist.strict.tsv white strict \
                        >& filterSamp.gexp.seq.tmpA.log
	    fi
        if [ -f $tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$curDate.tsv ]
	    then
		python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
			$tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$curDate.tsv \
			$tumor.gexp.seq.tmpA.tsv \
			$tumor.blacklist.samples.tsv black loose \
                        ../aux/$tumor.blacklist.loose.tsv black loose \
                        ../aux/$tumor.whitelist.loose.tsv white loose \
                        ../aux/$tumor.whitelist.strict.tsv white strict \
                        >& filterSamp.gexp.seq.tmpA.log
	    fi
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpB.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../aux/$tumor.blacklist.loose.tsv black loose \
                ../aux/$tumor.whitelist.loose.tsv white loose \
                ../aux/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.seq.tmpB.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpC.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../aux/$tumor.blacklist.loose.tsv black loose \
                ../aux/$tumor.whitelist.loose.tsv white loose \
                ../aux/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.seq.tmpC.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpD.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../aux/$tumor.blacklist.loose.tsv black loose \
                ../aux/$tumor.whitelist.loose.tsv white loose \
                ../aux/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.seq.tmpD.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		$tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv \
		$tumor.gexp.seq.tmpE.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../aux/$tumor.blacklist.loose.tsv black loose \
                ../aux/$tumor.whitelist.loose.tsv white loose \
                ../aux/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.gexp.seq.tmpE.log

	## a) merge 
	if [[ -f $tumor.gexp.seq.tmpA.tsv || -f $tumor.gexp.seq.tmpB.tsv || -f $tumor.gexp.seq.tmpC.tsv ]]
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

