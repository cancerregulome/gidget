#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##	date, eg '29jan13'
##	snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##	one or more tumor types, eg: 'prad,thca,skcm,stad'
##	config, eg 'parse_tcga.config', relative to $TCGAFMP_ROOT_DIR/config

WRONGARGS=1
if [[ $# != 5 ]] && [[ $# != 7 ]]
    then
        echo " Usage   : `basename $0` <curDate> <snapshotName> <tumorType> <config> <public/private> [auxName] [ignoreAM=yes/no] "
        echo " Example : `basename $0` 28oct13  dcc-snapshot-28oct13  brca  parse_tcga.27_450k.config  private  aux  no "
        echo " "
        echo " Note that the new auxName option at the end is optional and will default to simply aux "
        echo " Note that the ignoreAM (ignore annotations-manager) option is also optional and will default to no "
        echo " However, if you want to use either of these two optional command-line arguments, you MUST use BOTH "
        exit $WRONGARGS
fi

curDate=$1
snapshotName=$2
tumors=$(echo $3 | tr "," "\n")
config=$4
ppString=$5

if (( $# == 7 ))
    then
        auxName=$6
        ignoreAM=$7
    else
        auxName=aux
        ignoreAM=no
fi

echo " "
echo " "
echo " *******************"
echo `date`
echo " * run id ........... " $curDate 
echo " * snapshot name .... " $snapshotName
echo " * tumor ............ " $tumor
echo " * config ........... " $config
echo " * public/private ... " $ppString
echo " * aux dir .......... " $auxName
echo " *******************"

args=("$@")
for tumor in $tumors
	do 
	cd $TCGAFMP_DATA_DIR/$tumor

	echo " "
	echo " "
	echo " Tumor Type " $tumor
	date

	if [ ! -d $curDate ]
	    then
		mkdir $curDate
	fi

	cd $curDate
        pwd

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## first we parse the clinical XML files ...
        echo " parsing clinical XML files ... "
	rm -fr parse_all_xml.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/parse_tcga.py $TCGAFMP_ROOT_DIR/config/$config clinical/ $tumor $curDate $snapshotName >& parse_all_xml.$curDate.log

	## if we didn't get anything out of here, then skip to the next tumor type ...
	if [ ! -f $tumor.clinical.$curDate.tsv ]
	    then
		echo " NO clinical xml data available ... skipping to next tumor type "
	        continue
	fi

        ## make a copy of this first file, just in case we need to check some things ...
        cp $tumor.clinical.$curDate.tsv $tumor.clinical.$curDate.tsv_fromXML_only

	rm -fr tmp.sort
	sort $tumor.clinical.$curDate.tsv >& tmp.sort
	mv -f tmp.sort $tumor.clinical.$curDate.tsv
        ## $TCGAFMP_ROOT_DIR/shscript/fmp00B_hackBarcodes.sh $tumor.clinical.$curDate.tsv

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## then we parse the Firehose analyses output files ...
        echo " parsing Firehose analyses outputs ... "
	rm -fr parseFirehose.$curDate.log
	rm -fr gdac.broadinstitute.org_*.tsv
        rm -fr gdac.broadinstitute.org_*.txt
	python $TCGAFMP_ROOT_DIR/main/parseFirehose.py $tumor $ppString $auxName >& parseFirehose.$curDate.log

        ## the patients.counts_and_rates files do not differ across multiple subsets
        ## so we can concatenate all of these ...
        echo " creating new MutSig counts and rates file in aux directory " $auxName
        rm -fr ../$auxName/MutSigCV.patients.counts_and_rates.forXmlMerge.tsv
        rm -fr ../$auxName/MutSig.patients.counts_and_rates.forXmlMerge.tsv
        cat gdac.broadinstitute.org_*counts*rates*tsv | sort | uniq >& \
            ../$auxName/MutSig.patients.counts_and_rates.forXmlMerge.tsv
        rm -fr gdac.broadinstitute.org_*counts*rates*tsv

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## here we want to try to merge Firehose-based outputs into the XML-based clinical matrix
	## that was built using parse_all_xml ...
	## ( yes, I know this is ugly )

	## NOTE: one thing that is good that is happening somewhat accidentally is that if 
	## a particular Firehose output is not available from the most recent run (eg almost
	## all of the MutSig outputs do not exist in the 20120623 run), then this will 
	## automatically grab the next most recent file if such a file is available ...

	## also, I could not figure out how to avoid getting these kinds of messages when
	## a file doesn't exist:
	##	ls: gdac.broadinst*mRNAseq_*Clust*Cons*tsv: No such file or directory

	rm -fr clinical.temp.tsv
	cp $tumor.clinical.$curDate.tsv clinical.temp.tsv
	python $TCGAFMP_ROOT_DIR/main/quickLook.py clinical.temp.tsv | grep "Summary"

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## grab ALL gdac.broad*.tsv files and merge them in ...
        rm -fr gdac.broad.merge.log
        for f in `ls -1d gdac.broad*.tsv`
            do
		echo "    " $f
                ## $TCGAFMP_ROOT_DIR/shscript/fmp00B_hackBarcodes.sh $f
                echo " " >> gdac.broad.merge.log
                echo $f >> gdac.broad.merge.log
                echo " " >> gdac.broad.merge.log
		rm -fr merge_temp?.???
		cp clinical.temp.tsv merge_temp1.tsv
		python $TCGAFMP_ROOT_DIR/main/add2clinTSV.py merge_temp1.tsv $f merge_temp2.tsv >> gdac.broad.merge.log
		if [ -f merge_temp2.tsv ]
		    then
			cp -f merge_temp2.tsv clinical.temp.tsv
			python $TCGAFMP_ROOT_DIR/main/quickLook.py clinical.temp.tsv | grep "Summary"
		    else
		        echo " "
			echo $f
			echo " "
			tail merge_temp2.log
			echo " "
		fi
            done
	
	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## now we're going to merge in any 'extra' files that contain 'forXmlMerge' in the 
	## filename ...
	rm -fr forXmlMerge.log
        if [ "$ppString" = 'private' ]
            then
                echo " incorporating forXmlMerge files from specified aux directory ... " $auxName
        	for f in `ls ../$auxName/*.forXmlMerge.tsv`
        	    do
        		echo "    " $f 
        		echo "    " >> forXmlMerge.log
        		echo "    " >> forXmlMerge.log
                        echo $f >> forXmlMerge.log
        		rm -fr merge_temp?.???
        		cp clinical.temp.tsv merge_temp1.tsv
        		python $TCGAFMP_ROOT_DIR/main/add2clinTSV.py merge_temp1.tsv $f merge_temp2.tsv >> forXmlMerge.log
        		if [ -f merge_temp2.tsv ]
        		    then
                                echo " SUCCESSFUL merge " >> forXmlMerge.log
        			cp -f merge_temp2.tsv clinical.temp.tsv
        			python $TCGAFMP_ROOT_DIR/main/quickLook.py clinical.temp.tsv | grep "Summary"
        		    else
                                echo " ERROR in merge ??? " >> forXmlMerge.log
        		        echo " "
        			echo $f
        			echo " "
        			tail forXmlMerge.log
        			echo " "
        		fi
        	    done
                else
                    echo " NOT incorporating forXmlMerge files from aux directory ... "
            fi

	rm -fr merge_temp?.tsv
	rm -fr merge_temp?.log

        cp clinical.temp.tsv $tumor.clinical.$curDate.tsv

        ## if the tumor type is CESC, then call the new code ...
        if [ "$tumor" == "cesc" ]
            then
                echo " calling special CESC-specific reParseClin_CESC.py ... "
                python $TCGAFMP_ROOT_DIR/main/reParseClin_CESC.py $tumor $curDate ../$auxName/reParse-feature-list.txt
                mv $tumor.clinical.$curDate.tsv $tumor.clinical.$curDate.old.tsv
                cp $tumor.clinical.$curDate.cesc.tsv $tumor.clinical.$curDate.tsv
                cp $tumor.clinical.$curDate.tsv clinical.temp.tsv
                head $tumor.clinical.$curDate.tsv | cut -f1-10
            else
                echo " NOT calling the CESC-specific reParseClin_CESC.py ... "
        fi

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## here we "clean up" the clinical file and also "flip" it
	## note that the "cleaning up" was so-named originally because it removed non-
	## informative features, but it is also adding binary indicator features and so
	## the output matrix is actually typically quite a bit larger than the input ...
	rm -fr cleanClin.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/cleanClinTSV.py clinical.temp.tsv cleanClin.$curDate.tsv $ppString $auxName >& cleanClin.$curDate.log
	## rm -fr clinical.temp.tsv

	## but it still needs some cleaning up ;-)
	## --> get rid of the I() indicator features for Gistic features ...
	rm -fr x? x??
	rm -fr finalClin.$tumor.$curDate.tsv
	grep -v ":I(" cleanClin.$curDate.flipNumeric.tsv >& x1
	grep    ":I(" cleanClin.$curDate.flipNumeric.tsv >& x2
	grep -v "Gistic" x2 | grep -v "batch_number" >& x2a
	cat x1 x2a >& finalClin.$tumor.$curDate.tsv
	rm -fr x? x??

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## NEW as of 01 nov 2012 ... get the blacklist of patients and samples from the TCGA
	## annotations manager
        if [ "$ignoreAM" = 'no' ]
            then
	        $TCGAFMP_ROOT_DIR/shscript/Item_Blacklist.sh $tumor $TCGAFMP_ROOT_DIR/shscript/blacklist.spec >& Item_Blacklist.$curDate.log
            else
                rm -fr $tumor.blacklist.samples.tsv
            fi
	rm -fr cTmp.tsv
	cp finalClin.$tumor.$curDate.tsv cTmp.tsv
	rm -fr filterSamp.clin.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
		cTmp.tsv finalClin.$tumor.$curDate.tsv \
		$tumor.blacklist.samples.tsv black loose \
                ../$auxName/$tumor.blacklist.loose.tsv black loose \
                ../$auxName/$tumor.whitelist.loose.tsv white loose \
                ../$auxName/$tumor.whitelist.strict.tsv white strict \
                >& filterSamp.clin.$curDate.log

        ## and now run pairwise on this finalClin feature matrix ...
        ## NOTE that this gets run in the background !!!
        #### nohup python $TCGAFMP_ROOT_DIR/main/run_pwRK3.py \
        nohup python $TCGAFMP_ROOT_DIR/main/run-pairwise-v2.py \
                --pvalue 2. --all --forRE \
                --tsvFile $TCGAFMP_DATA_DIR/$tumor/$curDate/finalClin.$tumor.$curDate.tsv &

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## here we are building a subset of the clinical data based on the 'finalClin' file
	rm -fr t? t??
	rm -fr vitalStats.$tumor.$curDate.tsv

	head -1 finalClin.$tumor.$curDate.tsv >& t1
	grep ":disease_code:" finalClin.$tumor.$curDate.tsv >& t2a
	grep ":vital_status:" finalClin.$tumor.$curDate.tsv >& t2
	grep ":age_at_initial_pathologic_diagnosis:" finalClin.$tumor.$curDate.tsv >& t3
	grep ":days_to_birth:" finalClin.$tumor.$curDate.tsv >& t4
	grep ":gender:" finalClin.$tumor.$curDate.tsv >& t5
	grep ":race:" finalClin.$tumor.$curDate.tsv >& t6
	grep ":ethnicity:" finalClin.$tumor.$curDate.tsv >& t7
	grep ":year_of_initial_pathologic_diagnosis:" finalClin.$tumor.$curDate.tsv >& t8
	grep ":days_to_last_followup:" finalClin.$tumor.$curDate.tsv >& t9
	grep ":days_to_last_known_alive:" finalClin.$tumor.$curDate.tsv >& t9b
	grep ":days_to_death:" finalClin.$tumor.$curDate.tsv >& t10
	grep ":person_neoplasm_cancer_status:" finalClin.$tumor.$curDate.tsv >& t11
	grep ":tumor_stage:" finalClin.$tumor.$curDate.tsv >& t12
	grep ":residual_tumor:" finalClin.$tumor.$curDate.tsv >& t13
	grep ":primary_tumor_pathologic_spread:" finalClin.$tumor.$curDate.tsv >& t14
	grep ":distant_metastasis_pathologic_spread:" finalClin.$tumor.$curDate.tsv >& t16
	grep ":lymph_node_examined_count:" finalClin.$tumor.$curDate.tsv >& t29
	grep ":number_of_lymphnodes_positive_by_he:" finalClin.$tumor.$curDate.tsv >& t15
	grep ":primary_lymph_node_presentation_assessment:" finalClin.$tumor.$curDate.tsv >& t30
	grep ":prior_diagnosis:" finalClin.$tumor.$curDate.tsv >& t17
	grep ":pretreatment_history:" finalClin.$tumor.$curDate.tsv >& t18
	grep ":new_tumor_event_after_initial_treatment:" finalClin.$tumor.$curDate.tsv >& t19
	grep ":days_to_new_tumor_event_after_initial_treatment:" finalClin.$tumor.$curDate.tsv >& t20
	grep ":additional_surgery_locoregional_procedure:" finalClin.$tumor.$curDate.tsv >& t21
	grep ":additional_surgery_metastatic_procedure:" finalClin.$tumor.$curDate.tsv >& t22
	grep ":days_to_additional_surgery_locoregional_procedure:" finalClin.$tumor.$curDate.tsv >& t23
	grep ":days_to_additional_surgery_metastatic_procedure" finalClin.$tumor.$curDate.tsv >& t24
	grep ":targeted_molecular_therapy:" finalClin.$tumor.$curDate.tsv >& t25
	grep ":radiation_therapy:" finalClin.$tumor.$curDate.tsv >& t26
	grep ":additional_radiation_therapy:" finalClin.$tumor.$curDate.tsv >& t27
	grep ":additional_pharmaceutical_therapy:" finalClin.$tumor.$curDate.tsv >& t28
	grep ":karnofsky_performance_score:" finalClin.$tumor.$curDate.tsv >& t31
	cat t1 t2a t2 t3 t4 t5 t6 t7 t8 t9 t9b t10 t11 t12 t13 t14 t15 t16 t17 t18 t19 t20 t21 t22 t23 t24 t25 t26 t27 t28 t29 t30 t31 >& vitalStats.$tumor.$curDate.tsv
	rm -fr t? t??

	done

echo " "
echo " fmp01B_xml_refactor script is FINISHED !!! "
echo `date`
echo " "

