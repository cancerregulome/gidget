
## now we assume that in the input specified directory, we have
## one enormous file called post_proc_all.tsv and then all of 
## the feature type "pair" files, eg
##	post_proc_all.NMETH.NRPPA.tmp
##	post_proc_all.NCNVR.NGEXP.tmp
## etc ...

d=$1

echo " "
echo " "
echo " processing temp files in $1 "

date

echo " sorting the individual files ... "
for t in $d/post_proc_all.*.*.tmp
   do
	echo $t
        sort -grk 5 --temporary-directory=/titan/cancerregulome9/TCGA/pw_scratch/ $t >& $t.sort
   done

echo " concatenating at most 1 million pairs of each type ... "
rm -fr $d/post_proc_all.short
echo " " > $d/post_proc_all.short
for t in $d/post_proc_all.*.*.tmp.sort
    do
        echo $t
	head -1000000 $t >> $d/post_proc_all.short
    done

echo " now sorting the short concatenation ... "
rm -fr $d/post_proc_all.short.sort
sort -grk 5 --temporary-directory=/titan/cancerregulome9/TCGA/pw_scratch/ $d/post_proc_all.short >& $d/post_proc_all.short.sort

date

echo " deleting .tmp and .tmp.sort and .pw files "
rm -fr $d/post_proc_all.*.*.tmp.sort
rm -fr $d/post_proc_all.*.*.tmp
## rm -fr $d/*.pw 
## rm -fr $d/runList.txt

echo " and last but not least, removing unmapped features ... "
python $TCGAFMP_ROOT_DIR/main/filterPWPV.py $d/post_proc_all.short.sort 

grep -iv "pathway" $d/post_proc_all.short.sort.mapped | grep -v "	nan	" >& $d/post_proc_all.short.sort.mapped.noPathway

date

echo " "
echo " "

