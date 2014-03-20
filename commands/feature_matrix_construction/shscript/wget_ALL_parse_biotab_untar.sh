#!/bin/bash

if [ $# -ne 2 ]
then
  echo "Usage:   `basename $0` local-TCGA-directory TCGA-fmp-output-directory"
  echo "         TCGA-fmp-output-directory must contain subdirectories named as the tumor types"
  echo "example: for disk structure as"
  echo "           <path to TCGA data>/TCGA/repostiories,"
  echo "           <path to TCGA data>/TCGA/repostiories/dcc-mirror,"
  echo "           <path to TCGA outputs>/TCGAfmp_outputs"
  echo "           etc,"
  echo "         use"
  echo "           `basename $0` <path to TCGA data>/TCGA <path to TCGA outputs>/TCGAfmp_outputs"
  exit -1
fi

TCGA_DATA_TOP_DIR=$1
TCGA_FMP_OUTPUT_DIR=$2
# TODO: validate that TCGA_DATA_TOP_DIR is a valid directory


date
firstDir=`pwd`

cd $TCGAFMP_ROOT_DIR/shscript
echo "===wget_ALL==="
./wget_ALL.sh $TCGA_DATA_TOP_DIR

date
echo "===parse_biotab==="
./parse_biospecimen_biotab_files.sh $TCGA_DATA_TOP_DIR $TCGA_FMP_OUTPUT_DIR

date
echo "===untar==="
./untar.mirror_date.sh $TCGA_DATA_TOP_DIR

cd $firstDir

date
echo DONE!!!
