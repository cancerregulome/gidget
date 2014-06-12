## 
## pollux:shscript> ./doAllC_refactor.sh
##  Usage   : doAllC_refactor.sh <curDate> <snapshotName> <tumorType> <config> <public/private>
##  Example : doAllC_refactor.sh 28oct13  dcc-snapshot-28oct13  brca  parse_tcga.27_450k.config  public
## 
## pollux:shscript> ./doAllC_refactor_450.sh
##  Usage   : doAllC_refactor_450.sh <curDate> <snapshotName> <tumorType> <config> <public/private>
##  Example : doAllC_refactor_450.sh 28oct13  dcc-snapshot-28oct13  brca  parse_tcga.all450k.config  private
## 

cd $TCGAFMP_ROOT_DIR/shscript/

## first batch: brca, ucec, luad, lusc, kirc (started at 4:25pm)
##      --> lusc finished first at 10:32pm (~6h)
##          kirc finished       at 10:59pm (~6.5h)
##          luad finished       at 11:20pm (~7h)
##          ucec finished       at 00:59am (~8.5h)
##          brca finished       at 3:45am  (~11h)
echo " STARTING BATCH 1 "
date
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  brca  parse_tcga.27_450k.config  private  &
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  ucec  parse_tcga.27_450k.config  private  &
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  luad  parse_tcga.27_450k.config  private  &
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  lusc  parse_tcga.27_450k.config  private  &
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  kirc  parse_tcga.27_450k.config  private  

## second batch: ov, gbm, read, stad (started at 10:59pm)
##      --> stad finished at 1:45am (<3h)
##          read finished at 1:52am (~3h)
##          gbm  finished at 4:07am (~5h)
##          ov   finished at 4:54am (~6h)
echo " STARTING BATCH 2 "
date
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  ov    parse_tcga.27_450k.config  private  &
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  coad  parse_tcga.27_450k.config  private  &
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  gbm   parse_tcga.27_450k.config  private  &
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  read  parse_tcga.27_450k.config  private  &
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  stad  parse_tcga.27_450k.config  private  

## third batch: kirp, laml, hnsc, skcm, lgg (started at 1:45am)
##      --> laml finished at 3:45am (~2h)
##          kirp finished at 4:10am (~2.5h)
##          lgg  finished at 4:10am (~2.5h)
##          hnsc finished at 5:14am (~3.5h)
##          skcm finished at 5:50am (~4h)
echo " STARTING BATCH 3 "
date
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  kirp  parse_tcga.27_450k.config  private  &
sleep 15; ./doAllC_refactor.sh  test_private  dcc-snapshot  laml  parse_tcga.27_450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  hnsc  parse_tcga.all450k.config  private  &
#### sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  skcm  parse_tcga.all450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  lgg   parse_tcga.all450k.config  private  

## fourth batch: thca, prad, sarc, lihc, blca (started at 4:10am)
##      --> sarc finished at 5:25am (~1h)
##          lihc finished at 5:29am 
##          prad finished at 5:40am
##          blca finished at 5:59am
##          thca finished at 6:16am
echo " STARTING BATCH 4 "
date
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  thca  parse_tcga.all450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  prad  parse_tcga.all450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  sarc  parse_tcga.all450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  lihc  parse_tcga.all450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  blca  parse_tcga.all450k.config  private  

## fifth batch: tgct, cesc, pcpg, meso, acc, esca (started at 6:01am)
##      --> meso finished at 6:07am
##          pcpg finished at 6:08am
##          esca finished at 6:11am
##          acc  finished at 7:01am
##          cesc finished at 7:10am
echo " STARTING BATCH 5 "
date
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  tgct  parse_tcga.all450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  cesc  parse_tcga.all450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  pcpg  parse_tcga.all450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  meso  parse_tcga.all450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  acc   parse_tcga.all450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  ucs   parse_tcga.all450k.config  private  &
sleep 15; ./doAllC_refactor_450.sh  test_private  dcc-snapshot  esca  parse_tcga.all450k.config  private  

