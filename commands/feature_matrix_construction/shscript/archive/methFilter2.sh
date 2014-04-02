
## methFile=$1
## mirnFile=$2

## NOTE !!! we don't need the methFile to have been "annotated" because it automatically
## comes with the genomic coordinates of the probes ...
## the mirnFile on the other hand DOES need to be annotated

## methFile=/users/sreynold/to_be_checked_in/TCGAfmp/main/skcm.meth.top05.annot.tsv
methFile=/local/sreynold/scratch/skcm.jhu-usc.edu__humanmethylation450__methylation.450k_test.tsv
## mirnFile=$TCGAFMP_DATA_DIR/skcm/test3/skcm.mirn.tmpData2.tsv
mirnFile=/local/sreynold/scratch/skcm.mirn.tmpData2.tsv

rm -fr /local/sreynold/scratch/pp*

head -1 $methFile >& /local/sreynold/scratch/pp01
head -1 $mirnFile >& /local/sreynold/scratch/pp02

$TCGA_ROOT_DIR/shscript/tcga_fmp_transpose.sh /local/sreynold/scratch/pp01 | cut -c-15 >& /local/sreynold/scratch/pp03
$TCGA_ROOT_DIR/shscript/tcga_fmp_transpose.sh /local/sreynold/scratch/pp02 | cut -c-15 >& /local/sreynold/scratch/pp04

cat /local/sreynold/scratch/pp03 /local/sreynold/scratch/pp04 | sort | uniq -c | sort -nr | grep " 2 " | cut -c9- | sort >& /local/sreynold/scratch/pp05

python /users/sreynold/to_be_checked_in/TCGAfmp/main/filterTSVbySampList.py $methFile $methFile.pp.tsv /local/sreynold/scratch/pp05 white loose >& /local/sreynold/scratch/pp.meth.filt.log

python /users/sreynold/to_be_checked_in/TCGAfmp/main/filterTSVbySampList.py $mirnFile $mirnFile.pp.tsv /local/sreynold/scratch/pp05 white loose >& /local/sreynold/scratch/pp.mirn.filt.log

rm -fr /local/sreynold/scratch/????File.g?
head -1 $methFile.pp.tsv >& /local/sreynold/scratch/methFile.g1
head -1 $mirnFile.pp.tsv >& /local/sreynold/scratch/mirnFile.g1

$TCGA_ROOT_DIR/shscript/tcga_fmp_transpose.sh /local/sreynold/scratch/methFile.g1 | cut -c-15 >& /local/sreynold/scratch/methFile.g2
$TCGA_ROOT_DIR/shscript/tcga_fmp_transpose.sh /local/sreynold/scratch/mirnFile.g1 | cut -c-15 >& /local/sreynold/scratch/mirnFile.g2

## at this point the methFile.g2 and mirnFile.g2 should be identical or else we should not go forward !!!

python /users/sreynold/to_be_checked_in/TCGAfmp/main/methCorr.py $methFile.pp.tsv $mirnFile.pp.tsv "N:MIRN:" >& /local/sreynold/scratch/testing.pp

