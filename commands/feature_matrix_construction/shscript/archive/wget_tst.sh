#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


if [ $# -ne 1 ]
then
  echo "Usage: `basename $0` local-TCGA-directory"
  echo "   eg: for disk structure as"
  echo "         <path to TCGA data>/TCGA/repostiories,"
  echo "         <path to TCGA data>/TCGA/repostiories/dcc-mirror,"
  echo "         etc,"
  echo "       use"
  echo "         `basename $0` <path to TCGA data>/TCGA"
  exit -1
fi

TCGA_DATA_TOP_DIR=$1
# TODO: validate that TCGA_DATA_TOP_DIR is a valid directory


cd /tmp/

for d in skcm
    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd $TCGA_DATA_TOP_DIR/repositories/dcc-mirror/secure/tumor/$d
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

