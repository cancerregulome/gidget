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
	cd $TCGA_DATA_TOP_DIR/repositories/dcc-mirror/public/tumor/$d/cgcc/
        mkdir mdanderson.org
        chmod g+w mdanderson.org
        cd mdanderson.org
        mkdir mda_rppa_core
        chmod g+w mda_rppa_core
        cd mda_rppa_core
        mkdir protein_exp
        chmod g+w protein_exp
        cd protein_exp

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_3*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/cgcc/mdanderson.org/mda_rppa_core/protein_exp

    done

