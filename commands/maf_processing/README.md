#TCGA MAF pipeline

### What to do when you get a new MAF file ...

*But wait!* you might ask, *how do I know if I have a new MAF file?*

- If you are getting the MAF file from the DCC, then you can check like this:

    ```
$ cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/<tumor>/gsc/
$ ls -alt */*dna*/*/*/*.maf
    ```
and you can check the time stamp of the first MAF file listed -- usually you want to use the most recent one available, but sometimes an older one might have been "curated" or might be from a preferred sequencing center.
Sometimes the largest / most recent one is the one that is most likely to be of interest.

- On the other hand, you might have obtained a MAF file from a different
source.

We will use this SKCM MAF file as an example:
```
$TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/skcm/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_SKCM.IlluminaGA_DNASeq.Level_2.1.5.0/skcm_clean_pairs.aggregated.capture.tcga.uuid.somatic.maf
```

If you want to some basic information from this MAF such as the number of samples, the most frequently mutated genes, etc, there is a simple script called ```$TCGAFMP_ROOT_DIR/shscript/qMaf``` that you can use.  On this particular MAF file, it will report, for example, that the most frequently mutated genes (and the counts) are:

```
        1794 TTN
        1549 MUC16
         979 PCDHAC2
             etc ...
```
it will also let you know that there are 290341 called mutations, and of of these 171139 are Missense_Mutations, 93750 are Silent, 10596 are Nonsense_Mutations, 7600 are Splice_Site mutations, etc. Finally, it will
report that this MAF file contains mutations based on data from 346 unique 
tumor samples, 345 unique normal samples, and 344 unique patients.

Note that the above script can take several minutes to run on a very large
MAF file, so please be patient.

### Ok, so now that you have a new MAF file, what do you need to do next?

1. run Lisa's script(s)
	* TODO

2. run Brady's script(s)
	* TODO
	* The output from the binarization step is a very large tsv file containing binarized information about all mutated genes for all tumor samples referenced in the MAF file.


3. post-processing:
    1. copy the output of step #2 (not the "transpose" file) to ```$TCGAFMP_OUTPUTS/<tumor>/gnab/latest.gnab.txt```
    2. first post-processing step:

        ```
$ cd $TCGAFMP_ROOT_DIR/shscript
$ ./fmp03B_gnab_part.sh <tumor>
        ```
    3. next, features with very few 1's should be filtered out, for example:

        ```
$ cd $TCGAFMP_OUTPUTS/<tumor>/gnab/
$ python $TCGAFMP_ROOT_DIR/main/highVarTSV.py skcm.gnab.tmpData1.tsv skcm.gnab.tmpData2.tsv -2 NZC
        ```
        the above command will remove all features that don't have at least 2 mutations.
    4. additional, optional filtering approaches:
          * TODO
          * TODO
    5. adding annotations to feature names:

        ```
$ cd $TCGAFMP_OUTPUTS/<tumor>/gnab/
$ python $TCGAFMP_ROOT_DIR/main/annotateTSV.py <infile> hg19 skcm.gnab.tmpData4b.tsv
        ```
        ***Note***: it is important that the final output of this process be a file in ```$TCGAFMP_OUTPUTS/<tumor>/gnab/ called <tumor>.gnab.tmpData4b.tsv```, as that is where the FMxP will be looking for mutation data.

