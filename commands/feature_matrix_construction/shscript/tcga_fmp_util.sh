#!/bin/bash

###
# usage

# every file in the TCGA Feature Matrix Construction project should begin
# by sourcing this file.
# do not source the implementation file directly; this file provides the equivilent
# of header guards

: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}

# prevent multiple imports and avoid multiple global variable and function
# definitions, and function executions
if [ -z "${TCGAFMP_IMPORTED_UTILS}" ]
then
    # echo "importing TCGA FMP utilities:"
    source ${TCGAFMP_ROOT_DIR}/tcga_fmp_util_impl.sh
    # echo "..done"
fi
