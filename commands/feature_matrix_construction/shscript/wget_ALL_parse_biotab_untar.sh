#!/bin/bash

date
firstDir=`pwd`

cd $TCGAFMP_ROOT_DIR/shscript
echo "===wget_ALL==="
./wget_ALL.sh

date
echo "===parse_biotab==="
./parse_biospecimen_biotab_files.sh

date
echo "===untar==="
./untar.mirror_date.sh

cd $firstDir

date
echo DONE!!!
