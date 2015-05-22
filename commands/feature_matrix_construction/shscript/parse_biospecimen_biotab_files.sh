#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


for tumor in `cat $TCGAFMP_ROOT_DIR/config/tumor_list.txt`
    do

        echo " "
        echo " "
        echo " ************************************* "
        echo $tumor
        echo " "

        cd $TCGAFMP_DCC_REPOSITORIES/dcc-snapshot/public/tumor/$tumor/bcr/nationwidechildrens.org/bio/clin

        ## as of 14mar15 ... these files seem to have changed ...

        ## the biospecimen_cqcf_$tumor.txt file has either 29 [17 tumors] or 30 [18 tumors] columns ...
        ##     29 columns: brca, cesc, chol, hnsc, kirc, kirp, laml, lcml, lgg, lihc, lnnh, lusc, ov, pcpg, thym, ucs, uvm
        ##     30 columns: acc, blca, coad, dlbc, esca, gbm, kich, luad, meso, paad, prad, read, sarck, skcm, stad, tgct, thca, ucec
        ## --> as of 12apr15 ... some of these files now have 34 columns!!! but the ones we want are still #2 and #7

        ## the biospecimen_slide_$tumor.txt file has either 14 [17] or 15 [18] columns, with the same disease-type splits

        ## and the biospecimen_tumor_sample_$tumor.txt file has 6 [17] or 7 [18] columns, again with apparently the same split

        rm -fr $TCGAFMP_DCC_REPOSITORIES/scratch/t?

        ## grab only bcr_patient_barcode, and days_to_sample_procurement
        ## for the tumor types with 30 columns, we want #2 and #7
        head -1 *bio.Level_2*/nationwidechildrens.org_biospecimen_cqcf*.txt >& $TCGAFMP_DCC_REPOSITORIES/scratch/ta
        ~/scripts/transpose $TCGAFMP_DCC_REPOSITORIES/scratch/ta >& $TCGAFMP_DCC_REPOSITORIES/scratch/tb
        numLines=$(wc -l < "$TCGAFMP_DCC_REPOSITORIES/scratch/tb" )
        if [ $numLines -eq 30 ] || [ $numLines -eq 34 ]
            then
                cut -f 2,7 *bio.Level_2*/nationwidechildrens.org_biospecimen_cqcf*.txt         | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& $TCGAFMP_DCC_REPOSITORIES/scratch/t1
            else
                echo " ERROR ... unexpected number of columns in biospecimen_cqcf biotab file "
            fi


        ## grab everything except the bcr_slide_barcode, _uuid, and image_file_name
        ## for the tumor types with 14 columns, that means 1,5-
        ## and for the tumor types with 15 columns: 2,6-
        head -1 *bio.Level_2*/nationwidechildrens.org_biospecimen_slide*.txt >& $TCGAFMP_DCC_REPOSITORIES/scratch/tc
        ~/scripts/transpose $TCGAFMP_DCC_REPOSITORIES/scratch/tc >& $TCGAFMP_DCC_REPOSITORIES/scratch/td
        numLines=$(wc -l < "$TCGAFMP_DCC_REPOSITORIES/scratch/td" )
        if [ $numLines -eq 15 ]
            then
                cut -f 2,6-  *bio.Level_2*/nationwidechildrens.org_biospecimen_slide*.txt        | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& $TCGAFMP_DCC_REPOSITORIES/scratch/t2
            else
                echo " ERROR ... unexpected number of columns in biospecimen_slide biotab file "
            fi

        ## for the tumor types with 6 columns, we want: 1,3-5
        ## and for those with 7 columns, we want: 2,4-6
        head -1 *bio.Level_2*/nationwidechildrens.org_biospecimen_tumor_sample*.txt >& $TCGAFMP_DCC_REPOSITORIES/scratch/te
        ~/scripts/transpose $TCGAFMP_DCC_REPOSITORIES/scratch/te >& $TCGAFMP_DCC_REPOSITORIES/scratch/tf
        numLines=$(wc -l < "$TCGAFMP_DCC_REPOSITORIES/scratch/tf" )
        if [ $numLines -eq 7 ]
            then
                cut -f 2,4-6  *bio.Level_2*/nationwidechildrens.org_biospecimen_tumor_sample*.txt | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& $TCGAFMP_DCC_REPOSITORIES/scratch/t3
            else
                echo " ERROR ... unexpected number of columns in biospecimen_tumor_sample biotab file "
            fi

        python $TCGAFMP_ROOT_DIR/main/massageTSV.py $TCGAFMP_DCC_REPOSITORIES/scratch/t1 \
                $TCGAFMP_DATA_DIR/$tumor/aux/biospecimen_cqcf.forXmlMerge.tsv

        python $TCGAFMP_ROOT_DIR/main/massageTSV.py $TCGAFMP_DCC_REPOSITORIES/scratch/t2 \
                $TCGAFMP_DATA_DIR/$tumor/aux/biospecimen_slide.forXmlMerge.tsv

        python $TCGAFMP_ROOT_DIR/main/massageTSV.py $TCGAFMP_DCC_REPOSITORIES/scratch/t3 \
                $TCGAFMP_DATA_DIR/$tumor/aux/biospecimen_tumor_sample.forXmlMerge.tsv

        chmod g+w $TCGAFMP_DCC_REPOSITORIES/scratch/t?

    done



