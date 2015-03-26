#!/bin/bash

export PATH=${HOME}/bin:${HOME}/bin/${THISARCH}:$PATH
export PATH=/tools/bin:/titan/cancerregulome9/ITMI_PTB/bin/go/bin:$PATH
export PATH=/package/genome/EMBOSS/EMBOSS-1.13.3/emboss:$PATH
export MANPATH=${HOME}/man:$MANPATH
export LD_LIBRARY_PATH=/tools/lib/
export GIDGET_SOURCE_ROOT=/users/sreynold/git_home/gidget
export TCGAFMP_ROOT_DIR=/users/sreynold/git_home/gidget/commands/feature_matrix_construction
export TCGAFMP_PYTHON3=/users/rkramer/bin/python3
export TCGAFMP_BIOINFORMATICS_REFERENCES=/titan/cancerregulome9/workspaces/bioinformatics_references
export TCGAFMP_LOCAL_SCRATCH=/titan/cancerregulome13/TCGA/pw_scratch
export TCGAFMP_CLUSTER_HOME=/titan/cancerregulome9/workspaces/cluster
export TCGAFMP_CLUSTER_SCRATCH=/titan/cancerregulome13/TCGA/pw_scratch
export TCGAFMP_DCC_REPOSITORIES=/titan/cancerregulome11/TCGA/repositories
export TCGAFMP_DATA_DIR=/titan/cancerregulome14/TCGAfmp_outputs
export TCGAFMP_FIREHOSE_MIRROR=/titan/cancerregulome9/TCGA/firehose
export TCGAFMP_OUTPUTS=/titan/cancerregulome14/TCGAfmp_outputs
export TCGAFMP_PAIRWISE_ROOT=/titan/cancerregulome8/TCGA/scripts
export TCGABINARIZATION_DATABASE_DIR=/proj/ilyalab/bbernard/database
export TCGABINARIZATION_REFERENCES_DIR=/titan/cancerregulome9/workspaces/bioinformatics_references/binarization/20140512
export TCGAMAF_ROOT_DIR=/users/sreynold/git_home/gidget/commands/maf_processing
export TCGAMAF_SCRIPTS_DIR=/users/sreynold/git_home/gidget/commands/maf_processing
export TCGAMAF_DATA_DIR=/titan/cancerregulome9/workspaces/users/sreynolds/maf-proc
export TCGAMAF_REFERENCES_DIR=/titan/cancerregulome9/workspaces/bioinformatics_references/maf/20140504
export TCGAMAF_TOOLS_DIR=/tools/bin/
export TCGAMAF_PYTHON_BINARY=/tools/bin/python
export PYTHONPATH=$GIDGET_SOURCE_ROOT/gidget/util:$TCGAFMP_ROOT_DIR/main:$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$TCGAMAF_ROOT_DIR/python:/users/sreynold/.local/lib/python2.7/site-packages
export CR3=/titan/cancerregulome14/TCGAfmp_outputs
export VT_UTILS=/users/sreynold/git_home/VTpub/bin
export VT_SURVIVAL=/users/sreynold/git_home/vthorsson/survival
export CMP_HOME=/users/sreynold/git_home/ClinMolPairs
export PROJ_HOME=/users/sreynold/git_home/vthorsson
export DRY_RUN_COUNT=1000

umask 002

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


cd $TCGAFMP_CLUSTER_SCRATCH/cluster_test

f=test-`echo "$(date +"%d%b%y")" | tr '[A-Z]' '[a-z]'`.log
rm -fr $f
echo " " >& $f
echo " CLUSTER TEST STARTING AT ... " `date` >> $f
echo " " >> $f
python $TCGAFMP_ROOT_DIR/main/run-pairwise-v2.py --byType --type1 GEXP --type2 CNVR \
    --pvalue 1.e-06 --forRE \
    --tsvFile $TCGAFMP_DATA_DIR/cesc/01oct14/cesc.seq.01oct14.TP.tsv >> $f
echo " " >> $f
echo " CLUSTER TEST FINISHED AT ... " `date` >> $f
echo " " >> $f
echo " DONE " >> $f

cd $TCGAFMP_DATA_DIR/cesc/01oct14/
echo " " >> $TCGAFMP_CLUSTER_SCRATCH/cluster_test/$f
echo " " >> $TCGAFMP_CLUSTER_SCRATCH/cluster_test/$f

rm -fr t?
sort cesc.seq.01oct14.TP.GEXP.CNVR.pwpv            >& t1
sort cesc.seq.01oct14.TP.GEXP.CNVR.pwpv.KEEP       >& t2
sort cesc.seq.01oct14.TP.GEXP.CNVR.pwpv.forRE      >& t3
sort cesc.seq.01oct14.TP.GEXP.CNVR.pwpv.forRE.KEEP >& t4

echo " THESE NEXT TWO LINES SHOULD SHOW ZEROS " >> $TCGAFMP_CLUSTER_SCRATCH/cluster_test/$f
diff t1 t2 | wc -l >> $TCGAFMP_CLUSTER_SCRATCH/cluster_test/$f
diff t3 t4 | wc -l >> $TCGAFMP_CLUSTER_SCRATCH/cluster_test/$f
echo " " >> $TCGAFMP_CLUSTER_SCRATCH/cluster_test/$f

rm -fr t1 t2 t3 t4

cd $TCGAFMP_CLUSTER_SCRATCH
## find . -mtime +5 -exec rm -fr {} \;

