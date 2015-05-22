#!/bin/bash

###
# usage

# every file in the TCGA Feature Matrix Construction project should begin
# by sourcing this file.
# do not source the implementation file directly; this file provides the equivilent
# of header guards

: ${GIDGET_SOURCE_ROOT:?" environment variable must be set and non-empty; defines the path to the local gidget sourcecode"}

# prevent multiple imports and avoid multiple global variable and function
# definitions, and function executions
if [ -z "${GIDGET_IMPORTED_UTILS}" ]
then
    # echo "importing TCGA FMP utilities:"
    source ${GIDGET_SOURCE_ROOT}/gidget/util/env_impl.sh
    # echo "..done"
fi
