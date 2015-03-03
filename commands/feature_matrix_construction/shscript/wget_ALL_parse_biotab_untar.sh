#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh

# this script requires that the $TCGAFMP_LOCAL_SCRATCH/script_out exists and expects a command line:
#   nohup ./wget_ALL_parse_biotab_untar.sh >& $TCGAFMP_LOCAL_SCRATCH/script_out/`echo "$(date +%Y-%m-%d)"`_wget_parse_untar_out.txt

date
firstDir=`pwd`

cd $TCGAFMP_ROOT_DIR/shscript

echo "===get_metadata==="
./wget_metadata.sh

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

echo print quick check

echo -----------------
grep -C 20 -P "((DONE)|(===))" $TCGAFMP_LOCAL_SCRATCH/script_out/`echo "$(date +%Y-%m-%d)"`_wget_parse_untar_out.txt   

