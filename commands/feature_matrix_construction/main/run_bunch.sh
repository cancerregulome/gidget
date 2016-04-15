#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


python ./run_pwRK2.py --pvalue 2. --one 248 --tsvFile $TCGAFMP_DATA_DIR/blca/22mar13/blca.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 249 --tsvFile $TCGAFMP_DATA_DIR/blca/22mar13/blca.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 250 --tsvFile $TCGAFMP_DATA_DIR/blca/22mar13/blca.seq.22mar13.TP.tsv

python ./run_pwRK2.py --pvalue 2. --one 262 --tsvFile $TCGAFMP_DATA_DIR/brca/22mar13/brca.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 263 --tsvFile $TCGAFMP_DATA_DIR/brca/22mar13/brca.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 264 --tsvFile $TCGAFMP_DATA_DIR/brca/22mar13/brca.seq.22mar13.TP.tsv

python ./run_pwRK2.py --pvalue 2. --one 298 --tsvFile $TCGAFMP_DATA_DIR/coad/22mar13/coad.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 299 --tsvFile $TCGAFMP_DATA_DIR/coad/22mar13/coad.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 300 --tsvFile $TCGAFMP_DATA_DIR/coad/22mar13/coad.seq.22mar13.TP.tsv

python ./run_pwRK2.py --pvalue 2. --one 317 --tsvFile $TCGAFMP_DATA_DIR/gbm/22mar13/gbm.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 318 --tsvFile $TCGAFMP_DATA_DIR/gbm/22mar13/gbm.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 319 --tsvFile $TCGAFMP_DATA_DIR/gbm/22mar13/gbm.seq.22mar13.TP.tsv

python ./run_pwRK2.py --pvalue 2. --one 302 --tsvFile $TCGAFMP_DATA_DIR/hnsc/22mar13/hnsc.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 303 --tsvFile $TCGAFMP_DATA_DIR/hnsc/22mar13/hnsc.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 304 --tsvFile $TCGAFMP_DATA_DIR/hnsc/22mar13/hnsc.seq.22mar13.TP.tsv

python ./run_pwRK2.py --pvalue 2. --one 198 --tsvFile $TCGAFMP_DATA_DIR/kirc/22mar13/kirc.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 199 --tsvFile $TCGAFMP_DATA_DIR/kirc/22mar13/kirc.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 200 --tsvFile $TCGAFMP_DATA_DIR/kirc/22mar13/kirc.seq.22mar13.TP.tsv

python ./run_pwRK2.py --pvalue 2. --one 285 --tsvFile $TCGAFMP_DATA_DIR/luad/22mar13/luad.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 286 --tsvFile $TCGAFMP_DATA_DIR/luad/22mar13/luad.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 287 --tsvFile $TCGAFMP_DATA_DIR/luad/22mar13/luad.seq.22mar13.TP.tsv

python ./run_pwRK2.py --pvalue 2. --one 298 --tsvFile $TCGAFMP_DATA_DIR/lusc/22mar13/lusc.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 299 --tsvFile $TCGAFMP_DATA_DIR/lusc/22mar13/lusc.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 300 --tsvFile $TCGAFMP_DATA_DIR/lusc/22mar13/lusc.seq.22mar13.TP.tsv

python ./run_pwRK2.py --pvalue 2. --one 310 --tsvFile $TCGAFMP_DATA_DIR/ov/22mar13/ov.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 311 --tsvFile $TCGAFMP_DATA_DIR/ov/22mar13/ov.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 312 --tsvFile $TCGAFMP_DATA_DIR/ov/22mar13/ov.seq.22mar13.TP.tsv

python ./run_pwRK2.py --pvalue 2. --one 285 --tsvFile $TCGAFMP_DATA_DIR/read/22mar13/read.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 286 --tsvFile $TCGAFMP_DATA_DIR/read/22mar13/read.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 287 --tsvFile $TCGAFMP_DATA_DIR/read/22mar13/read.seq.22mar13.TP.tsv

python ./run_pwRK2.py --pvalue 2. --one 373 --tsvFile $TCGAFMP_DATA_DIR/ucec/22mar13/ucec.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 374 --tsvFile $TCGAFMP_DATA_DIR/ucec/22mar13/ucec.seq.22mar13.TP.tsv
python ./run_pwRK2.py --pvalue 2. --one 375 --tsvFile $TCGAFMP_DATA_DIR/ucec/22mar13/ucec.seq.22mar13.TP.tsv

