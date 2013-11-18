#!/bin/bash
referenceFolder="$MAF_REFERENCES_DIR"
#using UCSC known genes
echo
echo map transcipt id to uniprot id
knownGene=$referenceFolder"/HumanDB/hg18_knownGene.txt"
cut -d'	' -f1,11 $knownGene | awk '{if($2 != "") {print $0}}' > $referenceFolder"/knowngene_to_protein"
#knownGene=$referenceFolder"/HumanDB/hg19_knownGene.txt"
#cut -d'	' -f1,11 $knownGene | awk '{if($2 != "") {print $0}}' >> $referenceFolder"/knowngene_to_protein"
