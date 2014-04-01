#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/shscript/tcga_fmp_util.sh


date
firstDir=`pwd`

cd $TCGAFMP_ROOT_DIR/shscript
echo "===wget_ALL==="
./wget_ALL.sh

date
echo "===untar==="
./untar.mirror_date.sh

date
echo "===parse_biotab==="
./parse_biospecimen_biotab_files.sh

cd $firstDir

date
echo DONE!!!
