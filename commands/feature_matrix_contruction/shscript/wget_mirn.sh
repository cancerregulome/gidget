cd ~/scratch/

for d in acc blca brca cesc cntl coad dlbc esca gbm hnsc kich kirc kirp laml lgg lihc luad lusc meso ov paad pcpg prad read sarc skcm stad tgct thca ucs ucec
    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	## cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$d/cgcc/bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq/
	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$d/cgcc/
        mkdir bcgsc.ca
        chmod g+w bcgsc.ca
        cd bcgsc.ca
        mkdir illuminahiseq_mirnaseq
        chmod g+w illuminahiseq_mirnaseq
        cd illuminahiseq_mirnaseq
        mkdir mirnaseq
        chmod g+w mirnaseq
        cd mirnaseq

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_3*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/cgcc/bcgsc.ca/illuminahiseq_mirnaseq/mirnaseq/


	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	## cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$d/cgcc/bcgsc.ca/illuminaga_mirnaseq/mirnaseq/
	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$d/cgcc/
        mkdir bcgsc.ca
        chmod g+w bcgsc.ca
        cd bcgsc.ca
        mkdir illuminaga_mirnaseq
        chmod g+w illuminaga_mirnaseq
        cd illuminaga_mirnaseq
        mkdir mirnaseq
        chmod g+w mirnaseq
        cd mirnaseq

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_3*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/cgcc/bcgsc.ca/illuminaga_mirnaseq/mirnaseq/

    done

