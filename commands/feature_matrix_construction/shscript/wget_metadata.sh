#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh

# this script requires that the $TCGAFMP_LOCAL_SCRATCH/script_out exists and expects a command line:
#   nohup ./wget_ALL_parse_biotab_untar.sh >& $TCGAFMP_LOCAL_SCRATCH/script_out/`echo "$(date +%Y-%m-%d)"`_wget_parse_untar_out.txt

date
firstDir=`pwd`

cd $TCGAFMP_DCC_REPOSITORIES/uuids/

if [ -s metadata.current.txt ]
    then
        rm -fr metadata.last.txt
        cp metadata.current.txt metadata.last.txt
    fi

rm -fr metadata.current.txt
wget https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/other/metadata/metadata.current.txt

## make sure that we actually got something back !!!
if [ -s metadata.current.txt ]
    then

        rm -fr metadata.original.copy
        cp metadata.current.txt metadata.original.copy
        
        grep -v "UUID" metadata.current.txt | cut -f1-4 | sort >& t1
        rm -fr metadata.current.txt
        mv t1 metadata.current.txt

        ## and also make a copy that includes the date, just
        ## like the snapshot will
        ## cp metadata.current.txt metadata.`echo "$(date +%Y-%m-%d)"`.txt
        cp metadata.current.txt metadata.`echo "$(date +"%d%b%y")" | tr '[A-Z]' '[a-z]'`.txt
        
    else

        echo " ERROR in getting metadata file from TCGA NCI NIH "
        cp metadata.last.txt metadata.current.txt
        touch metadata.current.txt

    fi

cd $firstDir
