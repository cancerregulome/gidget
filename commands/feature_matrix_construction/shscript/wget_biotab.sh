#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/shscript/tcga_fmp_util.sh


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


for d in `cat $TCGAFMP_ROOT_DIR/shscript/tumor_list.txt`
    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d
	cd $TCGA_DATA_TOP_DIR/repositories/dcc-mirror/public/tumor/$d/bcr/
	mkdir biotab
        chmod g+w biotab
	cd biotab
	mkdir clin
        chmod g+w clin
	cd clin

	rm -fr index.html
	rm -fr *.tar.gz
	rm -fr *.txt

	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*.txt" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/bcr/biotab/clin

        chmod g+w *.*

    done

