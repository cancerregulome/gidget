#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAMAF_ROOT_DIR}/../../gidget/util/env.sh


if [ -z $TCGAMAF_REFERENCES_DIR ]; then 	# -n tests to see if the argument is non empty
	echo "!! Reference directory not defined! Aborting."
	exit
fi

if [ -z $TCGAMAF_SCRIPTS_DIR ]; then 	# -n tests to see if the argument is non empty
	echo "!! Script directory not defined! Aborting."
	exit
fi

cd "$TCGAMAF_REFERENCES_DIR"

curl 'http://www.genenames.org/cgi-bin/download?col=gd_app_sym&col=gd_prev_sym&col=gd_aliases&col=md_prot_id&status=Approved&status=Entry+Withdrawn&status_opt=2&where=&order_by=gd_hgnc_id&format=text&limit=&hgnc_dbtag=on&submit=submit' > hgnc_names_and_aliases_to_uniprot.txt

sed -i.bak  s_\(supplied\ by\ UniProt\)__ hgnc_names_and_aliases_to_uniprot.txt
