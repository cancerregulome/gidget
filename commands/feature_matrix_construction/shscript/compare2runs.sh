#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


t='skcm'
d1='15sep13FH'
d2='test'

rm -fr *.$t.$d1.$d2.cmp

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.bcgsc.ca__illuminaga_mirnaseq__mirnaseq.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.bcgsc.ca__illuminaga_mirnaseq__mirnaseq.$d2.tsv >& ga_mirna.$t.$d1.$d2.cmp &

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.bcgsc.ca__illuminaga_rnaseq__rnaseq.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.bcgsc.ca__illuminaga_rnaseq__rnaseq.$d2.tsv >& ga_rna.$t.$d1.$d2.cmp 

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq.$d2.tsv >& hiseq_mirna.$t.$d1.$d2.cmp &

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$d2.tsv >& hiseq_rna.$t.$d1.$d2.cmp 

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.broad.mit.edu__genome_wide_snp_6__snp.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.broad.mit.edu__genome_wide_snp_6__snp.$d2.tsv >& snp6.$t.$d1.$d2.cmp 


python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.jhu-usc.edu__humanmethylation27__methylation.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.jhu-usc.edu__humanmethylation27__methylation.$d2.tsv >& meth27.$t.$d1.$d2.cmp 

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.jhu-usc.edu__humanmethylation450__methylation.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.jhu-usc.edu__humanmethylation450__methylation.$d2.tsv >& meth450.$t.$d1.$d2.cmp &

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/finalClin.$t.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/finalClin.$t.$d2.tsv >& clin.$t.$d1.$d2.cmp 


t='skcm'
d1='14sep13FH'
d2='13sep13'

rm -fr *.$t.$d1.$d2.cmp

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq.$d2.tsv >& hiseq_mirna.$t.$d1.$d2.cmp &

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.broad.mit.edu__genome_wide_snp_6__snp.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.broad.mit.edu__genome_wide_snp_6__snp.$d2.tsv >& snp6.$t.$d1.$d2.cmp 

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.jhu-usc.edu__humanmethylation450__methylation.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.jhu-usc.edu__humanmethylation450__methylation.$d2.tsv >& meth450.$t.$d1.$d2.cmp &

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.mdanderson.org__mda_rppa_core__protein_exp.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.mdanderson.org__mda_rppa_core__protein_exp.$d2.tsv >& rppa.$t.$d1.$d2.cmp 

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$d2.tsv >& hiseq_rna.$t.$d1.$d2.cmp &

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/finalClin.$t.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/finalClin.$t.$d2.tsv >& clin.$t.$d1.$d2.cmp 

