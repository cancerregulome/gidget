#!/bin/bash

#TODO:FILE_LAYOUT this file appears to be unused, although if it is used then it needs to be refactored to avoid explicit paths

export PATH=${HOME}/bin:${HOME}/bin/${THISARCH}:$PATH
export PATH=/tools/bin:/titan/cancerregulome9/ITMI_PTB/bin/go/bin:$PATH # TODO:FILE_LAYOUT:EXPLICIT
export PATH=/package/genome/EMBOSS/EMBOSS-1.13.3/emboss:$PATH
export MANPATH=${HOME}/man:$MANPATH
export LD_LIBRARY_PATH=/tools/lib/
export GIDGET_SOURCE_ROOT=/users/sreynold/git_home/gidget
export TCGAFMP_ROOT_DIR=/users/sreynold/git_home/gidget/commands/feature_matrix_construction
export TCGAFMP_PYTHON3=/users/rkramer/bin/python3
export TCGAFMP_BIOINFORMATICS_REFERENCES=/titan/cancerregulome9/workspaces/bioinformatics_references # TODO:FILE_LAYOUT:EXPLICIT
export TCGAFMP_LOCAL_SCRATCH=/titan/cancerregulome13/TCGA/pw_scratch # TODO:FILE_LAYOUT:EXPLICIT
export TCGAFMP_CLUSTER_HOME=/titan/cancerregulome9/workspaces/cluster # TODO:FILE_LAYOUT:EXPLICIT
export TCGAFMP_CLUSTER_SCRATCH=/titan/cancerregulome13/TCGA/pw_scratch # TODO:FILE_LAYOUT:EXPLICIT
export TCGAFMP_DCC_REPOSITORIES=/titan/cancerregulome11/TCGA/repositories # TODO:FILE_LAYOUT:EXPLICIT
export TCGAFMP_DATA_DIR=/titan/cancerregulome14/TCGAfmp_outputs # TODO:FILE_LAYOUT:EXPLICIT
export TCGAFMP_FIREHOSE_MIRROR=/titan/cancerregulome9/TCGA/firehose # TODO:FILE_LAYOUT:EXPLICIT
export TCGAFMP_OUTPUTS=/titan/cancerregulome14/TCGAfmp_outputs # TODO:FILE_LAYOUT:EXPLICIT
export TCGAFMP_PAIRWISE_ROOT=/titan/cancerregulome8/TCGA/scripts # TODO:FILE_LAYOUT:EXPLICIT
export TCGABINARIZATION_DATABASE_DIR=/proj/ilyalab/bbernard/database
export TCGABINARIZATION_REFERENCES_DIR=/titan/cancerregulome9/workspaces/bioinformatics_references/binarization/20140512 # TODO:FILE_LAYOUT:EXPLICIT
export TCGAMAF_ROOT_DIR=/users/sreynold/git_home/gidget/commands/maf_processing
export TCGAMAF_SCRIPTS_DIR=/users/sreynold/git_home/gidget/commands/maf_processing
export TCGAMAF_DATA_DIR=/titan/cancerregulome9/workspaces/users/sreynolds/maf-proc # TODO:FILE_LAYOUT:EXPLICIT
export TCGAMAF_REFERENCES_DIR=/titan/cancerregulome9/workspaces/bioinformatics_references/maf/20140504 # TODO:FILE_LAYOUT:EXPLICIT
export TCGAMAF_TOOLS_DIR=/tools/bin/
export TCGAMAF_PYTHON_BINARY=/tools/bin/python
export PYTHONPATH=$GIDGET_SOURCE_ROOT/gidget/util:$TCGAFMP_ROOT_DIR/main:$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$TCGAMAF_ROOT_DIR/python:/users/sreynold/.local/lib/python2.7/site-packages
export CR3=/titan/cancerregulome14/TCGAfmp_outputs # TODO:FILE_LAYOUT:EXPLICIT
export VT_UTILS=/users/sreynold/git_home/VTpub/bin
export VT_SURVIVAL=/users/sreynold/git_home/vthorsson/survival
export CMP_HOME=/users/sreynold/git_home/ClinMolPairs
export PROJ_HOME=/users/sreynold/git_home/vthorsson
export DRY_RUN_COUNT=1000

umask 002

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh

cd $TCGAFMP_ROOT_DIR/shscript

f=snapshot-`echo "$(date +%Y-%m-%d)"`-log.txt
nohup ./wget_ALL_parse_biotab_untar.sh >& $TCGAFMP_DCC_REPOSITORIES/script_log/$f &

