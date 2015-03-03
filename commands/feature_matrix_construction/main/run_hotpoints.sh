#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/blca/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_BLCA.IlluminaGA_DNASeq.Level_2.0.3.0/PR_TCGA_BLCA_PAIR_Capture_All_Pairs_QCPASS_v3.aggregated.capture.tcga.uuid.somatic.maf blca
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/brca/gsc/genome.wustl.edu/illuminaga_dnaseq/mutations/genome.wustl.edu_BRCA.IlluminaGA_DNASeq.Level_2.5.3.0/genome.wustl.edu_BRCA.IlluminaGA_DNASeq.Level_2.5.3.0.somatic.maf brca
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/cesc/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_CESC.IlluminaGA_DNASeq.Level_2.0.5.0/PR_TCGA_CESC_PAIR_Capture_All_Pairs_QCPASS_v3.aggregated.capture.tcga.uuid.somatic.maf cesc
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/coad/gsc/hgsc.bcm.edu/illuminaga_dnaseq/mutations/hgsc.bcm.edu_COAD.IlluminaGA_DNASeq.Level_2.1.5.0/hgsc.bcm.edu_COAD.IlluminaGA_DNASeq.1.somatic.maf coad
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/gbm/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_GBM.IlluminaGA_DNASeq.Level_2.100.1.0/step4_gbm_liftover.aggregated.capture.tcga.uuid.maf2.4.migrated.somatic.maf gbm
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/hnsc/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_HNSC.IlluminaGA_DNASeq.Level_2.0.2.0/PR_TCGA_HNSC_PAIR_Capture_All_Pairs_QCPASS_v2.aggregated.capture.tcga.uuid.somatic.maf hnsc
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/kich/gsc/hgsc.bcm.edu/illuminaga_dnaseq/mutations/hgsc.bcm.edu_KICH.IlluminaGA_DNASeq.Level_2.1.2.0/hgsc.bcm.edu_KICH.IlluminaGA_DNASeq.1.somatic.maf kich
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/kirc/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_KIRC.IlluminaGA_DNASeq.Level_2.1.5.0/BI_and_BCM_1.4.aggregated.tcga.somatic.maf kirc
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/kirp/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_KIRP.IlluminaGA_DNASeq.Level_2.0.3.0/PR_TCGA_KIRP_PAIR_Capture_All_Pairs_QCPASS_v3.aggregated.capture.tcga.uuid.somatic.maf kirp
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/laml/gsc/genome.wustl.edu/illuminaga_dnaseq/mutations/genome.wustl.edu_LAML.IlluminaGA_DNASeq.Level_2.2.14.0/genome.wustl.edu_LAML.IlluminaGA_DNASeq.Level_2.2.13.0.somatic.maf laml
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/lgg/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_LGG.IlluminaGA_DNASeq.Level_2.0.3.0/PR_TCGA_LGG_PAIR_Capture_All_Pairs_QCPASS_v3.aggregated.capture.tcga.uuid.somatic.maf lgg
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/luad/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_LUAD.IlluminaGA_DNASeq.Level_2.0.4.0/PR_TCGA_LUAD_PAIR_Capture_All_Pairs_QCPASS_v3.aggregated.capture.tcga.uuid.somatic.maf luad
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/lusc/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_LUSC.IlluminaGA_DNASeq.Level_2.1.5.0/LUSC_Paper_v8.aggregated.tcga.somatic.maf lusc
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/ov/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_OV.IlluminaGA_DNASeq.Level_2.7.3.0/broad.mit.edu_OV.IlluminaGA_DNASeq.Level_2.7.somatic.maf ov
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/paad/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_PAAD.IlluminaGA_DNASeq.Level_2.0.3.0/PR_TCGA_PAAD_PAIR_Capture_All_Pairs_QCPASS_v3.aggregated.capture.tcga.uuid.somatic.maf paad
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/prad/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_PRAD.IlluminaGA_DNASeq.Level_2.1.3.0/PR-TCGA-Analysis_set.aggregated.tcga.somatic.maf prad
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/read/gsc/hgsc.bcm.edu/illuminaga_dnaseq/mutations/hgsc.bcm.edu_READ.IlluminaGA_DNASeq.Level_2.1.6.0/hgsc.bcm.edu_READ.IlluminaGA_DNASeq.1.somatic.maf read
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/skcm/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_SKCM.IlluminaGA_DNASeq.Level_2.1.5.0/skcm_clean_pairs.aggregated.capture.tcga.uuid.somatic.maf skcm
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/stad/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_STAD.IlluminaGA_DNASeq.Level_2.0.4.0/PR_TCGA_STAD_PAIR_Capture_All_Pairs_QCPASS_v4.aggregated.capture.tcga.uuid.somatic.maf stad
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/thca/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_THCA.IlluminaGA_DNASeq.Level_2.1.5.0/AN_TCGA_THCA_PAIR_Capture_ALLQC_14Aug2013_429.aggregated.capture.tcga.uuid.somatic.maf thca
python ./findMutHotPoints.py TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/ucec/gsc/genome.wustl.edu/illuminaga_dnaseq/mutations/genome.wustl.edu_UCEC.IlluminaGA_DNASeq.Level_2.1.7.0/genome.wustl.edu_UCEC.IlluminaGA_DNASeq.Level_2.1.7.somatic.maf ucec
