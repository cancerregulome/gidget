#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/tcga_fmp_util.sh


# =============================================================================
# broad.mit.edu/illuminaga_dnaseq_cont/mutations_protected
for d in `cat $TCGAFMP_ROOT_DIR/config/tumor_list.txt`

    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/secure/tumor/$d
        mkdir gsc
        chmod g+w gsc
        cd gsc
	mkdir broad.mit.edu
        chmod g+w broad.mit.edu
	cd broad.mit.edu
	mkdir illuminaga_dnaseq_cont
        chmod g+w illuminaga_dnaseq_cont
	cd illuminaga_dnaseq_cont
	mkdir mutations_protected
        chmod g+w mutations_protected
	cd mutations_protected

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_2*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     --user=USERNAME_HERE --password=PASSWD_HERE \
	     https://tcga-data-secure.nci.nih.gov/tcgafiles/tcga4yeo/tumor/$d/gsc/broad.mit.edu/illuminaga_dnaseq_cont/mutations_protected

    done

# =============================================================================
# genome.wustl.edu/illuminaga_dnaseq_cont/mutations_protected
for d in `cat $TCGAFMP_ROOT_DIR/config/tumor_list.txt`

    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/secure/tumor/$d/gsc/
	mkdir genome.wustl.edu
        chmod g+w genome.wustl.edu
	cd genome.wustl.edu
	mkdir illuminaga_dnaseq_cont
        chmod g+w illuminaga_dnaseq_cont
	cd illuminaga_dnaseq_cont
	mkdir mutations_protected
        chmod g+w mutations_protected
	cd mutations_protected

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_2*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     --user=USERNAME_HERE --password=PASSWD_HERE \
	     https://tcga-data-secure.nci.nih.gov/tcgafiles/tcga4yeo/tumor/$d/gsc/genome.wustl.edu/illuminaga_dnaseq_cont/mutations_protected

    done


# =============================================================================
# hgsc.bcm.edu/illuminaga_dnaseq_cont/mutations_protected
for d in `cat $TCGAFMP_ROOT_DIR/config/tumor_list.txt`

    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/secure/tumor/$d/gsc/
	mkdir hgsc.bcm.edu
        chmod g+w hgsc.bcm.edu
	cd hgsc.bcm.edu
	mkdir illuminaga_dnaseq_cont
        chmod g+w illuminaga_dnaseq_cont
	cd illuminaga_dnaseq_cont
	mkdir mutations_protected
        chmod g+w mutations_protected
	cd mutations_protected

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_2*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     --user=USERNAME_HERE --password=PASSWD_HERE \
	     https://tcga-data-secure.nci.nih.gov/tcgafiles/tcga4yeo/tumor/$d/gsc/hgsc.bcm.edu/illuminaga_dnaseq_cont/mutations_protected

    done


# =============================================================================
# hgsc.bcm.edu/illuminaga_dnaseq_cont_curated/mutations/
for d in `cat $TCGAFMP_ROOT_DIR/config/tumor_list.txt`

    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/$d/gsc/
	mkdir hgsc.bcm.edu
        chmod g+w hgsc.bcm.edu
	cd hgsc.bcm.edu
	mkdir illuminaga_dnaseq_cont_curated
        chmod g+w illuminaga_dnaseq_cont_curated
	cd illuminaga_dnaseq_cont_curated
	mkdir mutations
        chmod g+w mutations
	cd mutations

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_2*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/gsc/hgsc.bcm.edu/illuminaga_dnaseq_cont_curated/mutations

    done

# =============================================================================
