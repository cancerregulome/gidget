
for tumor in acc blca brca cesc cntl coad dlbc esca gbm hnsc kich kirc kirp laml lgg lihc luad lusc meso ov paad pcpg prad read sarc skcm stad tgct thca ucs ucec
    do

        echo " "
        echo " "
        echo " ************************************* "
        echo $tumor
        echo " "

        rm -fr ~/scratch/t?

        cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$tumor/bcr/biotab/clin

        ## NOTEs ...
        ## no biospecimen_cqcf file for thca (?)
        ## no biospecimen_slide file for laml (?)
        ## no biospecimen_tumor_sample file for gbm, laml, ov (?)

        ## 27jun13 ... looking at files in detail ... for STAD ...

        ## biospecimen_cqcf_stad.txt file has 344 lines x 26 columns
        ##     --> none of these actually seem interesting or relevant ???
        ##              --> so I will NOT process these files anymore ...
        ##
	##	0       bcr_patient_barcode                             :       TCGA-B7-5816
	##	1       b_cell_tumor_slide_submitted                    :       [Not Available]
	##	2       country                                         :       Russia
	##	3       cytogenetic_report_submitted                    :       [Not Available]
	##	4       days_to_pathology_review                        :       [Completed]
	##	5       days_to_sample_procurement                      :       [Completed]
	##	6       differential_report_submitted                   :       [Not Available]
	##	7       digital_image_submitted                         :       NO
	##	8       ffpe_tumor_slide_submitted                      :       [Not Available]
	##	9       hiv_positive_status                             :       [Not Available]
	##	10      maximum_tumor_dimension                         :       [Not Available]
	##	11      method_of_sample_procurement                    :       Surgical Resection
	##	12      other_method_of_sample_procurement              :       [Not Available]
	##	13      other_vessel_used                               :       [Not Available]
	##	14      path_confirm_diagnosis_matching                 :       YES
	##	15      path_confirm_report_attached                    :       YES
	##	16      path_confirm_tumor_necrosis_metrics             :       YES
	##	17      path_confirm_tumor_nuclei_metrics               :       YES
	##	18      percent_myeloblasts_for_submitted_specimen      :       [Not Available]
	##	19      reason_path_confirm_diagnosis_not_matching      :       [Not Available]
	##	20      sample_prescreened                              :       YES
	##	21      submitted_for_lce                               :       [Not Available]
	##	22      t_cell_tumor_slide_submitted                    :       [Not Available]
	##	23      top_slide_submitted                             :       YES
	##	24      total_cells_submitted                           :       [Not Available]
	##	25      vessel_used                                     :       Cryomold

        ## biospecimen_slide_stad.txt file has 738 lines x 16 columns
	##	0       bcr_sample_barcode                              :       TCGA-B7-5816-01A
	##	1       bcr_slide_barcode                               :       TCGA-B7-5816-01A-01-BS1
	##	2       bcr_slide_uuid                                  :       842d5f43-6fda-4eb0-be82-8b3531ffcf73
	##	3       number_proliferating_cells                      :       [Not Available]
	##	4       percent_eosinophil_infiltration                 :       [Not Available]
	##	5       percent_granulocyte_infiltration                :       [Not Available]
	##	6       percent_inflam_infiltration                     :       [Not Available]
	##	7       percent_lymphocyte_infiltration                 :       0
	##	8       percent_monocyte_infiltration                   :       0
	##	9       percent_necrosis                                :       15
	##	10      percent_neutrophil_infiltration                 :       0
	##	11      percent_normal_cells                            :       0
	##	12      percent_stromal_cells                           :       30
	##	13      percent_tumor_cells                             :       55
	##	14      percent_tumor_nuclei                            :       70
	##	15      section_location                                :       TOP

        ## biospecimen_tumor_sample_stad.txt file has 325 lines x 7 columns
	##	0       bcr_patient_barcode     :       TCGA-B7-5816
	##	1       bcr_sample_uuid         :       1b4b19c1-75a6-4434-831e-adce44c54eb5
	##	2       tumor_necrosis_percent  :       30
	##	3       tumor_nuclei_percent    :       70
	##	4       tumor_pathology         :       null
	##	5       tumor_weight            :       360
	##	6       vial_number             :       1


        ## cut -f 1- biospecimen_cqcf*.txt       | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& ~/scratch/t1
        cut -f 1,4- biospecimen_slide*.txt       | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& ~/scratch/t2
        cut -f 1,3- biospecimen_tumor_sample*.txt | sort | sed -e '1,$s/\[Not Available\]/NA/g' | sed -e '1,$s/\[Not Reported\]/NA/g' | sed -e '1,$s/\[Not Applicable\]/NA/g' | sed -e '1,$s/null/NA/g' >& ~/scratch/t3

        ## python /users/sreynold/to_be_checked_in/TCGAfmp/main/massageTSV.py ~/scratch/t1 \
        ##         /titan/cancerregulome14/TCGAfmp_outputs/$tumor/aux/biospecimen_cqcf.forXmlMerge.tsv

        python /users/sreynold/to_be_checked_in/TCGAfmp/main/massageTSV.py ~/scratch/t2 \
                /titan/cancerregulome14/TCGAfmp_outputs/$tumor/aux/biospecimen_slide.forXmlMerge.tsv

        python /users/sreynold/to_be_checked_in/TCGAfmp/main/massageTSV.py ~/scratch/t3 \
                /titan/cancerregulome14/TCGAfmp_outputs/$tumor/aux/biospecimen_tumor_sample.forXmlMerge.tsv

    done

