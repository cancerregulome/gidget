#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAMAF_ROOT_DIR}/../../gidget/util/env.sh


# Cronjob for downloading reference data against 

if [ -z $TCGAMAF_REFERENCES_DIR ]; then 	# -n tests to see if the argument is non empty
	echo "!! Reference directory not defined! Aborting."
	exit
fi

if [ -z $TCGAMAF_SCRIPTS_DIR ]; then 	# -n tests to see if the argument is non empty
	echo "!! Script directory not defined! Aborting."
	exit
fi

cd "$TCGAMAF_REFERENCES_DIR"

#rm -rf gene2accession*
#rm -rf gene2refseq* 
#rm -rf Homo_sapiens.gene_info*
#rm -rf gene_refseq_uniprotkb_collab*

# save files with original timestamps

curl -C - -O --remote-time ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2accession.gz
curl -C - -O --remote-time ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2refseq.gz
curl -C - -O --remote-time ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz
curl -C - -O --remote-time ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_refseq_uniprotkb_collab.gz


# Store original timestamps for NCBI's Gene for archival purposes.
# NCBI's Gene database is potentially updated daily, so we use the file creation time
# for bookkeeping.
# see http://www.ncbi.nlm.nih.gov/books/NBK3841/#EntrezGene.How_Data_Are_Maintained

for file in gene2accession gene2refseq Homo_sapiens.gene_info gene_refseq_uniprotkb_collab
do

	# add file's timestamp to the name as part of the string:
	# newfilename=$file-`stat -c %y $file.gz | cut -d ' ' -f1 | sed 's/-//g'`.gz
	# mv $file.gz $newfilename

	# gunzip $newfilename
	echo gunzip $file
	gunzip $file
done


# remove the first header line from this file;
# leave the original with an ".orig" suffix per original script

# TODO: for ease of maintaining archives (which could be downloaded again),
# do not modify file and look into modifying downstream tools to ignore the header line,
# instead.
echo removing first line
sed -iorig '1d' Homo_sapiens.gene_info


# TODO: move these into per-uniprot-release directories

#rm -rf idmapping_selected.tab*
#rm -rf uniprot_sprot_human*
#rm -rf uniprot_trembl_human*
#rm -rf uniprot_sprot_varsplic.fasta*
#rm -rf uniprot_sec_ac.txt
curl -C - -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/idmapping_selected.tab.gz
curl -C - -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_sprot_human.dat.gz
curl -C - -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_trembl_human.dat.gz
curl -C - -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot_varsplic.fasta.gz
curl -C - -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/docs/sec_ac.txt
mv sec_ac.txt uniprot_sec_ac.txt
cp uniprot_sec_ac.txt uniprot_sec_ac.txt.orig # TODO is this still necessary? probably there for manual version
# before next line's automation:

# removing header; only printing lines with Secondary AC[accession number]<space(s)>Primary AC
sed -r -n -i '/^[a-zA-Z0-9]+[ \t]+[a-zA-Z0-9]+$/p' uniprot_sec_ac.txt

# get the uniprot release name
curl -C - -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/relnotes.txt
uniprotversion=`head -n 1 relnotes.txt | cut -d ' ' -f3`
rm -f relnotes.txt

# rename files with uniprot version and uncompress
for uniprotfile in idmapping_selected.tab uniprot_sprot_human.dat uniprot_trembl_human.dat uniprot_sprot_varsplic.fasta
do
	#newuniprotfilename=$file-$uniprotversion.gz
	#mv $uniprotfile.gz $newuniprotfilename
	#gunzip $newuniprotfilename
        echo gunzip $uniprotfile.gz
	gunzip $uniprotfile.gz
done


# TODO: make sure that downstream scripts are okay with the versioned filenames.

# Use the above resources to map genes to uniprot protein accessions
#sh "$MAF_SCRIPTS_DIR/bash/prepareEntrezGeneUniprotReferences.sh"

