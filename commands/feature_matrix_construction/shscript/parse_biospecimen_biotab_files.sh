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

        rm -fr $TCGAFMP_DCC_REPOSITORIES/scratch/t?

        cd $TCGAFMP_DCC_REPOSITORIES/dcc-snapshot/public/tumor/$tumor/bcr/nationwidechildrens.org/bio/clin

        ## 07mar14 ... looking at files for LGG ...

        ## biospecimen_cqcf_lgg.txt file has 23 columns:
	##   1 bcr_patient_barcode
	##   2 consent_or_death_status
	##   3 country
	##   4 days_to_pathology_review
	##   5 days_to_sample_procurement
	##   6 digital_image_submitted
	##   7 ethnicity
	##   8 histological_type
	##   9 histological_type_other              
	##  10 history_of_neoadjuvant_treatment
	##  11 method_of_sample_procurement
	##  12 other_method_of_sample_procurement
	##  13 other_vessel_used
	##  14 path_confirm_diagnosis_matching
	##  15 path_confirm_report_attached
	##  16 path_confirm_tumor_necrosis_metrics
	##  17 path_confirm_tumor_nuclei_metrics
	##  18 race
	##  19 reason_path_confirm_diagnosis_not_matching
	##  20 sample_prescreened
	##  21 submitted_for_lce
	##  22 top_slide_submitted
	##  23 vessel_used

        ## biospecimen_slide_lgg.txt has 12 columns:
        ## --> as of 13may14, these files have 13 columns instead of 12:
	##   1 bcr_sample_barcode
	##   2 bcr_slide_barcode
	##   3 bcr_slide_uuid
        ##   4 is_derived_from_ffpe
	##   5 percent_lymphocyte_infiltration
	##   6 percent_monocyte_infiltration
	##   7 percent_necrosis
	##   8 percent_neutrophil_infiltration
	##   9 percent_normal_cells
	##  10 percent_stromal_cells
	##  11 percent_tumor_cells
	##  12 percent_tumor_nuclei
	##  13 section_location

        ## biospecimen_tumor_sample_lgg.txt file has 6 columns:
	##   1 bcr_patient_barcode
	##   2 bcr_sample_uuid
	##   3 tumor_necrosis_percent
	##   4 tumor_nuclei_percent
	##   5 tumor_weight
	##   6 vial_number

        rm -fr $TCGAFMP_DCC_REPOSITORIES/scratch/t?

        ## grab only bcr_patient_barcode, and days_to_sample_procurement
        cut -f 1,5 *bio.Level_2*/nationwidechildrens.org_biospecimen_cqcf*.txt         | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& $TCGAFMP_DCC_REPOSITORIES/scratch/t1

        ## grab everything except the bcr_slide barcode and uuid
        cut -f 1,4-  *bio.Level_2*/nationwidechildrens.org_biospecimen_slide*.txt        | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& $TCGAFMP_DCC_REPOSITORIES/scratch/t2

        ## grab everything except the bcr_sample_uuid
        cut -f 1,3-  *bio.Level_2*/nationwidechildrens.org_biospecimen_tumor_sample*.txt | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& $TCGAFMP_DCC_REPOSITORIES/scratch/t3

        python $TCGAFMP_ROOT_DIR/main/massageTSV.py $TCGAFMP_DCC_REPOSITORIES/scratch/t1 \
                $TCGAFMP_DATA_DIR/$tumor/aux/biospecimen_cqcf.forXmlMerge.tsv

        python $TCGAFMP_ROOT_DIR/main/massageTSV.py $TCGAFMP_DCC_REPOSITORIES/scratch/t2 \
                $TCGAFMP_DATA_DIR/$tumor/aux/biospecimen_slide.forXmlMerge.tsv

        python $TCGAFMP_ROOT_DIR/main/massageTSV.py $TCGAFMP_DCC_REPOSITORIES/scratch/t3 \
                $TCGAFMP_DATA_DIR/$tumor/aux/biospecimen_tumor_sample.forXmlMerge.tsv

        chmod g+w $TCGAFMP_DCC_REPOSITORIES/scratch/t?

    done

