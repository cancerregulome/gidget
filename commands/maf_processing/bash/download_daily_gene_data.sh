#!/bin/bash
# Cronjob for downloading reference data against 

if [ -z $MAF_REFERENCES_DIR ]; then 	# -n tests to see if the argument is non empty
	echo "!! Reference directory not defined! Aborting."
	exit
fi

if [ -z $MAF_SCRIPTS_DIR ]; then 	# -n tests to see if the argument is non empty
	echo "!! Script directory not defined! Aborting."
	exit
fi

cd "$MAF_REFERENCES_DIR"

rm -rf gene2accession*
rm -rf gene2refseq* 
rm -rf Homo_sapiens.gene_info*
rm -rf gene_refseq_uniprotkb_collab*

curl -O ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2accession.gz
curl -O ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2refseq.gz
curl -O ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz
curl -O ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_refseq_uniprotkb_collab.gz

gunzip gene2accession.gz
gunzip gene2refseq.gz
gunzip Homo_sapiens.gene_info.gz
gunzip gene_refseq_uniprotkb_collab.gz

rm -rf idmapping_selected.tab*
rm -rf uniprot_sprot_human*
rm -rf uniprot_trembl_human*
rm -rf uniprot_sprot_varsplic.fasta*
rm -rf uniprot_sec_ac.txt
curl -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/idmapping_selected.tab.gz
curl -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_sprot_human.dat.gz
curl -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_trembl_human.dat.gz
curl -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot_varsplic.fasta.gz
curl -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/docs/sec_ac.txt
mv sec_ac.txt uniprot_sec_ac.txt
cp uniprot_sec_ac.txt uniprot_sec_ac.txt.orig

#this file now has a header line
cp Homo_sapiens.gene_info Homo_sapiens.gene_info.orig
sed '1d' Homo_sapiens.gene_info > test
mv test Homo_sapiens.gene_info

gunzip idmapping_selected.tab.gz
gunzip uniprot_sprot_human.dat.gz
gunzip uniprot_trembl_human.dat.gz 
gunzip uniprot_sprot_varsplic.fasta.gz

# Use the above resources to map genes to uniprot protein accessions
#sh "$MAF_SCRIPTS_DIR/bash/prepareEntrezGeneUniprotReferences.sh"

