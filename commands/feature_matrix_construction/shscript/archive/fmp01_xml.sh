#!/bin/bash

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
	echo " Tumor Type " $tumor
	date

	if [ ! -d $curDate ]
	    then
		mkdir $curDate
	fi

	cd $curDate

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## first we parse the clinical XML files ...
	rm -fr parse_all_xml.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/parse_all_xml.py $tumor clinical.$curDate $snapshotName >& parse_all_xml.$curDate.log

	## if we didn't get anything out of here, then skip to the next tumor type ...
	if [ ! -f $tumor.clinical.$curDate.tsv ]
	    then
		echo " NO clinical xml data available ... skipping to next tumor type "
	        continue
	fi

	rm -fr tmp.sort
	sort $tumor.clinical.$curDate.tsv >& tmp.sort
	mv -f tmp.sort $tumor.clinical.$curDate.tsv

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## then we parse the Firehose analyses output files ...
	rm -fr parseFirehose.$curDate.log
	rm -fr gdac.broadinstitute.org_*.tsv
	python $TCGAFMP_ROOT_DIR/main/parseFirehose.py $tumor >& parseFirehose.$curDate.log

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

	## FIXME: the stuff below could probably be replaced with a single block
	## that handles all gdac.broad*.tsv files that exist in this directory ...
	
	f=`ls -1d gdac.broad*all_lesions.tsv | tail -1`
	if [ -f $f ] 
	    then
		echo "    " $f
		rm -fr merge_temp?.???
		cp clinical.temp.tsv merge_temp1.tsv
		python $TCGAFMP_ROOT_DIR/main/add2clinTSV.py merge_temp1.tsv $f merge_temp2.tsv >& merge_temp2.log
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
	fi
	
	f=`ls -1d gdac.broad*broad_values_by_arm.tsv | tail -1`
	if [ -f $f ] 
	    then
		echo "    " $f 
		rm -fr merge_temp?.???
		cp clinical.temp.tsv merge_temp1.tsv
		python $TCGAFMP_ROOT_DIR/main/add2clinTSV.py merge_temp1.tsv $f merge_temp2.tsv >& merge_temp2.log
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
	fi
	
	for f in `ls -1d gdac.broad*Clustering_CNMF*tsv`
	    do
		echo "    " $f 
		rm -fr merge_temp?.???
		cp clinical.temp.tsv merge_temp1.tsv
		python $TCGAFMP_ROOT_DIR/main/add2clinTSV.py merge_temp1.tsv $f merge_temp2.tsv >& merge_temp2.log
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
	
	for f in `ls -1d gdac.broad*Clustering_Consensus*tsv`
	    do
		echo "    " $f 
		rm -fr merge_temp?.???
		cp clinical.temp.tsv merge_temp1.tsv
		python $TCGAFMP_ROOT_DIR/main/add2clinTSV.py merge_temp1.tsv $f merge_temp2.tsv >& merge_temp2.log
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
	
	f=`ls -1d gdac.broad*Mut*Sig*counts*rates*tsv | tail -1`
	if [ -f $f ] 
	    then
		echo "    " $f 
		rm -fr merge_temp?.???
		cp clinical.temp.tsv merge_temp1.tsv
		python $TCGAFMP_ROOT_DIR/main/add2clinTSV.py merge_temp1.tsv $f merge_temp2.tsv >& merge_temp2.log
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
	fi

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## now we're going to merge in any 'extra' files that contain 'forXmlMerge' in the 
	## filename ...
	for f in `ls ../aux/*.forXmlMerge.tsv`
	    do
		echo "    " $f 
		rm -fr merge_temp?.???
		cp clinical.temp.tsv merge_temp1.tsv
		python $TCGAFMP_ROOT_DIR/main/add2clinTSV.py merge_temp1.tsv $f merge_temp2.tsv >& merge_temp2.log
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

	rm -fr merge_temp?.tsv
	rm -fr merge_temp?.log

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## here we "clean up" the clinical file and also "flip" it
	## note that the "cleaning up" was so-named originally because it removed non-
	## informative features, but it is also adding binary indicator features and so
	## the output matrix is actually typically quite a bit larger than the input ...
	rm -fr cleanClin.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/cleanClinTSV.py clinical.temp.tsv cleanClin.$curDate.tsv >& cleanClin.$curDate.log
	rm -fr clinical.temp.tsv

	## but it still needs some cleaning up ;-)
	## --> get rid of the I() indicator features for Gistic features ...
	rm -fr x? x??
	grep -v ":I(" cleanClin.$curDate.flipNumeric.tsv >& x1
	grep    ":I(" cleanClin.$curDate.flipNumeric.tsv >& x2
	grep -v "Gistic" x2 | grep -v "batch_number" >& x2a
	cat x1 x2a >& finalClin.$tumor.$curDate.tsv
	rm -fr x? x??

	## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	## NEW as of 01 nov 2012 ... get the blacklist of patients and samples from the TCGA
	## annotations manager
	$TCGAFMP_ROOT_DIR/shscript/Item_Blacklist.sh $tumor $TCGAFMP_ROOT_DIR/shscript/blacklist.spec
	#### cd /users/sreynold/code/AnnotM/
	#### ./Item_Blacklist.sh $tumor blacklist
	cp finalClin.$tumor.$curDate.tsv cTmp.tsv
	rm -fr filterSamp.clin.$curDate.log
	python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py cTmp.tsv $tumor.blacklist.samples.tsv \
		black finalClin.$tumor.$curDate.tsv >& filterSamp.clin.$curDate.log
	rm -fr cTmp.tsv

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
	cat t1 t2a t2 t3 t4 t5 t6 t7 t8 t9 t10 t11 t12 t13 t14 t15 t16 t17 t18 t19 t20 t21 t22 t23 t24 t25 t26 t27 t28 t29 t30 t31 >& vitalStats.$tumor.$curDate.tsv
	rm -fr t? t??

    done

echo " "
echo " fmp01_xml script is FINISHED !!! "
date
echo " "

