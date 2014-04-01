#!/bin/bash

if [ $# -ne 1 ]
then

	echo "Usage: `basename $0` MAF_FILE"
	
else
	
	echo " "
	echo " Entrez_Gene_Id "
	cut -f1 $1 | sort | uniq -c | sort -rn | head -21
	cut -f1 $1 | sort | uniq -c | wc -l

	echo " "
	echo " Center "
	cut -f3 $1 | sort | uniq -c | sort -rn | head | grep -v "^      1 "

	echo " "
	echo " NCBI_Build "
	cut -f4 $1 | sort | uniq -c | sort -rn | head | grep -v "^      1 "

	echo " " 
	echo " Variant_Classification "
	cut -f9 $1 | sort | uniq -c | sort -rn | head | grep -v "^      1 "

	echo " "
	echo " Variant_Type "
	cut -f10 $1 | sort | uniq -c | sort -rn | head | grep -v "^      1 "

	echo " "
	echo " dbSNP_RS "
	cut -f14 $1 | sort | uniq -c | sort -rn | head -5 | grep -v "^      1 "

	echo " "
	echo " dbSNP_Val_Status "
	cut -f15 $1 | sort | uniq -c | sort -rn | head -5 | grep -v "^      1 "

	echo " "
	echo " # of unique tumor TCGA samples "
	cut -f16 $1 | sort | uniq -c | grep "TCGA\-" | wc -l

	echo " # of unique tumor TCGA patients "
	cut -f16 $1 | sort | cut -c-13 | uniq -c | grep "TCGA\-" | wc -l

	echo " "
	echo " # of unique normal TCGA samples "
	cut -f17 $1 | sort | uniq -c | grep "TCGA\-" | wc -l

	echo " # of unique normal TCGA patients "
	cut -f17 $1 | sort | cut -c-13 | uniq -c | grep "TCGA\-" | wc -l

	echo " "
	echo " Verification_Status "
	cut -f24 $1 | sort | uniq -c | sort -rn | head | grep -v "^      1 "

	echo " "
	echo " Validation_Status "
	cut -f25 $1 | sort | uniq -c | sort -rn | head | grep -v "^      1 "

	echo " "
	echo " Validation_Method "
	cut -f29 $1 | sort | uniq -c | sort -rn | head | grep -v "^      1 "

	echo " "
	echo " Mutation_Status "
	cut -f26 $1 | sort | uniq -c | sort -rn | head | grep -v "^      1 "

	echo " "
	echo " Sequence_Source "
	cut -f28 $1 | sort | uniq -c | sort -rn | head | grep -v "^      1 "

fi
