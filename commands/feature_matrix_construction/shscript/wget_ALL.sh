#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


curDir=`pwd`

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_bio "
./wget_bio.sh

### cd $TCGAFMP_ROOT_DIR/shscript
### date
### echo " wget_biotab "
### ./wget_biotab.sh

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_maf "
./wget_maf.sh

### cd $TCGAFMP_ROOT_DIR/shscript
### date
### echo " wget_maf_prot "
### ./wget_maf_prot.sh

### cd $TCGAFMP_ROOT_DIR/shscript
### date
### echo " wget_msat_prot "
### ./wget_msat_prot.sh

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_meth "
./wget_meth.sh

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_mirn "
./wget_mirn.sh

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_rnaseq "
./wget_rnaseq.sh

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_rppa "
./wget_rppa.sh

cd $TCGAFMP_ROOT_DIR/shscript
date
echo " wget_snp "
./wget_snp.sh

echo " DONE !!! "
date

cd $curDir

