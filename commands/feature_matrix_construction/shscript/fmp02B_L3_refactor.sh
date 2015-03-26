#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      date, eg '29jan13'
##      snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##      one or more tumor types, eg: 'prad,thca,skcm,stad'
##      a config file, eg: 'parse_tcga.config', relative to $TCGAFMP_ROOT_DIR/config

WRONGARGS=1
if [ $# != 4 ]
    then
        echo " Usage   : `basename $0` <curDate> <snapshotName> <tumorType> <config>"
        echo " Example : `basename $0` 28oct13  dcc-snapshot-28oct13  brca  parse_tcga.27_450k.config"
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
        rm -fr *__*.$curDate.tsv
        rm -fr *__*.$curDate.tsv.bkp

	## COPY-NUMBER
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config broad.mit.edu/genome_wide_snp_6/snp/ $tumor $curDate $snapshotName           >& level3.broad.snp_6.$curDate.log 

	## MICRO-RNA (both GA and HiSeq)
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config bcgsc.ca/illuminaga_mirnaseq/mirnaseq/ $tumor $curDate $snapshotName                >& level3.bcgsc.ga_mirn.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq/ $tumor $curDate $snapshotName             >& level3.bcgsc.hiseq_mirn.$curDate.log 

        ## for f in *__mirnaseq*tsv
        ##     do
        ##         $TCGAFMP_ROOT_DIR/shscript/fmp00B_hackBarcodes.sh $f
        ##     done

	## MESSENGER-RNA (many different platforms)
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config bcgsc.ca/illuminaga_rnaseq/rnaseq/ $tumor $curDate $snapshotName                    >& level3.bcgsc.ga_rnaseq.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config bcgsc.ca/illuminahiseq_rnaseq/rnaseq/ $tumor $curDate $snapshotName                 >& level3.bcgsc.hiseq_rnaseq.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/agilentg4502a_07_1/transcriptome/ $tumor $curDate $snapshotName             >& level3.unc.agil_07_1.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/agilentg4502a_07_2/transcriptome/ $tumor $curDate $snapshotName             >& level3.unc.agil_07_2.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/agilentg4502a_07_3/transcriptome/ $tumor $curDate $snapshotName             >& level3.unc.agil_07_3.$curDate.log 
     ## python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/illuminaga_rnaseq/rnaseq/ $tumor $curDate $snapshotName                     >& level3.unc.ga_rnaseq.$curDate.log 
     ## python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/illuminahiseq_rnaseq/rnaseq/ $tumor $curDate $snapshotName                  >& level3.unc.hiseq_rnaseq.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/illuminaga_rnaseqv2/rnaseqv2/ $tumor $curDate $snapshotName                 >& level3.unc.ga_rnaseqv2.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config unc.edu/illuminahiseq_rnaseqv2/rnaseqv2/ $tumor $curDate $snapshotName              >& level3.unc.hiseq_rnaseqv2.$curDate.log 

	## METHYLATION (both 27k and 450k platforms)
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config jhu-usc.edu/humanmethylation27/methylation/ $tumor $curDate $snapshotName           >& level3.jhu-usc.meth27.$curDate.log 
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config jhu-usc.edu/humanmethylation450/methylation/ $tumor $curDate $snapshotName          >& level3.jhu-usc.meth450.$curDate.log 

	## RPPA
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config mdanderson.org/mda_rppa_core/protein_exp/ $tumor $curDate $snapshotName             >& level3.mda.rppa.$curDate.log 

	## MICRO-SATELLITE INSTABILITY
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config nationwidechildrens.org/microsat_i/fragment_analysis/ $tumor $curDate $snapshotName >& level3.nwc.microsat_i.$curDate.log 

	## now we need to move any 'obsolete' expression datasets out of the way ...
	rm -fr $tumor.*.$curDate.tsv.bkp

        ## cleaning this up a bit ...
        ## we want to check for all of the various types of RNAseq data we might have ...

        haveUNC_HiSeq_V2=false
        haveUNC_GA_V2=false
        haveUNC_HiSeq_V1=false
        haveUNC_GA_V1=false
        haveBCG_HiSeq=false
        haveBCG_GA=false

	if [ -f $tumor.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$curDate.tsv ] ; then haveUNC_HiSeq_V2=true ; fi
	if [ -f $tumor.unc.edu__illuminaga_rnaseqv2__rnaseqv2.$curDate.tsv ];     then haveUNC_GA_V2=true ;    fi
	if [ -f $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv ] ;     then haveUNC_HiSeq_V1=true ; fi
	if [ -f $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv ] ;        then haveUNC_GA_V1=true ;    fi
	if [ -f $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv ] ;    then haveBCG_HiSeq=true ;    fi
	if [ -f $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv ] ;       then haveBCG_GA=true ;       fi

        echo " have these RNAseq data types: " $haveUNC_HiSeq_V2 $haveUNC_GA_V2 $haveUNC_HiSeq_V1 $haveUNC_GA_V1 $haveBCG_HiSeq $haveBCG_GA

        ## if we have data from BCGSC ~and~ from UNC, then we disregard the BCGSC data entirely ...
        if [[ $haveUNC_HiSeq_V2 == true || $haveUNC_GA_V2 == true || $haveUNC_HiSeq_V1 == true || $haveUNC_GA_V1 == true ]]
            then
                if [[ $haveBCG_HiSeq == true ]]
                    then
                        echo " WARNING: deprecating BCGSC HiSeq RNAseq data in favor of UNC RNAseq data "
                        mv $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv $tumor.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$curDate.tsv.bkp
                fi
                if [[ $haveBCG_GA == true ]]
                    then
                        echo " WARNING: deprecating BCGSC GA RNAseq data in favor of UNC RNAseq data "
                        mv $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv $tumor.bcgsc.ca__illuminaga_rnaseq__rnaseq.$curDate.tsv.bkp
                fi
        fi

        ## if we have UNC HiSeq data from both V1 and V2 pipelines, deprecate V1
        if [[ $haveUNC_HiSeq_v2 == true && $haveUNC_HiSeq_V1 == true ]]
            then
                echo " WARNING: deprecating UNC HiSeq RNAseq V1 data in favor of V2 data "
                mv $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv $tumor.unc.edu__illuminahiseq_rnaseq__rnaseq.$curDate.tsv.bkp
        fi

        ## if we have UNC GA data from both V1 and V2 pipelines, deprecate V1
        if [[ $haveUNC_GA_v2 == true && $haveUNC_GA_V1 == true ]]
            then
                echo " WARNING: deprecating UNC GA RNAseq V1 data in favor of V2 data "
                mv $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv $tumor.unc.edu__illuminaga_rnaseq__rnaseq.$curDate.tsv.bkp
        fi

    done

echo " "
echo " fmp02B_L3 script is FINISHED !!! "
echo `date`
echo " "

