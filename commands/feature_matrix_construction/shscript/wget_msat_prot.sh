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

	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/secure/tumor/$d/cgcc/
	mkdir nationwidechildrens.org
        chmod g+w nationwidechildrens.org
	cd nationwidechildrens.org
	mkdir microsat_i
        chmod g+w microsat_i
	cd microsat_i
	mkdir fragment_analysis
        chmod g+w fragment_analysis
	cd fragment_analysis

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_1*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
	     --accept "*Level_2*.tar.gz" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     --user=USERNAME_HERE --password=PASSWD_HERE \
	     https://tcga-data-secure.nci.nih.gov/tcgafiles/tcga4yeo/tumor/$d/cgcc/nationwidechildrens.org/microsat_i/fragment_analysis

    done

