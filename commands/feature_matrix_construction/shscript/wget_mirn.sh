#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/shscript/tcga_fmp_util.sh


for d in `cat $TCGAFMP_ROOT_DIR/config/tumor_list.txt`

    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/$d/cgcc/
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

	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/$d/cgcc/
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

