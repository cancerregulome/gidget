#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


cd /tmp/

for d in brca
    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/secure/tumor/$d
        mkdir gsc
        chmod g+w gsc
        cd gsc
	mkdir ucsc.edu
        chmod g+w ucsc.edu
	cd ucsc.edu
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
	     https://tcga-data-secure.nci.nih.gov/tcgafiles/tcga4yeo/tumor/$d/gsc/ucsc.edu/illuminaga_dnaseq_cont/mutations_protected

    done

for d in brca
    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/secure/tumor/$d
        mkdir gsc
        chmod g+w gsc
        cd gsc
	mkdir ucsc.edu
        chmod g+w ucsc.edu
	cd ucsc.edu
	mkdir illuminaga_dnaseq
        chmod g+w illuminaga_dnaseq
	cd illuminaga_dnaseq
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
	     https://tcga-data-secure.nci.nih.gov/tcgafiles/tcga4yeo/tumor/$d/gsc/ucsc.edu/illuminaga_dnaseq/mutations_protected

    done

