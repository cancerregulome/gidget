
t='lgg'
d1='04oct13FH'
d2='23sep13s'

rm -fr *.$t.$d1.$d2.cmp

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.bcgsc.ca__illuminaga_mirnaseq__mirnaseq.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.bcgsc.ca__illuminaga_mirnaseq__mirnaseq.$d2.tsv >& bcgsc.ga_mirna.$t.$d1.$d2.cmp & 

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.bcgsc.ca__illuminaga_rnaseq__rnaseq.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.bcgsc.ca__illuminaga_rnaseq__rnaseq.$d2.tsv >& bcgsc.ga_rna.$t.$d1.$d2.cmp &

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.bcgsc.ca__illuminahiseq_mirnaseq__mirnaseq.$d2.tsv >& bcgsc.hiseq_mirna.$t.$d1.$d2.cmp &

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.bcgsc.ca__illuminahiseq_rnaseq__rnaseq.$d2.tsv >& bcgsc.hiseq_rna.$t.$d1.$d2.cmp 

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.broad.mit.edu__genome_wide_snp_6__snp.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.broad.mit.edu__genome_wide_snp_6__snp.$d2.tsv >& broad.snp6.$t.$d1.$d2.cmp &


python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.jhu-usc.edu__humanmethylation27__methylation.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.jhu-usc.edu__humanmethylation27__methylation.$d2.tsv >& jhu-usc.meth27.$t.$d1.$d2.cmp &

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.jhu-usc.edu__humanmethylation450__methylation.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.jhu-usc.edu__humanmethylation450__methylation.$d2.tsv >& jhu-usc.meth450.$t.$d1.$d2.cmp &

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.mdanderson.org__mda_rppa_core__protein_exp.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.mdanderson.org__mda_rppa_core__protein_exp.$d2.tsv >& mda.rppa.$t.$d1.$d2.cmp 

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/$t.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/$t.unc.edu__illuminahiseq_rnaseqv2__rnaseqv2.$d2.tsv >& unc.hiseq_rna_v2.$t.$d1.$d2.cmp &

python ../main/compare2TSVs.py \
    $TCGAFMP_DATA_DIR/$t/$d1/finalClin.$t.$d1.tsv \
    $TCGAFMP_DATA_DIR/$t/$d2/finalClin.$t.$d2.tsv >& clin.$t.$d1.$d2.cmp &


