#!/bin/bash

# every TCGA MAF script should start with these lines:
: ${TCGAMAF_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA MAF directory"}
source ${TCGAFMP_ROOT_DIR}/bash/tcga_maf_util.sh


echo $TGCGAMAF_DATA_DIR

gene2uniprot_sprot=$TCGAMAF_REFERENCES_DIR/gene2uniprot.sprot
gene2uniprot_trembl=$TCGAMAF_REFERENCES_DIR/gene2uniprot.trembl

mafInputList=${1:-$TCGAMAF_DATA_DIR/sept24_thca}
newMafInputList=${mafInputList}.ncmlst
outputFolder=${2:-$TCGAMAF_DATA_DIR}
maf_unmapped_log=$TCGAMAF_DATA_DIR/UNMAPPED.log

maf_ncm=""
echo STEP 0: decomment MAF files
rm $newMafInputList
echo > $newMafInputList
while read line
do
    $TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/preprocess_maf.py $line ${line}.ncm
    echo ${line}.ncm >> $newMafInputList
    maf_ncm=${line}.ncm
done < $mafInputList
mafInputList=$newMafInputList

####################################################
echo STEP 1: update MAF files by adding uniprot id
echo
echo "$TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/updateMAF_addUniprotID.py -mafInputList $mafInputList -gene2uniprot_sprot $gene2uniprot_sprot -gene2uniprot_trembl $gene2uniprot_trembl -output $outputFolder > $maf_unmapped_log"
$TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/updateMAF_addUniprotID.py -mafInputList $mafInputList -gene2uniprot_sprot $gene2uniprot_sprot -gene2uniprot_trembl $gene2uniprot_trembl -output $outputFolder > $maf_unmapped_log

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
  maf_uniprot_file=${line}.with_uniprot
  maf_uniprot_file_orig=${line}.with_uniprot.orig
  cp $maf_uniprot_file $maf_uniprot_file_orig
  maf_uniprot=$maf_uniprot_file
done < $mafInputList
echo Your file is $maf_uniprot

####################################################
echo
echo STEP2: update MAF files by annotating CDS/protein changes with ANNOVAR output 
annovarExecutable=$$/annovar
humandbFolder=$TCGAMAF_REFERENCES_DIR/HumanDB
knowngene2protein=$TCGAMAF_REFERENCES_DIR/knowngene_to_protein
refseq2uniprot=$TCGAMAF_REFERENCES_DIR/gene_refseq_uniprotkb_collab
uniprot_sprot_human=$TCGAMAF_REFERENCES_DIR/uniprot_sprot_human.dat
uniprot_trembl_human=$TCGAMAF_REFERENCES_DIR/uniprot_trembl_human.dat
uniprot_sec=$TCGAMAF_REFERENCES_DIR/uniprot_sec_ac.txt
isoprot_seq=$TCGAMAF_REFERENCES_DIR/isoform1.sprot

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
    $TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/simplify_maf.py $line ${line}.annovar_input ${line}.buildID
	#awk 'BEGIN{FS="\t";OFS="\t"}NR>1{print $5,$6,$7,$11,$13,"line"NR,$1,$2,$10,$12}' $line > $line".annovar_input"
	buildver=`cat ${line}.buildID`
    
	knownGene=$humandbFolder/${buildver}_knownGene.txt
	knownGeneMrna=$humandbFolder/${buildver}_knownGeneMrna.fa
    
	echo Format the above short version of MAF to the required ANNOVAR input
	$TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/updateAnnovarInput.py -input ${line}.annovar_input -output $outputFolder

	echo Execute ANNOVAR
        # some parameters may need to change from the defaults depending on the MAF data @see http://www.openbioinformatics.org/annovar/annovar_gene.html; no separate flag is used; splicing_threshold and neargene are at their default values
	splicing_threshold=2
	neargene=1000
	echo $annovarExecutable/annotate_variation.pl ${line}.annovar_input --buildver $buildver -splicing_threshold $splicing_threshold -neargene $neargene -dbtype knowngene $humandbFolder
	$annovarExecutable/annotate_variation.pl ${line}.annovar_input --buildver $buildver -splicing_threshold $splicing_threshold -neargene $neargene -dbtype knowngene $humandbFolder
	
        annovarExonicOutput=${line}.annovar_input.exonic_variant_function
	#annovarExonicOutput_orig=$line".annovar_input.exonic_variant_function_orig"

	#echo copying ANNOVAR output file for safekeeping
	#cp $annovarExonicOutput $annovarExonicOutput_orig

	echo filtering ANNOVAR output for default isoform
	
	echo "$TCGAMAF_SCRIPTS_DIR/perl/uniprot_lookup.pl $annovarExonicOutput $gene2uniprot_sprot $knowngene2protein $uniprot_sec $maf_uniprot $isoprot_seq > $annovarExonicOutput.isoform_filter"

	$TCGAMAF_SCRIPTS_DIR/perl/uniprot_lookup.pl $annovarExonicOutput $gene2uniprot_sprot $knowngene2protein $uniprot_sec $maf_uniprot $isoprot_seq > $annovarExonicOutput".isoform_filter"
	annovarExonicOutput=${line}.annovar_input.exonic_variant_function.isoform_filter
	annovarExonicOutput_orig=${line}.annovar_input.exonic_variant_function.isoform_filter_orig

	echo copying ANNOVAR isoform output file for safekeeping
	cp $annovarExonicOutput $annovarExonicOutput_orig

	#echo get coding changes for non SNP mutations
	#$TCGAMAF_SCRIPTS_DIR/perl/coding_change.pl $annovarExonicOutput $knownGene $knownGeneMrna > $annovarExonicOutput".non_snp.protein_sequence"
	#turned this off - not sure it really is doing anything
	#echo Update ANNOVAR output such as: 1.add coding changes for non SNP, 2.adding normal nucleotides for DNP mutations
	#$TCGAMAF_PYTHON_BINARY $TCGAMAF_SCRIPTS_DIR/python/updateAnnovarOutput.py -annovaroutput $annovarExonicOutput

	echo Grab the required fields from ANNOVAR output
	cut -d'	' -f1-3 $annovarExonicOutput > ${line}.annovar_exonic_variant_function
        cut -d'	' -f1,2,3,8 ${line}.annovar_input.variant_function > ${line}.annovar_variant_function

	echo Update MAF that already has uniprot accessions being added, See STEP 1
	uniprot_sprot_isoform1=$TCGAMAF_REFERENCES_DIR/isoform1.sprot
	uniprot_trembl_isoform1=$TCGAMAF_REFERENCES_DIR/isoform1.trembl

	#file processing - problem here with isoform filtering - turned off filtering in this python script
	$TCGAMAF_PYTHON_BINARY $scriptFolder/python/updateMAF_annotateMutation.py -mafWithUniprotID ${line}.with_uniprot -knowngene2protein $knowngene2protein -refseq2uniprot $refseq2uniprot \
	-uniprot_sprot_human $uniprot_sprot_human -uniprot_trembl_human $uniprot_trembl_human -uniprot_sprot_isoform1 $uniprot_sprot_isoform1 -uniprot_trembl_isoform1 $uniprot_trembl_isoform1 \
	-output $outputFolder > ${line}.annotation_errors
	
	#echo Remove temporary files
	#rm $line".annovar_input"
	#rm $line".annovar_exonic_variant_function"
	#rm $line".annovar_variant_function"	

done < $mafInputList

echo
date
echo Update Completed!



