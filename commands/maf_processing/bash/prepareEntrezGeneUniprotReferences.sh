#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAMAF_ROOT_DIR}/../../gidget/util/env.sh


if [ -z $TCGAMAF_REFERENCES_DIR ]; then      # -n tests to see if the argument is non empty
        echo "!! Reference directory not defined! Aborting."
        exit
fi

if [ -z $TCGAMAF_SCRIPTS_DIR ]; then      # -n tests to see if the argument is non empty
        echo "!! Script folder not defined! Aborting."
        exit
fi

if [ -z $TCGAMAF_PYTHON_BINARY ]; then      # -n tests to see if the argument is non empty
        echo "!! Python binary not defined! Aborting."
        exit
fi

# NCBI reference data 
gene2refseq=$TCGAMAF_REFERENCES_DIR/gene2refseq
refseq2uniprot=$TCGAMAF_REFERENCES_DIR/gene_refseq_uniprotkb_collab
gene_refseq_uniprotkb_collab=$TCGAMAF_REFERENCES_DIR/gene_refseq_uniprotkb_collab
geneInfo=$TCGAMAF_REFERENCES_DIR/Homo_sapiens.gene_info

# From HUGO
hgnc2uniprot=$TCGAMAF_REFERENCES_DIR/hgnc_names_and_aliases_to_uniprot.txt

# Uniprot reference data
uniprot_idmapping=$TCGAMAF_REFERENCES_DIR/idmapping_selected.tab
uniprot_sprot_human=$TCGAMAF_REFERENCES_DIR/uniprot_sprot_human.dat
uniprot_trembl_human=$TCGAMAF_REFERENCES_DIR/uniprot_trembl_human.dat


echo
date

#hgnc2uniprot download has been changed to include approved symbols, previous symbols, synonyms, and uniprot IDs
echo
echo processing hgnc2uniprot file $hgnc2uniprot
echo grab geneID, gene Symbol and gene Synonyms
gene_info_subset=$TCGAMAF_REFERENCES_DIR/gene_info_subset
gene2uniprot=$TCGAMAF_REFERENCES_DIR/gene2uniprot
echo "cut -d' ' -f2,3,5 $geneInfo > $gene_info_subset"
cut -d'	' -f2,3,5 $geneInfo > $gene_info_subset
echo "build $gene2uniprot"
echo scripts in: $TCGAMAF_SCRIPTS_DIR
echo "$TCGAMAF_PYTHON_BINARY ${TCGAMAF_SCRIPTS_DIR}/python/createGene2Uniprot.py -geneInfo $gene_info_subset -hgnc2uniprot $hgnc2uniprot -output $gene2uniprot"
$TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/createGene2Uniprot.py -geneInfo $gene_info_subset -hgnc2uniprot $hgnc2uniprot -output $gene2uniprot

echo
echo processing uniprot idmapping file $uniprot_idmapping
echo grab uniprotkb-ac and geneid for human 
uniprot2gene=$TCGAMAF_REFERENCES_DIR/uniprot2gene
awk 'BEGIN{FS="\t"}\
     {if($14=9606) {\
        print $1,"\t",$3 }\
     }' $uniprot_idmapping > $uniprot2gene 
echo update $gene2uniprot by adding more uniprot ids to the file using $uniprot2gene  
echo "$TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/updateGene2Uniprot_with_uniprotIDMapping.py -uniprot2gene $uniprot2gene -gene2uniprot $gene2uniprot -output $gene2uniprot.temp"
$TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/updateGene2Uniprot_with_uniprotIDMapping.py -uniprot2gene $uniprot2gene -gene2uniprot $gene2uniprot -output $gene2uniprot.temp
echo "mv $gene2uniprot.temp $gene2uniprot"
mv $gene2uniprot.temp $gene2uniprot

echo
echo processing $uniprot_sprot_human 
echo grab accession, gene symbol and id
uniprot_sprot_human_subset=${uniprot_sprot_human}_subset
awk '{if($1=="ID" || $1=="AC" || $1=="GN" || ($1=="DR" && match($2,"GeneID;"))){\
	print $0;}\
     }' $uniprot_sprot_human > $uniprot_sprot_human_subset

#do we really need TREMBL?*****
echo
echo processing $uniprot_trembl_human
echo grab accession, gene symbol and id
uniprot_trembl_human_subset=${uniprot_trembl_human}_subset
awk '{if($1=="ID" || $1=="AC" || $1=="GN" || ($1=="DR" && match($2,"GeneID;"))){\
        print $0;}\
     }' $uniprot_trembl_human > $uniprot_trembl_human_subset

echo
echo update $gene2uniprot by adding more uniprot ids to the file using sprot and trembl
echo "$TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/updateGene2Uniprot_with_sprot_trembl.py -uniprot_human $uniprot_human -gene2uniprot $gene2uniprot -output $gene2uniprot.temp"
$TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/updateGene2Uniprot_with_sprot_trembl.py -uniprot_sprot_human $uniprot_sprot_human_subset -uniprot_trembl_human $uniprot_trembl_human_subset -gene2uniprot $gene2uniprot -output_sprot $gene2uniprot.sprot -output_trembl $gene2uniprot.trembl

echo
echo create uniprot sprot and trembl isoform1 sequence files
uniprot_isoform=$TCGAMAF_REFERENCES_DIR/uniprot_sprot_varsplic.fasta
isoform1_sprot=$TCGAMAF_REFERENCES_DIR/isoform1.sprot
isoform1_trembl=$TCGAMAF_REFERENCES_DIR/isoform1.trembl
echo "$TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/createUniProt_ISOForm1_Sequence_File.py -uniprot_sprot_human $uniprot_sprot_human -uniprot_trembl_human $uniprot_trembl_human -uniprot_isoform $uniprot_isoform -output_sprot $isoform1_sprot -output_trembl $isoform1_trembl"
$TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/createUniProt_ISOForm1_Sequence_File.py -uniprot_sprot_human $uniprot_sprot_human -uniprot_trembl_human $uniprot_trembl_human -uniprot_isoform $uniprot_isoform -output_sprot $isoform1_sprot -output_trembl $isoform1_trembl

#using UCSC known genes
echo
echo map transcript id to uniprot id
knownGene=$TCGAMAF_REFERENCES_DIR/HumanDB/hg18_kgXref.txt
cut -d'	' -f1,3 $knownGene | awk '{if($2 != "") {print $0}}' > $TCGAMAF_REFERENCES_DIR/knowngene_to_protein
knownGene=$TCGAMAF_REFERENCES_DIR"/HumanDB/hg19_kgXref.txt"
cut -d'	' -f1,3 $knownGene | awk '{if($2 != "") {print $0}}' >> $TCGAMAF_REFERENCES_DIR/knowngene_to_protein

echo
echo remove temporary files
rm $gene_info_subset
rm $uniprot2gene

echo
echo change permissions to 777
chmod 777 $TCGAMAF_REFERENCES_DIR/*

echo 
date
