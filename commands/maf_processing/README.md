#TCGA MAF pipeline

### What to do when you get a new MAF file ...

*But wait!* you might ask, *how do I know if I have a new MAF file?*

- If you are getting the MAF file from the DCC, then you can check like this:

    ```
$ cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/<tumor>/gsc/
$ ls -alt */*dna*/*/*/*.maf
    ```
and you can check the time stamp of the first MAF file listed -- usually you want to use the most recent one available, but sometimes an older one might have been "curated" or might be from a preferred sequencing center.
Generally, the most recent and/or largest MAF file is the one that is most likely to be of interest.

- On the other hand, you might have obtained a MAF file from a different
source.

We will use this SKCM MAF file as an example:
```
$TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/skcm/gsc/broad.mit.edu/illuminaga_dnaseq/mutations/broad.mit.edu_SKCM.IlluminaGA_DNASeq.Level_2.1.5.0/skcm_clean_pairs.aggregated.capture.tcga.uuid.somatic.maf
```

If you want to see some basic information about  this MAF such as the number of samples, the most frequently mutated genes, etc, there is a simple script called ```$TCGAFMP_ROOT_DIR/shscript/qMaf.sh``` that you can use.  On this particular MAF file, it will report, for example, that the most frequently mutated genes (and the counts) are:

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

1. run MAF annotation scripts, the manual way.  For kicks, let's assume you're doing the processing in a separate directory.
	* Link in your original (downloaded) MAF:
	* ```ln -s <original MAF> .```
	* create a little file to describe which file will be processed:
	* ```touch maf_file_list```
	* ```echo <original MAF filename> > maf_file_list```
	* set required environmental variables.  Currently, these are set as bash shell variables.  You can ask the project author for her working file. For example, call the file ```set_gidget_env_vars.sh```.  Copy and edit this as appropriate.  Note, there may be currently-used variables for development.  Then source the file (NOT execute):
	* ```source set_gidget_env_vars.sh```
	* update your current data directory:
	* ```export TCGAMAF_DATA_DIR=`pwd -P````
	* run the annotation:
	* ```${GIDGET_SOURCE_ROOT}/commands/maf_processing/bash/updateMAF.sh```
	* if success, the main output file is (the annotated MAF): ```<maf filename>.ncm.with_uniprot```
	* run some addition file reporting:
	* ```${GIDGET_SOURCE_ROOT}/commands/maf_processing/bash/final_maf_diagnostics.sh <maf filename>.ncm.with_uniprot```




2. run the binarization scripts.  Again, let's assume you're doing the processing in a separate directory.
	* * Link in your annotated MAF:
	* ```ln -s <annotated MAF, the ncm.with_uniprot file> .```
	* bring in the scripts: doing it this way helps with some relative path issues (TBD)
	* ```ln -s ${GIDGET_SOURCE_ROOT}/commands/binarization/genes_and_mutations_annovar.pl```
	* ```ln -s ${GIDGET_SOURCE_ROOT}/commands/binarization/mutation_binarization_annovar.pl```
	* run the mutation summary:
	* ```./genes_and_mutations_annovar.pl <TUMOR SHORT CODE, for ex ‘STAD’> <maf filename>.ncm.with_uniprot > mutation_summary_dd_.mm.yyyy.txt```
	* The major output from the binarization step is a very large tsv file containing binarized information about all mutated genes for all tumor samples referenced in the MAF file.  This step can take quite a while:
	* ```./mutation_binarization_annovar.pl <maf filename>.ncm.with_uniprot > mut_bin_mm.dd.yyyy.txt```

3. post-processing; NOTE: perhaps open a fresh terminal, or at least be aware that you've set a bunch of gidget environmental variables and review them:
    1. copy the output of step #2 (```mut_bin_mm.dd.yyyy.txt```, not the "transpose" file) to ```$TCGAFMP_OUTPUTS/<tumor>/gnab/latest.gnab.txt```
    2. first post-processing step (all this currently does is some minor clean-up and/or re-formatting):

        ```
$ cd $TCGAFMP_ROOT_DIR/shscript
$ ./fmp03B_gnab_part.sh <tumor>
        ```
    3. next, features with very few 1's should be filtered out, for example:

        ```
$ cd $TCGAFMP_OUTPUTS/<tumor>/gnab/
$ python $TCGAFMP_ROOT_DIR/main/highVarTSV.py skcm.gnab.tmpData1.tsv skcm.gnab.tmpData2.tsv -2 NZC
        ```
        the above command will remove all features that don't have at least 2 mutations.  If you know that your tumor-type has a very high mutation rate, you might want to set this value higher (but be sure to keep the negative sign in front -- ```highVarTSV.py``` has several different options/modes and this particular use case is indicated by a negative value).
    4. additional, optional filtering approaches:
          * filtering out identical features: Often, two features for the same gene will actually be identical.  If, for example, all of the mutations in a particular gene are all nonsilent, then the "y_n" feature and the "nonsilent" feature will be identical.  Identical features can be removed using ```$TCGAFMP_ROOT_DIR/main/filterIdentFeat2.py```
          * keep only a certain class of muations:  Another approach that is sometimes used is to keep only a certain class of mutations for all genes, eg those with "code_potential" in the feature name.  This can easily be done simply by editing the TSV file using ```grep``` etc, just make sure that you keep the header line with the sample identifiers as part of the final file.
          * keep features only for specified genes:  Another approache is to keep only those features that pertain to a specified list of genes.  This can be done using ```$TCGAFMP_ROOT_DIR/main/filterByGeneList.py```.
    5. adding annotations to feature names:

        ```
$ cd $TCGAFMP_OUTPUTS/<tumor>/gnab/
$ python $TCGAFMP_ROOT_DIR/main/annotateTSV.py <infile> hg19 skcm.gnab.filter.annot.tsv
        ```
        
***Note***: it is important that the final output of this process be a file in the directory ```$TCGAFMP_OUTPUTS/<tumor>/gnab/```, in a file called ```<tumor>.gnab.filter.annot.tsv```, as that is where the FMxP will be looking for mutation data.

