#!/bin/bash

## NOTE: only the SNP data processing is sent to run in the background ... 
## otherwise this all runs single-threaded ... (and somewhat inefficiently)

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH


## this script should be called with a current date string such as 14jan13 (ddmmmyy)
curDate=$1
snapshotName=$2

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

if [ -z "$snapshotName" ]
    then
        echo " using default dcc-snapshot "
    else
        echo " using this specific snapshot: " $snapshotName
fi

## for tumor in blca brca cesc cntl coad dlbc esca gbm hnsc kich kirc kirp laml lcll lgg lihc lnnh luad lusc ov paad prad read sarc skcm stad thca ucec
for tumor in skcm stad thca ucec

    do

	cd $TCGAFMP_DATA_DIR/$tumor

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
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate broad.mit.edu/genome_wide_snp_6/snp $tumor $snapshotName                  >& level3.broad.snp_6.$curDate.log &
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate bcgsc.ca/illuminaga_mirnaseq/mirnaseq $tumor $snapshotName                >& level3.bcgsc.ga_mirn.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate bcgsc.ca/illuminaga_rnaseq/rnaseq $tumor $snapshotName                    >& level3.bcgsc.ga_rnaseq.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq $tumor $snapshotName             >& level3.bcgsc.hiseq_mirn.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate bcgsc.ca/illuminahiseq_rnaseq/rnaseq $tumor $snapshotName                 >& level3.bcgsc.hiseq_rnaseq.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate genome.wustl.edu/genome_wide_snp_6/snp $tumor $snapshotName               >& level3.wustl.snp_6.$curDate.log &
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate jhu-usc.edu/humanmethylation27/methylation $tumor $snapshotName           >& level3.jhu-usc.meth27.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate jhu-usc.edu/humanmethylation450/methylation $tumor $snapshotName          >& level3.jhu-usc.meth450.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate mdanderson.org/mda_rppa_core/protein_exp $tumor $snapshotName             >& level3.mda.rppa.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate nationwidechildrens.org/microsat_i/fragment_analysis $tumor $snapshotName >& level3.nwc.microsat_i.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate unc.edu/agilentg4502a_07_1/transcriptome $tumor $snapshotName             >& level3.unc.agil_07_1.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate unc.edu/agilentg4502a_07_2/transcriptome $tumor $snapshotName             >& level3.unc.agil_07_2.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate unc.edu/agilentg4502a_07_3/transcriptome $tumor $snapshotName             >& level3.unc.agil_07_3.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate unc.edu/illuminaga_rnaseq/rnaseq $tumor $snapshotName                     >& level3.unc.ga_rnaseq.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate unc.edu/illuminahiseq_rnaseq/rnaseq $tumor $snapshotName                  >& level3.unc.hiseq_rnaseq.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/new_Level3_matrix.py $curDate unc.edu/illuminahiseq_rnaseqv2/rnaseqv2 $tumor $snapshotName              >& level3.unc.hiseq_rnaseqv2.$curDate.log 

	## there are a few cases where there is a V1 and a V2 RNAseq dataset at this point, 
	## and we want to only use V2 if it is available ...
	rm -fr $tumor.*.$curDate.tsv.bkp
	if [ -f $tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$curDate.tsv ]
	    then
		if [ -f $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv ]
		    then
			echo " Illumina HiSeq RNAseq V2 data exists ... moving RNAseq V1 dataset to bkp "
		        mv $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv \
			   $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv.bkp
		fi
	fi
	
    done

echo " "
echo " fmp02_L3 script is FINISHED !!! "
date
echo " "

