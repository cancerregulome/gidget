#!/bin/bash


###
# usage

# every file in the TCGA MAF project should begin
# by sourcing this file.
# do not source the implementation file directly; this file provides the equivilent
# of header guards

: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF scripts directory"}

# prevent multiple imports and avoid multiple global variable and function
# definitions, and function executions
if [ -z "${TCGAMAF_IMPORTED_UTILS}" ]
then
    # echo "importing TCGA MAF utilities:"
    source ${TCGAMAF_ROOT_DIR}/bash/tcga_maf_util_impl.sh
    # echo "..done"
fi
