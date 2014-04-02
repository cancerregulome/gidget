#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

python $TCGAFMP_ROOT_DIR/main/mergeTSV.py \
    $TCGAFMP_DATA_DIR/blca/29mar13/finalClin.blca.29mar13.tsv \
    $TCGAFMP_DATA_DIR/brca/29mar13/finalClin.brca.29mar13.tsv \
    $TCGAFMP_DATA_DIR/coad/29mar13/finalClin.coad.29mar13.tsv \
    $TCGAFMP_DATA_DIR/gbm/29mar13/finalClin.gbm.29mar13.tsv \
    $TCGAFMP_DATA_DIR/hnsc/29mar13/finalClin.hnsc.29mar13.tsv \
    $TCGAFMP_DATA_DIR/kirc/29mar13/finalClin.kirc.29mar13.tsv \
    $TCGAFMP_DATA_DIR/laml/29mar13/finalClin.laml.29mar13.tsv \
    $TCGAFMP_DATA_DIR/luad/29mar13/finalClin.luad.29mar13.tsv \
    $TCGAFMP_DATA_DIR/blca/29mar13/blca.gexp.seq.tmpData2.tsv \
    $TCGAFMP_DATA_DIR/brca/29mar13/brca.gexp.seq.tmpData2.tsv \
    $TCGAFMP_DATA_DIR/coad/29mar13/coad.gexp.seq.tmpData2.tsv \
    $TCGAFMP_DATA_DIR/gbm/29mar13/gbm.gexp.seq.tmpData2.tsv \
    $TCGAFMP_DATA_DIR/hnsc/29mar13/hnsc.gexp.seq.tmpData2.tsv \
    $TCGAFMP_DATA_DIR/kirc/29mar13/kirc.gexp.seq.tmpData2.tsv \
    $TCGAFMP_DATA_DIR/laml/29mar13/laml.gexp.seq.tmpData2.tsv \
    $TCGAFMP_DATA_DIR/luad/29mar13/luad.gexp.seq.tmpData2.tsv \
    test.merge.8.tsv


