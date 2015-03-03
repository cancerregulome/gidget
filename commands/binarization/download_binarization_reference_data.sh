#!/bin/bash

# every TCGA Binarization script should start with these lines:
: ${GIDGET_SOURCE_ROOT:?" environment variable must be set and non-empty; defines the path to the gidget code directory"}
source $GIDGET_SOURCE_ROOT/gidget/util/env.sh


cd "$TCGABINARIZATION_REFERENCES_DIR"





# A census of human transcription factors: function, expression and evolution
# Juan M Vaquerizas, Sarah K Kummerfeld, Sarah A Teichmann, Nicholas M Luscombe
#

# http://www.nature.com/nrg/journal/v10/n4/suppinfo/nrg2538.html


INTERPRO_TSV_FILENAME=interpro_domains_vaquerizas_nature_2009.tsvINTERPRO_TSV_FILENAME=interpro_domains_vaquerizas_nature_2009.tsv
# Supplementary Table 1
# List of Interpro DNA-binding domains and families used to characterise the human TFs repertoire.

curl http://www.nature.com/nrg/journal/v10/n4/extref/nrg2538-s2.txt > ${INTERPRO_TSV_FILENAME} 

cp ${INTERPRO_TSV_FILENAME} ${INTERPRO_TSV_FILENAME}.original
dos2unix ${INTERPRO_TSV_FILENAME}

# strip header
sed -r -n  -i '/^[a-zA-Z0-9]+\t+[a-zA-Z0-9]+$/p' ${INTERPRO_TSV_FILENAME}


# TODO: check
# http://www.ebi.ac.uk/interpro/download.html
