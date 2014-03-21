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
	cd $TCGA_DATA_TOP_DIR/repositories/dcc-mirror/public/tumor/$d/
        mkdir bcr
        chmod g+w bcr
        cd bcr
        mkdir nationwidechildrens.org
        chmod g+w nationwidechildrens.org
        cd nationwidechildrens.org
        mkdir bio
        chmod g+w bio
        cd bio
        mkdir clin
        chmod g+w clin
        cd clin

        ## NEW 22jan14 : grabbing the bio.Level_2 files as well

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*bio.Level_1*.tar.gz" --accept "*bio.Level_2*.tar.gz" \
             --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/bcr/nationwidechildrens.org/bio/clin

    done

for d in `cat $TCGAFMP_ROOT_DIR/shscript/tumor_list.txt`
    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d
	cd $TCGA_DATA_TOP_DIR/repositories/dcc-mirror/public/tumor/$d
        mkdir bcr
        chmod g+w bcr
        cd bcr
        mkdir genome.wustl.edu
        chmod g+w genome.wustl.edu
        cd genome.wustl.edu
        mkdir bio
        chmod g+w bio
        cd bio
        mkdir clin
        chmod g+w clin
        cd clin

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*bio.Level_1*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/bcr/genome.wustl.edu/bio/clin

    done


for d in `cat $TCGAFMP_ROOT_DIR/shscript/tumor_list.txt`
    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d
	cd $TCGA_DATA_TOP_DIR/repositories/dcc-mirror/public/tumor/$d
        mkdir bcr
        chmod g+w bcr
        cd bcr
        mkdir intgen.org
        chmod g+w intgen.org
        cd intgen.org
        mkdir bio
        chmod g+w bio
        cd bio
        mkdir clin
        chmod g+w clin
        cd clin

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*bio.Level_1*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/bcr/intgen.org/bio/clin

    done


