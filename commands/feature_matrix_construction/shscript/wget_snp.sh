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
	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/$d/cgcc
        mkdir broad.mit.edu
        chmod g+w broad.mit.edu
        cd broad.mit.edu
        mkdir genome_wide_snp_6
        chmod g+w genome_wide_snp_6
        cd genome_wide_snp_6
        mkdir snp
        chmod g+w snp
        cd snp

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_3*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/cgcc/broad.mit.edu/genome_wide_snp_6/snp

    done

