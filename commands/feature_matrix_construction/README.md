# TCGA FMx pipeline

This README will lead you through the steps necessary to create a new tumor-specific feature matrix (FMx) 
for your tumor-type of interest.

### MAF processing
If there is a MAF file for your tumor-type, then you should make sure that it has been processed and the binary mutation features are ready to be incorporated into the final FMx.  See the README under ```commands/maf_processing```.

### DNA Methylation processing
The next thing you should know/decide is how you want to process the DNA methylation data.  Two DNA methylation platforms have been used over the course of the TCGA project: the 27k platform and the 450k platform.  For tumor types that contain data from both of these platforms (typically for disjoint sample sets), we typically process these in such a way as to only use the CpG probes that exist on both platforms (with a few extra microRNA specific probes from the 450k platform).  For tumor types that contain data only from the 450k platform, it is probably preferable not to restrict oneself to this limited set of probes.  In order to determine what type of DNA methylation is available for your tumor-type, check to see what types of data archives exist in the local DCC mirror.  (Note that the mere presence of the directories does not necessarily imply that any Level_3 data archives actually exist, so be sure to check for the presence of actual data archives.)

```
	$ cd $TCGAFMP_DCC_REPOSITORIES
	$ cd dcc-mirror/public/tumor/<tumor>/cgcc/jhu-usc.edu/
	$ ls -alt humanmethylation27/methylation/*Level_3*.tar.gz | wc -l
	$ ls -alt humanmethylation450/methylation/*Level_3*.tar.gz | wc -l
```

If you have only 450k data, then you need to pre-process this data prior to building a feature matrix combining all of the other data.  Currently, the tumor types that have only 450k data are: ACC, BLCA, CESC, ESCA, HNSC, LGG, LIHC, MESO, PCPG, PRAD, SARC, SKCM, and THCA.  This pre-processing step is done by the ``` $TCGAFMP_ROOT_DIR/shscript/prep450k.sh ``` script as follows:

```
        ### WARNING !!! do not run this unless you really need to, it takes a LOOOOONG time !!!
	$ $TCGAFMP_ROOT_DIR/shscript/prep450k.sh <tumor> <snpashot-name>
```

This step actually involves looking at the DNA methylation data, the mRNAseq data (specifically IlluminaHiSeq RNAseqV2 data from UNC), and the miRNAseq data (specifically IlluminaHiSeq data from BCGSC) jointly.  (If your mRNAseq or miRNAseq data is not from those centers/platforms and you want to use this pre-processing step, it will need to be modified.)  After combining these three data types, the methylation features are correlated against the proximal expression features and when the absolute value of the correlation coefficient is > 0.30, those features will be kept.  In addition, the top 2% most variable probes (according to interdecile variability) will also be kept.  This pre-processing has not been optimized at all (and probably won't be any time soon since it only needs to be run when new 450k data becomes available for a tumor type of interest), and should be run overnight as it takes ~12h for a typical tumor.

*NOTE:* In order to check whether you *really* need to re-run this ```prep450k.sh``` step, compare the dates for:

```
	$ ls -alt $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/<tumor>/cgcc/jhu-usc.edu/humanmethylation450/methylation/*Level_3*.tar.gz
	$ ls -alt $TCGAFMP_DATA_DIR/<tumor>/meth450k/<tumor>.meth_gexp_mirn.plus.annot.tsv
```

### Heterogeneous FMx construction
Now you are ready to run the high-level script that will produce a FMx.  There are actually two of these, depending again on whether you have only 450k data or you are combining 27k and 450k data.  The usage of the two scripts is very similar:

```
	$ $TCGAFMP_ROOT_DIR/shscript/doAllC_refactor_v2.sh  <curDate>  <snapshotName>  <tumor>  <config>  <public/private>
	$ $TCGAFMP_ROOT_DIR/shscript/doAllC_refactor_450_v2.sh  <curDate>  <snapshotName>  <tumor>  <config>  <public/private>
```

The ```curDate``` parameter does not actually have to be a date and can be any string by which you want to identify this particular run.  The ```snapshotName``` can just be ```dcc-snapshot``` if you want to use the current snapshot, or you can refer to an earlier one explicitly, *eg* ```dcc-snapshot-03mar14```.  The ```config``` file should be either ```parse_tcga.27_450k.config``` or ```parse_tcga.all450k.config``` depending on what type of run you are doing.  This config file can be customized but it is unlikely that you will need to do that.  Finally, if you specify ```public```, then no additional data from the ```aux``` directory will be included into the feature matrix.  This step will take ~5h on a typical tumor (or as little as ~2h for a tumor with relatively few samples and possibly much longer for a tumor with a large number of samples such as BRCA).

The outputs of this process will be a series of files called ```$TCGAFMP_OUTPUTS/<tumor>/<curDate>/<tumor>.{all,seq}.<curDate>.{subsetName}.tsv```.  The ```all``` *vs* ```seq``` indicates whether this FMx contains mRNAseq expression data only (*seq*) or may also include array-based expression data (*all*).  This really only applies to older tumor types such as BRCA, COAD, KIRC, KIRP, LGG, LUAD, LUSC, OV, READ, and UCEC, and for most of those there is now more mRNAseq data available than array data and it may be preferable to limit analysis to the mRNAseq data.  Multiple subsets may have been automatically created and are also indicated within the name of the FMx tsv file.

### Pairwise analysis run
The code for this as well as these instructions should be moved out from this ```feature_matrix_construction``` subdirectory and put into a new ```pairwise_analysis``` subdirectory, but for the moment this is where it resides.

The main driver program for running pairwise analysis on a FMx is ```$TCGAFMP_ROOT_DIR/main/run_pwRK3.py```.  If you invoke it without any command-line arguments, it will give you the following usage information (as well as details on the format of the 12-column output file):

```
bash-3.2$ python $TCGAFMP_ROOT_DIR/main/run_pwRK3.py

 Output of this script is a tab-delimited file with 12 columns, and
 one line for each significant pairwise association:

     # 1  feature A
     # 2  feature B (order is alphabetical, and has no effect on result)
     # 3  Spearman correlation coefficient (range is [-1,+1], or NA
     # 4  number of samples used for pairwise test (non-NA overlap of feature A and feature B)
     # 5  -log10(p-value)  (uncorrected)
     # 6  log10(Bonferroni correction factor)
     # 7  -log10(corrected p-value)   [ col #7 = min ( (col #5 - col #6), 0 ) ]
     # 8  # of non-NA samples in feature A that were not used in pairwise test
     # 9  -log(p-value) that the samples from A that were not used are 'different' from those that were
     #10  (same as col #8 but for feature B)
     #11  (same as col #9 but for feature B)
     #12  genomic distance between features A and B (or 500000000)

usage: run_pwRK3.py [-h] [--min-ct-cell MIN_CT_CELL]
                    [--min-mx-cell MIN_MX_CELL] [--min-samples MIN_SAMPLES]
                    [--pvalue PVALUE] [--adjP] [--all] [--one ONE] [--byType]
                    [--type1 TYPE1] [--type2 TYPE2] [--verbosity VERBOSITY]
                    --tsvFile TSVFILE [--forRE] [--forLisa] [--useBC USEBC]

```

It can be used in various modes:

- ```--all``` : test all possible pairs (all-by-all, *ie* N-choose-2)
- ```--one``` : test one feature against all others (or combine this with ```--byType``` to test one feature against all others of a specific type)
- ```--byType``` : do all-by-all but only within the feature types defined by ```--type1``` and ```--type2``` (for example test all GEXP features against all METH features using ```--type1 GEXP --type2 METH``` or test all GNAB features against all other features using ```--type1 GNAB --type2 ANY```)

All pairwise statistical tests will be compared to the specified ```--pvalue``` threshold and reported only if they are more significant.

The ```--forRE``` option should be specified to produce output that is further filtered and appropriate for loading into Regulome Explorer.  This post-processing step has not been optimized and can be very slow if a loose p-value threshold was specified, resulting in hundreds of millions of significant pairs which now must be sorted and filtered.

### NEW Pairwise helper script
Because different types of features tend to produce p-values with very different orders of magnitude, it has become obvious that it is useful to be able to specify a different p-value threshold for each type of comparison.  In order to facilitate this, the ```$TCGAFMP_ROOT_DIR/shscript/PairProcess-v2.sh``` script has been provided.  It has not been optimized, but it calls the ```run_pwRK3.py``` program described above once for every possible pair of feature types, using the p-value thresholds specified either in ```$TCGAFMP_OUTPUTS/<tumor>/aux/PairProcess_config.csv``` if it is available, or the defaults in ```$TCGAFMP_ROOT_DIR/shscript/PairProcess_config.csv```.  Being able to specify very stringent p-value thresholds for some type-pairs (*eg* GEXP,GEXP) while specifying much looser p-value thresholds for others (*eg* CLIN,CLIN) using this helper script will be significantly faster than simply running ```run_pwRK3.py``` using the ```--all``` option with a single very loose p-value threshold because of the significant time that will be spent in post-processing the outputs.

The usage for this script looks like this:
```
$TCGAFMP_ROOT_DIR/shscript/PairProcess-v2.sh
     Usage   : PairProcess-v2.sh <curDate> <tumorType> <tsvExtension>
     Example : PairProcess-v2.sh  28oct13   brca        TP.tsv
```
where the above example usage would run the PairProcess on the file ```$TCGAFMP_OUTPUTS/brca/28oct13/brca.seq.28oct13.TP.tsv```

If you customize the ```PairProcess_config.csv``` file, it should have 36 lines: there are 8 different feature types (CLIN, CNVR, GEXP, GNAB, METH, MIRN, RPPA, and SAMP), and ```8 multichoose 2``` is equal to ```9 choose 2``` which is 36.  The default file has p-value thresholds ranging from 1.e-02 to 1.e-60.  Depending on the number of samples in your dataset, you may want to adjust these.  After running this script on a feature matrix, you will have 36 seperate output files called ```<FMx-root-name>.<type1>.<type2>.pwpv``` and 36 corresponding filtered files called ```<FMx-root-name>.<type1>.<type2>.pwpv.forRE```.  The filtering that produces the ```forRE``` output files limits each of these to 1-2 million significant pairs.  If the upstream un-filtered file has many more than that because of a relatively loose p-value threshold, the post-processing could be optimized by choosing a more stringent p-value threshold for that specific ```<type1>.<type2>``` comparison.  The typical *worst* offender is the (METH,METH) comparison.  If on the other hand, the individual ```forRE``` output files have fewer significant associations reported than you would like, you may want to consider a looser p-value threshold.  The final combined output file(s) are named ````<FMx-root-name>.pwpv``` and ```<FMx-root-name>.pwpv.forRE``` and it is this latter one that you will want to load into RE.


