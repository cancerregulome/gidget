#!/bin/bash

: ${LD_LIBRARY_PATH:?" environment variable must be set and non-empty"}
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty"}

if [[ "$PYTHONPATH" != *"gidget"* ]]; then
    echo " "
    echo " your PYTHONPATH should include paths to gidget/commands/... directories "
    echo " "
    exit 99
fi

## this script should be called with the following parameters:
##      date, eg '29jan13'
##      snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##      one or more tumor types, eg: 'prad,thca,skcm,stad'
##      a config file, eg: 'parse_tcga.config', relative to $TCGAFMP_ROOT_DIR/config

WRONGARGS=1
if [ $# != 4 ]
    then
        echo " Usage   : `basename $0` <curDate> <snapshotName> <tumorType> <config>"
        echo " Example : `basename $0` 28oct13 dcc-snapshot-28oct13 brca parse_tcga.config"
        exit $WRONGARGS
fi

curDate=$1
snapshotName=$2
tumors=$(echo $3 | tr "," "\n")
config=$4

echo " "
echo " "
echo " *******************"
echo `date`
echo " *" $curDate
echo " *" $snapshotName
echo " *" $config
echo " *******************"

args=("$@")
for tumor in $tumors
    do

	## cd /titan/cancerregulome3/TCGA/outputs/$tumor
	## cd /titan/cancerregulome14/TCGAfmp_outputs/$tumor
	cd $TCGAFMP_OUTPUTS/$tumor

	echo " "
	echo " "
	date
	echo " Tumor Type " $tumor
	date

	if [ ! -d $curDate ]
	    then
		mkdir $curDate
	fi

	cd $curDate

	rm -fr level3.*.*.$curDate.log
        rm -fr *__*.$curDate.tsv
        rm -fr *__*.$curDate.tsv.bkp

	## COPY-NUMBER
        ## 29may13 : subbing in Michael's version that calls his resegmentation code which should be at least 5x faster
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config broad.mit.edu/genome_wide_snp_6/snp/ $tumor $curDate $snapshotName           >& level3.broad.snp_6.$curDate.log 
	## python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate broad.mit.edu/genome_wide_snp_6/snp $tumor $snapshotName                  >& level3.broad.snp_6.$curDate.log 
	## python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate genome.wustl.edu/genome_wide_snp_6/snp $tumor $snapshotName               >& level3.wustl.snp_6.$curDate.log 

	## MICRO-RNA
	##python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate bcgsc.ca/illuminaga_mirnaseq/mirnaseq $tumor $snapshotName                >& level3.bcgsc.ga_mirn.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config bcgsc.ca/illuminaga_mirnaseq/mirnaseq/ $tumor $curDate $snapshotName                >& level3.bcgsc.ga_mirn.$curDate.log 
	##python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq $tumor $snapshotName             >& level3.bcgsc.hiseq_mirn.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq/ $tumor $curDate $snapshotName             >& level3.bcgsc.hiseq_mirn.$curDate.log 

	## MESSENGER-RNA
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config bcgsc.ca/illuminaga_rnaseq/rnaseq/ $tumor $curDate $snapshotName                    >& level3.bcgsc.ga_rnaseq.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config bcgsc.ca/illuminahiseq_rnaseq/rnaseq/ $tumor $curDate $snapshotName                 >& level3.bcgsc.hiseq_rnaseq.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/agilentg4502a_07_1/transcriptome/ $tumor $curDate $snapshotName             >& level3.unc.agil_07_1.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/agilentg4502a_07_2/transcriptome/ $tumor $curDate $snapshotName             >& level3.unc.agil_07_2.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/agilentg4502a_07_3/transcriptome/ $tumor $curDate $snapshotName             >& level3.unc.agil_07_3.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/illuminaga_rnaseq/rnaseq/ $tumor $curDate $snapshotName                     >& level3.unc.ga_rnaseq.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/illuminahiseq_rnaseq/rnaseq/ $tumor $curDate $snapshotName                  >& level3.unc.hiseq_rnaseq.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/illuminaga_rnaseqv2/rnaseqv2/ $tumor $curDate $snapshotName                 >& level3.unc.ga_rnaseqv2.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/illuminahiseq_rnaseqv2/rnaseqv2/ $tumor $curDate $snapshotName              >& level3.unc.hiseq_rnaseqv2.$curDate.log 

	## METHYLATION
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config jhu-usc.edu/humanmethylation27/methylation/ $tumor $curDate $snapshotName           >& level3.jhu-usc.meth27.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config jhu-usc.edu/humanmethylation450/methylation/ $tumor $curDate $snapshotName          >& level3.jhu-usc.meth450.$curDate.log 

	## RPPA
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config mdanderson.org/mda_rppa_core/protein_exp/ $tumor $curDate $snapshotName             >& level3.mda.rppa.$curDate.log 

	## MICRO-SATELLITE INSTABILITY
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config nationwidechildrens.org/microsat_i/fragment_analysis/ $tumor $curDate $snapshotName >& level3.nwc.microsat_i.$curDate.log 

	## now we need to move any 'obsolete' expression datasets out of the way ...
	rm -fr $tumor.*.$curDate.tsv.bkp

	## new as of 25mar13 ... there is now GA_RNASeqV2 data for COAD, READ and UCEC which
	## we are going to say for now "outranks" any HiSeq_RNASeqV2 data ...
	if [ -f $tumor.unc.edu__illuminaga_rnaseqv2__rnaseqv2.$curDate.tsv ]
	    then
		if [ -f $tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$curDate.tsv ]
		    then
			echo " Illumina GA RNAseq V2 data exists ... moving HiSeq RNAseq V2 dataset to bkp "
		        mv $tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$curDate.tsv \
			   $tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$curDate.tsv.bkp
		fi
		if [ -f $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina GA RNAseq V2 data exists ... moving HiSeq RNAseq V1 dataset to bkp "
		        mv $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
		if [ -f $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina GA RNAseq V2 data exists ... moving GA RNAseq V1 dataset to bkp "
		        mv $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
		if [ -f $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina GA RNAseq V2 data exists ... moving BCGSC HiSeq dataset to bkp "
		        mv $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
		if [ -f $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina GA RNAseq V2 data exists ... moving BCGSC GA dataset to bkp "
		        mv $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
	fi
	

	## there are a few cases where there is a V1 and a V2 RNAseq dataset at this point, 
	## and we want to only use V2 if it is available ...
	if [ -f $tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$curDate.tsv ]
	    then
		if [ -f $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina HiSeq RNAseq V2 data exists ... moving HiSeq RNAseq V1 dataset to bkp "
		        mv $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
		if [ -f $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina HiSeq RNAseq V2 data exists ... moving GA RNAseq V1 dataset to bkp "
		        mv $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
		if [ -f $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina HiSeq RNAseq V2 data exists ... moving BCGSC HiSeq dataset to bkp "
		        mv $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
		if [ -f $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina HiSeq RNAseq V2 data exists ... moving BCGSC GA dataset to bkp "
		        mv $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
	fi
	
	## also HiSeq RNASeq outranks GA RNASeq ... (and any data from BCGSC)
	if [ -f $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv ]
	    then
		if [ -f $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina HiSeq RNAseq V1 data exists ... moving GA RNAseq V1 dataset to bkp "
		        mv $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
		if [ -f $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina HiSeq RNAseq V1 data exists ... moving BCGSC HiSeq dataset to bkp "
		        mv $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
		if [ -f $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina HiSeq RNAseq V1 data exists ... moving BCGSC GA dataset to bkp "
		        mv $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
	fi
	
    done

echo " "
echo " fmp02B_L3 script is FINISHED !!! "
echo `date`
echo " "
