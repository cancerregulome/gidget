#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable env.sh

# TODO:FILE_LAYOUT:EXPLICIT
## python ./findMutHotPoints.py /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/stad/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_STAD.IlluminaGA_DNASeq.Level_2.0.4.0/PR_TCGA_STAD_PAIR_Capture_All_Pairs_QCPASS_v4.aggregated.capture.tcga.uuid.somatic.maf stad1

# TODO:FILE_LAYOUT:EXPLICIT
python ./findMutHotPoints.py /titan/cancerregulome9/workspaces/STAD_Snapshot_Files_For_Upload/Mutations/20131025_FullSTADMAFandPRfilewithSTRELKAIndels/STAD_MAF_with_STRELKA.clean_barcode.maf stad >& run_hotpoints_stad.log13

