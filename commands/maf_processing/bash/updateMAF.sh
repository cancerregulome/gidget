#!/bin/bash

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

mafInputList=${1:-${dataFolder}/sept24_thca}
newMafInputList=$mafInputList".ncmlst"
outputFolder=${2:-$dataFolder}
maf_unmapped_log=$dataFolder/UNMAPPED.log

maf_ncm=""
echo STEP 0: decomment MAF files
rm $newMafInputList
echo > $newMafInputList
while read line
do
    $python $scriptFolder/python/preprocess_maf.py $line $line".ncm"
    echo $line".ncm" >> $newMafInputList
    maf_ncm=$line".ncm"
done < $mafInputList
mafInputList=$newMafInputList

####################################################
echo STEP 1: update MAF files by adding uniprot id
echo
echo "$python $scriptFolder/python/updateMAF_addUniprotID.py -mafInputList $mafInputList -gene2uniprot_sprot $gene2uniprot_sprot -gene2uniprot_trembl $gene2uniprot_trembl -output $outputFolder > $maf_unmapped_log"
"$python" "$scriptFolder/python/updateMAF_addUniprotID.py" -mafInputList "$mafInputList" -gene2uniprot_sprot "$gene2uniprot_sprot" -gene2uniprot_trembl "$gene2uniprot_trembl" -output "$outputFolder" > "$maf_unmapped_log"

maf_uniprot=""
while read line
do
  if [ -z $line ]
    then
        echo "Nothing to do for a blank line."
        continue
    fi
  echo copying STEP1:MAF uniprot file

  #keeping a copy of uniprot file
  echo copying file with uniprot
  maf_uniprot_file=$line."with_uniprot"
  maf_uniprot_file_orig=$line".with_uniprot.orig"
  cp $maf_uniprot_file $maf_uniprot_file_orig
  maf_uniprot=$maf_uniprot_file
done < $mafInputList
echo Your file is $maf_uniprot

####################################################
echo
echo STEP2: update MAF files by annotating CDS/protein changes with ANNOVAR output 
annovarExecutable=$toolsFolder"/annovar"
humandbFolder=$referenceFolder"/HumanDB"
knowngene2protein=$referenceFolder/knowngene_to_protein
refseq2uniprot=$referenceFolder/gene_refseq_uniprotkb_collab
uniprot_sprot_human=$referenceFolder/uniprot_sprot_human.dat
uniprot_trembl_human=$referenceFolder/uniprot_trembl_human.dat
uniprot_sec=$referenceFolder/uniprot_sec_ac.txt
isoprot_seq=$referenceFolder/isoform1.sprot

while read line
do
	echo
	date
    if [ -z $line ]
    then
        echo "Nothing to do for a blank line."
        continue
    fi

	echo Create a short version of MAF
    #that previous line replacement is necessary to handle output that doesn't understand comment lines, which is everything
    $python $scriptFolder/python/simplify_maf.py $line $line".annovar_input" $line".buildID"
	#awk 'BEGIN{FS="\t";OFS="\t"}NR>1{print $5,$6,$7,$11,$13,"line"NR,$1,$2,$10,$12}' $line > $line".annovar_input"
	buildver=`cat $line".buildID"`
    
	knownGene=$humandbFolder"/"$buildver"_knownGene.txt"
	knownGeneMrna=$humandbFolder"/"$buildver"_knownGeneMrna.fa"
    
	echo Format the above short version of MAF to the required ANNOVAR input
	"$python" "$scriptFolder/python/updateAnnovarInput.py" -input $line".annovar_input" -output $outputFolder

	echo Execute ANNOVAR
        # some parameters may need to change from the defaults depending on the MAF data @see http://www.openbioinformatics.org/annovar/annovar_gene.html; no separate flag is used; splicing_threshold and neargene are at their default values
	splicing_threshold=2
	neargene=1000
	echo "$annovarExecutable/annotate_variation.pl "$line".annovar_input --buildver $buildver -splicing_threshold $splicing_threshold -neargene $neargene -dbtype knowngene $humandbFolder"
	$annovarExecutable/annotate_variation.pl $line".annovar_input" --buildver $buildver -splicing_threshold $splicing_threshold -neargene $neargene -dbtype knowngene $humandbFolder
	
        annovarExonicOutput=$line".annovar_input.exonic_variant_function"
	#annovarExonicOutput_orig=$line".annovar_input.exonic_variant_function_orig"

	#echo copying ANNOVAR output file for safekeeping
	#cp $annovarExonicOutput $annovarExonicOutput_orig

	echo filtering ANNOVAR output for default isoform
	
	echo "$scriptFolder/perl/uniprot_lookup.pl $annovarExonicOutput $gene2uniprot_sprot $knowngene2protein $uniprot_sec $maf_uniprot $isoprot_seq > $annovarExonicOutput.isoform_filter"

	$scriptFolder/perl/uniprot_lookup.pl $annovarExonicOutput $gene2uniprot_sprot $knowngene2protein $uniprot_sec $maf_uniprot $isoprot_seq > $annovarExonicOutput".isoform_filter"
	annovarExonicOutput=$line".annovar_input.exonic_variant_function.isoform_filter"
	annovarExonicOutput_orig=$line".annovar_input.exonic_variant_function.isoform_filter_orig"

	echo copying ANNOVAR isoform output file for safekeeping
	cp $annovarExonicOutput $annovarExonicOutput_orig

	#echo get coding changes for non SNP mutations
	#$scriptFolder/perl/coding_change.pl $annovarExonicOutput $knownGene $knownGeneMrna > $annovarExonicOutput".non_snp.protein_sequence"
	#turned this off - not sure it really is doing anything
	#echo Update ANNOVAR output such as: 1.add coding changes for non SNP, 2.adding normal nucleotides for DNP mutations
	#$python $scriptFolder/python/updateAnnovarOutput.py -annovaroutput $annovarExonicOutput

	echo Grab the required fields from ANNOVAR output
	cut -d'	' -f1-3 $annovarExonicOutput > $line".annovar_exonic_variant_function"
        cut -d'	' -f1,2,3,8 $line".annovar_input.variant_function" > $line".annovar_variant_function"	

	echo Update MAF that already has uniprot accessions being added, See STEP 1
	uniprot_sprot_isoform1=$referenceFolder/isoform1.sprot
	uniprot_trembl_isoform1=$referenceFolder/isoform1.trembl

	#file processing - problem here with isoform filtering - turned off filtering in this python script
	$python $scriptFolder/python/updateMAF_annotateMutation.py -mafWithUniprotID $line".with_uniprot" -knowngene2protein $knowngene2protein -refseq2uniprot $refseq2uniprot \
	-uniprot_sprot_human $uniprot_sprot_human -uniprot_trembl_human $uniprot_trembl_human -uniprot_sprot_isoform1 $uniprot_sprot_isoform1 -uniprot_trembl_isoform1 $uniprot_trembl_isoform1 \
	-output $outputFolder > $line".annotation_errors"
	
	#echo Remove temporary files
	#rm $line".annovar_input"
	#rm $line".annovar_exonic_variant_function"
	#rm $line".annovar_variant_function"	

done < $mafInputList

echo
date
echo Update Completed!



