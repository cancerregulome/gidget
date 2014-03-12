#!/bin/bash

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
echo "using local TCGA top-level data directory $TCGA_DATA_TOP_DIR"
echo

# TODO: validate that TCGA_DATA_TOP_DIR is a valid directory


date
firstDir=`pwd`

cd $TCGAFMP_ROOT_DIR/shscript
echo "===wget_ALL==="
./wget_ALL.sh $TCGA_DATA_TOP_DIR

date
echo "===parse_biotab==="
./parse_biospecimen_biotab_files.sh $TCGA_DATA_TOP_DIR

date
echo "===untar==="
./untar.mirror_date.sh $TCGA_DATA_TOP_DIR

cd $firstDir

date
echo DONE!!!
