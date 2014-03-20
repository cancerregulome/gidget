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
# TODO: validate that TCGA_DATA_TOP_DIR is a valid directory


curDir=`pwd`

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_bio "
./wget_bio.sh $TCGA_DATA_TOP_DIR

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_biotab "
./wget_biotab.sh $TCGA_DATA_TOP_DIR

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_maf "
./wget_maf.sh $TCGA_DATA_TOP_DIR

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_maf_prot "
./wget_maf_prot.sh $TCGA_DATA_TOP_DIR

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_msat_prot "
./wget_msat_prot.sh $TCGA_DATA_TOP_DIR

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_meth "
./wget_meth.sh $TCGA_DATA_TOP_DIR

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_mirn "
./wget_mirn.sh $TCGA_DATA_TOP_DIR

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_rnaseq "
./wget_rnaseq.sh $TCGA_DATA_TOP_DIR

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_rppa "
./wget_rppa.sh $TCGA_DATA_TOP_DIR

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_snp "
./wget_snp.sh $TCGA_DATA_TOP_DIR

echo " DONE !!! "
date

cd $curDir

