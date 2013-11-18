#!/bin/bash

if [ -z $MAF_REFERENCES_DIR ]; then      # -n tests to see if the argument is non empty
        echo "!! Reference directory not defined! Aborting."
        exit
fi

if [ -z $MAF_TOOLS_DIR ]; then      # -n tests to see if the argument is non empty
        echo "!! Tools folder not defined! Aborting."
        exit
fi

referenceFolder="$MAF_REFERENCES_DIR"
toolsFolder="$MAF_TOOLS_DIR"

echo
echo update ANNOVAR 
cd $toolsFolder
wget http://www.openbioinformatics.org/annovar/download/annovar.latest.tar.gz
tar -zxvf annovar.latest.tar.gz
cd $toolsFolder/annovar
chmod 777 $toolsFolder/annovar

echo
echo download UCSC knownGene files
humandbFolder=$referenceFolder/HumanDB
./annotate_variation.pl -downdb -buildver hg18 knownGene $humandbFolder
./annotate_variation.pl -downdb -buildver hg19 knownGene $humandbFolder


