#!/bin/bash

export LD_LIBRARY_PATH=/tools/lib/
export TCGAFMP_ROOT_DIR=/users/sreynold/to_be_checked_in/TCGAfmp
export PYTHONPATH=$TCGAFMP_ROOT_DIR/pyclass:$TCGAFMP_ROOT_DIR/util:$PYTHONPATH

curDate=19feb13
snapshotName=dcc-snapshot
oneTumor=sarc

./fmp02B_L3_a.sh  $curDate $snapshotName $oneTumor >& fmp02B.$curDate.$snapshotName.$oneTumor.log

