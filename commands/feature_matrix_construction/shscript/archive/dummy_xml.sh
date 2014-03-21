#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH


## this script should be called with the following parameters:
##	date, eg '29jan13'
##	snapshot, either 'dcc-snapshot' (most recent) or, eg, 'dcc-snapshot-29jan13;
##	one or more tumor types, eg: 'prad thca skcm stad'
curDate=$1
snapshotName=$2
tumor=$3

if [ -z "$curDate" ]
    then
	echo " this script must be called with a date string of some kind, eg 28feb13 "
	exit
fi
if [ -z "$snapshotName" ]
    then
	echo " this script must be called with a specific snapshot-name, eg dcc-snapshot "
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
echo " *" $snapshotName
echo " *******************"

args=("$@")
for ((i=2; i<$#; i++))
    do
	tumor=${args[$i]}

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
	rm -fr forXmlMerge.log
	for f in `ls ../aux/*.forXmlMerge.tsv`
	    do
		echo "    " $f 
		echo "    " >> forXmlMerge.log
		rm -fr merge_temp?.???
		cp clinical.temp.tsv merge_temp1.tsv
		python $TCGAFMP_ROOT_DIR/main/add2clinTSV.py merge_temp1.tsv $f merge_temp2.tsv >> forXmlMerge.log
		if [ -f merge_temp2.tsv ]
		    then
			cp -f merge_temp2.tsv clinical.temp.tsv
			python $TCGAFMP_ROOT_DIR/main/quickLook.py clinical.temp.tsv | grep "Summary"
		    else
		        echo " "
			echo $f
			echo " "
			tail forXmlMerge.log
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



    done

echo " "
echo " dummy_xml script is FINISHED !!! "
date
echo " "

