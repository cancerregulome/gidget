#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


## this script should be called with the following parameters:
##      date, eg '12jul13' or 'test'
##      one tumor type, eg 'ucec'

WRONGARGS=1
if [[ $# != 3 ]] && [[ $# != 4 ]]
    then
        echo " Usage   : `basename $0` <curDate> <tumorType> <public/private>  [auxName] "
        echo " Example : `basename $0` 28oct13  brca  private  aux "
        echo " "
        echo " Note that the new auxName option at the end is optional and will default to simply aux "
        exit $WRONGARGS
fi

curDate=$1
tumor=$2
ppString=$3

if (( $# == 4 ))
    then
        auxName=$4
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
	echo " Tumor Type " $tumor
	date

	cd $curDate

        s=''
        if [ "$ppString" = 'private' ]
            then
	        s=$(<../$auxName/splitType.txt)
	        if [ -z "$s" ]
	            then
	                echo " no splitType specified "
	            else
		        echo " splitType is $s"
	        fi
        fi

        rm -fr filterFeat.log
        rm -fr final.addI.log
        rm -fr sampleType.split.log

	## for all jctmg tsv files ...
	for f in $tumor.newMerge.???.$curDate.jctmg.*tsv
	    do

		## remove the 'jctmg' and the 'newMerge' from the name and rename
		g=${f/.jctmg./.}
		k=${g/.newMerge./.}

		echo " "
                date
                echo " operating on intermediate file " $f

                ## delete scratch files that might have been left over from before ...
                rm -fr tmpf1.tsv tmpf2.tsv

                echo " adding indicator features ... "
                python $TCGAFMP_ROOT_DIR/main/addIndicators.py $f tmpf1a.tsv >> final.addI.log

                if [ "$ppString" = 'private' ]
                    then
                        echo " adding discrete features ... "
                        python $TCGAFMP_ROOT_DIR/main/addDiscreteFeat.py tmpf1a.tsv tmpf1.tsv ../$auxName/$tumor.addDiscreteFeat_List.txt >> final.addI.log
                fi

                echo " filtering features and samples ... "
                python $TCGAFMP_ROOT_DIR/main/filterTSVbyFeatList.py \
                            tmpf1.tsv tmpf2.tsv \
                            ../$auxName/$tumor.features.blacklist.loose.tsv  black loose \
                            ../$auxName/$tumor.features.blacklist.strict.tsv black strict \
                            ../$auxName/$tumor.features.whitelist.loose.tsv  white loose \
                            ../$auxName/$tumor.features.whitelist.strict.tsv white strict \
                            >> filterFeat.log

                echo " log-transform all GEXP and MIRN features "
                python $TCGAFMP_ROOT_DIR/main/logTransformTSV.py tmpf2.tsv tmpf2b.tsv GEXP MIRN

                python $TCGAFMP_ROOT_DIR/main/filterTSVbySampList.py \
                            tmpf2b.tsv $k \
                            $tumor.blacklist.samples.tsv black loose \
                            ../$auxName/$tumor.blacklist.loose.tsv  black loose \
                            ../$auxName/$tumor.blacklist.strict.tsv black strict \
                            ../$auxName/$tumor.whitelist.loose.tsv  white loose \
                            ../$auxName/$tumor.whitelist.strict.tsv white strict \
                            >> filterFeat.log

                echo " get summary information on this file ... "
                echo $k
		smry=${k/.tsv/.summary}
                python $TCGAFMP_ROOT_DIR/main/quickLook.py $k >& $smry

                echo " and finally split according to sampleType ... "
                python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py \
                        $k sampleType >> sampleType.split.log

                rm -fr tmpf1.tsv tmpf2.tsv
                date
                echo " "

	    done

	## now, for all tumor-only files
	for f in $tumor.???.$curDate.T?.tsv
	    do

		if [ -f $f ]
		    then

			h=${f/.tsv/.score.log}
			python $TCGAFMP_ROOT_DIR/main/scoreCatFeat.py \
			    --tsvFile $TCGAFMP_DATA_DIR/$tumor/$curDate/$f >& $h
	
			h=${f/.tsv/.split.log}
	
			if [ -z "$s" ]
			    then
				echo " "
			    else
				echo " "
                                echo " splitting feature matrix ... "
                                date
				echo "python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py $f $s >& $h "
				python $TCGAFMP_ROOT_DIR/main/splitTSVbyCat.py $f $s >& $h 
			fi

		fi


	    done


echo " "
echo " fmp10B_splitType script is FINISHED !!! "
echo `date`
echo " "

