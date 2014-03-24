#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAFMP_ROOT_DIR}/bash/tcga_maf_util.sh


MAF_ROOT=${1:-/users/liype/maf_check_in}
export MAF_DATA_DIR=${MAF_ROOT}"/data"
export MAF_REFERENCES_DIR=${MAF_ROOT}"/reference"
export MAF_TOOLS_DIR=${MAF_ROOT}"/tools"
export MAF_SCRIPTS_DIR=${MAF_ROOT}"/src"
export MAF_PYTHON_BINARY="/tools/bin/python2.7"
