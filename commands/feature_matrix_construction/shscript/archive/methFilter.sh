
## methFile=$1
## gexpFile=$2

## NOTE !!! we don't need the methFile to have been "annotated" because it automatically
## comes with the genomic coordinates of the probes ...
## the gexpFile on the other hand DOES need to be annotated

## methFile=/users/sreynold/to_be_checked_in/TCGAfmp/main/skcm.meth.top05.annot.tsv
methFile=/local/sreynold/scratch/skcm.jhu-usc.edu__humanmethylation450__methylation.450k_test.tsv
## gexpFile=$TCGAFMP_DATA_DIR/skcm/test3/skcm.gexp.seq.tmpData2.tsv
gexpFile=/local/sreynold/scratch/skcm.gexp.seq.tmpData2.tsv

rm -fr /local/sreynold/scratch/qq*

head -1 $methFile >& /local/sreynold/scratch/qq01
head -1 $gexpFile >& /local/sreynold/scratch/qq02

$TCGA_ROOT_DIR/shscript/tcga_fmp_transpose.sh /local/sreynold/scratch/qq01 | cut -c-15 >& /local/sreynold/scratch/qq03
$TCGA_ROOT_DIR/shscript/tcga_fmp_transpose.sh /local/sreynold/scratch/qq02 | cut -c-15 >& /local/sreynold/scratch/qq04

cat /local/sreynold/scratch/qq03 /local/sreynold/scratch/qq04 | sort | uniq -c | sort -nr | grep " 2 " | cut -c9- | sort >& /local/sreynold/scratch/qq05

python /users/sreynold/to_be_checked_in/TCGAfmp/main/filterTSVbySampList.py $methFile $methFile.qq.tsv /local/sreynold/scratch/qq05 white loose >& /local/sreynold/scratch/qq.meth.filt.log

python /users/sreynold/to_be_checked_in/TCGAfmp/main/filterTSVbySampList.py $gexpFile $gexpFile.qq.tsv /local/sreynold/scratch/qq05 white loose >& /local/sreynold/scratch/qq.gexp.filt.log

rm -fr /local/sreynold/scratch/????File.h?
head -1 $methFile.qq.tsv >& /local/sreynold/scratch/methFile.h1
head -1 $gexpFile.qq.tsv >& /local/sreynold/scratch/gexpFile.h1

$TCGA_ROOT_DIR/shscript/tcga_fmp_transpose.sh /local/sreynold/scratch/methFile.h1 | cut -c-15 >& /local/sreynold/scratch/methFile.h2
$TCGA_ROOT_DIR/shscript/tcga_fmp_transpose.sh /local/sreynold/scratch/gexpFile.h1 | cut -c-15 >& /local/sreynold/scratch/gexpFile.h2

## at this point the methFile.h2 and gexpFile.h2 should be identical or else we should not go forward !!!

python /users/sreynold/to_be_checked_in/TCGAfmp/main/methCorr.py $methFile.qq.tsv $gexpFile.qq.tsv "N:GEXP:" >& /local/sreynold/scratch/testing.qq

