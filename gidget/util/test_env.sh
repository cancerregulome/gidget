#!/bin/bash

# Sample script to demonstrate usage of the bash utilies in env.sh;
# Note that one check, for TCGAFMP_ROOT_DIR, should be done before sourcing the utility script.

# This simple script simply prints a global variable that will only be non-blank if the utility script
# was imported properly.


# every TCGA FMP script should start with these lines
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh



echo "script path is ${SCRIPT_PATH}"
