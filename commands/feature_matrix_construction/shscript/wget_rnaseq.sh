#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


for d in `cat $TCGAFMP_ROOT_DIR/config/tumor_list.txt`

    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	## UNC HiSeq RNASeqV2
	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/$d
        mkdir cgcc
        chmod g+w cgcc
        cd cgcc
        mkdir unc.edu
        chmod g+w unc.edu
        cd unc.edu

        mkdir illuminahiseq_rnaseqv2
        chmod g+w illuminhiseq_rnaseqv2
        cd illuminahiseq_rnaseqv2
        mkdir rnaseqv2
        chmod g+w rnaseqv2
        cd rnaseqv2

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_3*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/cgcc/unc.edu/illuminahiseq_rnaseqv2/rnaseqv2

	## UNC GA RNASeqV2
	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/$d/cgcc/unc.edu/
	mkdir illuminaga_rnaseqv2
        chmod g+w illuminaga_rnaseqv2
	cd illuminaga_rnaseqv2
	mkdir rnaseqv2
        chmod g+w rnaseqv2
	cd rnaseqv2

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_3*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/cgcc/unc.edu/illuminaga_rnaseqv2/rnaseqv2

	## UNC GA RNASeq
	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/$d/cgcc/unc.edu
        mkdir illuminaga_rnaseq
        chmod g+w illuminaga_rnaseq
        cd illuminaga_rnaseq
        mkdir rnaseq
        chmod g+w rnaseq
        cd rnaseq

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_3*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/cgcc/unc.edu/illuminaga_rnaseq/rnaseq

	## BCGSC GA RNASeq
	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/$d/cgcc
        mkdir bcgsc.ca
        chmod g+w bcgsc.ca
        cd bcgsc.ca
        mkdir illuminaga_rnaseq
        chmod g+w illuminaga_rnaseq
        cd illuminaga_rnaseq
        mkdir rnaseq
        chmod g+w rnaseq
        cd rnaseq

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_3*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/cgcc/bcgsc.ca/illuminaga_rnaseq/rnaseq

	## BCGSC HiSeq RNASeq
	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/$d/cgcc/bcgsc.ca
        mkdir illuminahiseq_rnaseq
        chmod g+w illuminahiseq_rnaseq
        cd illuminahiseq_rnaseq
        mkdir rnaseq
        chmod g+w rnaseq
        cd rnaseq

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_3*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/cgcc/bcgsc.ca/illuminahiseq_rnaseq/rnaseq

    done

