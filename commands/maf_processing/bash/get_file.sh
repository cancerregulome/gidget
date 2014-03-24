#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAFMP_ROOT_DIR}/bash/tcga_maf_util.sh


echo $MAF_DATA_DIR
if [ -z $MAF_DATA_DIR ]; then      # -n tests to see if the argument is non empty
        echo "!! Data directory not defined! Aborting."
        exit
fi

if [ -z $MAF_REFERENCES_DIR ]; then      # -n tests to see if the argument is non empty
        echo "!! Reference directory not defined! Aborting."
        exit
fi

if [ -z $MAF_TOOLS_DIR ]; then      # -n tests to see if the argument is non empty
        echo "!! Tools folder not defined! Aborting."
        exit
fi

if [ -z $MAF_SCRIPTS_DIR ]; then      # -n tests to see if the argument is non empty
        echo "!! Script folder not defined! Aborting."
        exit
fi

if [ -z $MAF_PYTHON_BINARY ]; then      # -n tests to see if the argument is non empty
        echo "!! Python binary not defined! Aborting."
        exit
fi

dataFolder="$MAF_DATA_DIR"
referenceFolder="$MAF_REFERENCES_DIR"
toolsFolder="$MAF_TOOLS_DIR"
scriptFolder="$MAF_SCRIPTS_DIR"
python="$MAF_PYTHON_BINARY"

gene2uniprot_sprot=$referenceFolder/gene2uniprot.sprot
gene2uniprot_trembl=$referenceFolder/gene2uniprot.trembl

mafInputList=${1:-${dataFolder}/mar26_COADREAD}
newMafInputList=$mafInputList".ncmlst"
outputFolder=${2:-$dataFolder}
maf_unmapped_log=$dataFolder/UNMAPPED.log

echo STEP 0: decomment MAF files
rm $newMafInputList
echo > $newMafInputList
while read line
do
    $python $scriptFolder/python/preprocess_maf.py $line $line".ncm"
    echo $line".ncm" >> $newMafInputList
done < $mafInputList
mafInputList=$newMafInputList

####################################################
echo STEP 1: update MAF files by adding uniprot id
echo
echo "$python $scriptFolder/python/updateMAF_addUniprotID.py -mafInputList $mafInputList -gene2uniprot_sprot $gene2uniprot_sprot -gene2uniprot_trembl $gene2uniprot_trembl -output $outputFolder > $maf_unmapped_log"
"$python" "$scriptFolder/python/updateMAF_addUniprotID.py" -mafInputList "$mafInputList" -gene2uniprot_sprot "$gene2uniprot_sprot" -gene2uniprot_trembl "$gene2uniprot_trembl" -output "$outputFolder" > "$maf_unmapped_log"

while read line
do
  if [ -z $line ]
    then
        echo "Nothing to do for a blank line."
        continue
    fi
  echo Need to get a copy of the MAF uniprot file
  map_uniprot_file=$line."with_uniprot"
  map_uniprot_file_orig=$line".with_uniprot.orig"
  cp $map_uniprot_file $map_uniprot_file_orig
done < $mafInputList


