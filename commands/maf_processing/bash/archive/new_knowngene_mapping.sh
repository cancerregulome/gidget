#!/bin/bash
referenceFolder="$MAF_REFERENCES_DIR"
#using UCSC known genes
echo
echo map transcript id to uniprot id
knownGene=$referenceFolder"/HumanDB/hg18_kgXref.txt"
cut -d'	' -f1,3 $knownGene | awk '{if($2 != "") {print $0}}' > $referenceFolder"/knowngene_to_protein"
knownGene=$referenceFolder"/HumanDB/hg19_kgXref.txt"
cut -d'	' -f1,3 $knownGene | awk '{if($2 != "") {print $0}}' >> $referenceFolder"/knowngene_to_protein"
