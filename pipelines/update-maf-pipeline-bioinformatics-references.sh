#!/bin/bash

# This script loads the processed feature matrix into Regulome Explorer

# every TCGA script should start with these lines:
: ${GIDGET_SOURCE_ROOT:?" environment variable must be set and non-empty; defines the path to the local code for the gidget project"}

source ${GIDGET_SOURCE_ROOT}/gidget/util/env.sh

#TODO ssh?

if [[ $# != 0 ]]
    then
        echo " Usage: `basename`"
        echo " "
        echo " This is an admin script and updates the bioinfomatics references."
        echo " Currently, this script updates references for the MAF pipeline,"
        echo " based on the environment variable TCGAMAF_REFERENCES_DIR"
        exit 1
fi

echo
echo "warning: this will reset data in this directory:"
echo $TCGAMAF_REFERENCES_DIR
echo


echo "create MAF references directory, if necessary"
mkdir -p $TCGAMAF_REFERENCES_DIR
echo "-done."

cd $TCGAMAF_REFERENCES_DIR
echo "updating ANNOVAR reference data"
$GIDGET_SOURCE_ROOT/commands/maf_processing/bash/download_monthly_annovar_build_data.sh
echo "-done."

cd $TCGAMAF_REFERENCES_DIR
echo "HGNC processing"
$GIDGET_SOURCE_ROOT/commands/maf_processing/bash/download_hgnc_symbols.sh
echo "-done."

cd $TCGAMAF_REFERENCES_DIR
echo "gene data"
$GIDGET_SOURCE_ROOT/commands/maf_processing/bash/download_daily_gene_data.sh
echo "-done."

cd $TCGAMAF_REFERENCES_DIR
echo "prepareEntrezGeneUniprotReferences"
$GIDGET_SOURCE_ROOT/commands/maf_processing/bash/prepareEntrezGeneUniprotReferences.sh
echo "-done."

echo
echo "done with MAF reference update"