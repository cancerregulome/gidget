
for tumor in `cat $TCGAFMP_ROOT_DIR/shscript/tumor_list.txt`
    do

        echo " "
        echo " "
        echo " ************************************* "
        echo $tumor
        echo " "

        rm -fr /titan/cancerregulome11/TCGA/repositories/scratch/t?

        ## cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$tumor/bcr/biotab/clin
        cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$tumor/bcr/nationwidechildrens.org/bio/clin

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
	##   1 bcr_sample_barcode
	##   2 bcr_slide_barcode
	##   3 bcr_slide_uuid
	##   4 percent_lymphocyte_infiltration
	##   5 percent_monocyte_infiltration
	##   6 percent_necrosis
	##   7 percent_neutrophil_infiltration
	##   8 percent_normal_cells
	##   9 percent_stromal_cells
	##  10 percent_tumor_cells
	##  11 percent_tumor_nuclei
	##  12 section_location

        ## biospecimen_tumor_sample_lgg.txt file has 6 columns:
	##   1 bcr_patient_barcode
	##   2 bcr_sample_uuid
	##   3 tumor_necrosis_percent
	##   4 tumor_nuclei_percent
	##   5 tumor_weight
	##   6 vial_number

        rm -fr /titan/cancerregulome11/TCGA/repositories/scratch/t?

        cut -f 1,5 *bio.Level_2*/nationwidechildrens.org_biospecimen_cqcf*.txt         | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& /titan/cancerregulome11/TCGA/repositories/scratch/t1

        cut -f 1,4-  *bio.Level_2*/nationwidechildrens.org_biospecimen_slide*.txt        | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& /titan/cancerregulome11/TCGA/repositories/scratch/t2

        cut -f 1,3-  *bio.Level_2*/nationwidechildrens.org_biospecimen_tumor_sample*.txt | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& /titan/cancerregulome11/TCGA/repositories/scratch/t3

        python $TCGAFMP_ROOT_DIR/main/massageTSV.py /titan/cancerregulome11/TCGA/repositories/scratch/t1 \
                /titan/cancerregulome14/TCGAfmp_outputs/$tumor/aux/biospecimen_cqcf.forXmlMerge.tsv

        python $TCGAFMP_ROOT_DIR/main/massageTSV.py /titan/cancerregulome11/TCGA/repositories/scratch/t2 \
                /titan/cancerregulome14/TCGAfmp_outputs/$tumor/aux/biospecimen_slide.forXmlMerge.tsv

        python $TCGAFMP_ROOT_DIR/main/massageTSV.py /titan/cancerregulome11/TCGA/repositories/scratch/t3 \
                /titan/cancerregulome14/TCGAfmp_outputs/$tumor/aux/biospecimen_tumor_sample.forXmlMerge.tsv

        chmod g+w /titan/cancerregulome11/TCGA/repositories/scratch/t?

    done

