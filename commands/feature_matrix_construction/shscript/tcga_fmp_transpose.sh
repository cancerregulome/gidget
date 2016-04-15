#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


if [ $# -ne 1 ]
then

	echo "Usage: `basename $0` INPUT_FILE"
	
else
	
	in_file=$1

	awk 'BEGIN {FS=OFS="\t"}
	{
	for (i=1;i<=NF;i++)
	{
	 arr[NR,i]=$i;
	 if(big <= NF)
	  big=NF;
	 }
	}
	
	END {
	  for(i=1;i<=big;i++)
	   {
	    for(j=1;j<=NR;j++)
	    {
	     printf("%s%s",arr[j,i], (j==NR ? "" : OFS));
	    }
	    print "";
	   }
	}' $in_file

fi

