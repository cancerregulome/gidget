#TCGA FMx pipeline

### How to create a new tumor-specific feature matrix (FMx) for your tumor-type of interest.

- If there is a MAF file for your tumor-type, then you should make sure that it has been processed and the binary mutation features are ready to be incorporated into the final FMx.  See the README under commands/maf_processing.

- The next thing you should know/decide is how you want to process the DNA methylation data.  Two DNA methylation platforms have been used over the course of the TCGA project: the 27k platform and the 450k platform.  For tumor types that contain data from both of these platforms (typically for disjoint sample sets), we typically process these in such a way as to only use the CpG probes that exist on both platforms (with a few extra microRNA specific probes from the 450k platform).  For tumor types that contain data only from the 450k platform, it is probably preferable not to restrict oneself to this limited set of probes.  In order to determine what type of DNA methylation is available for your tumor-type, check to see what types of data archives exist in the local DCC mirror.  (Note that the mere presence of the directories does not necessarily imply that any Level_3 data archives actually exist, so be sure to check for the presence of actual data archives.)

```
	$ cd $TCGAFMP_DCC_REPOSITORIES
	$ cd dcc-mirror/public/tumor/<tumor>/cgcc/jhu-usc.edu/
	$ ls -alt humanmethylation27/methylation/*Level_3*.tar.gz | wc -l
	$ ls -alt humanmethylation450/methylation/*Level_3*.tar.gz | wc -l
```

- If you have only 450k data, then you need to pre-process this data prior to building a feature matrix combining all of the other data.  Currently, the tumor types that have only 450k data are: ACC, BLCA, CESC, ESCA, HNSC, LGG, LIHC, MESO, PCPG, PRAD, SARC, SKCM, and THCA.  This pre-processing step is done by the ``` $TCGAFMP_ROOT_DIR/shscript/prep450k.sh ``` script as follows:

```
	$ $TCGAFMP_ROOT_DIR/shscript/prep450k.sh <tumor> <snpashot-name>
```

This step actually involves looking at the DNA methylation data, the mRNAseq data (specifically IlluminaHiSeq RNAseqV2 data from UNC), and the miRNAseq data (specifically IlluminaHiSeq data from BCGSC) jointly.  (If your mRNAseq or miRNAseq data is not from those centers/platforms and you want to use this pre-processing step, it will need to be modified.)  After combining these three data types, the methylation features are correlated against the proximal expression features and when the absolute value of the correlation coefficient is > 0.30, those features will be kept.  In addition, the top 2% most variable probes (according to interdecile variability) will also be kept.  This pre-processing has not been optimized at all (and probably won't be any time soon since it only needs to be run when new 450k data becomes available for a tumor type of interest), and should be run overnight as it takes ~10h.

- Now you are ready to run a the high-level script that will produce a FMx.  There are actually two of these, depending again on whether you have only 450k data or you are combining 27k and 450k data.  The usage of the two scripts is very similar:

```
	$ $TCGAFMP_ROOT_DIR/shscript/doAllC_refactor.sh  <curDate>  <snapshotName>  <tumor>  <config>  <public/private>
	$ $TCGAFMP_ROOT_DIR/shscript/doAllC_refactor_450.sh  <curDate>  <snapshotName>  <tumor>  <config>  <public/private>
```

The ```curDate``` parameter does not actually have to be a date and can be any string by which you want to identify this particular run.  The ```snapshotName``` can just be ```dcc-snapshot``` if you want to use the current snapshot, or you can refer to an earlier one explicitly, eg ```dcc-snapshot-03mar14```.  The ```config``` file should be either ```parse_tcga.27_450k.config``` or ```parse_tcga.all450k.config``` depending on what type of run you are doing.  This config file can be customized but it is unlikely that you will need to do that.  Finally, if you specify ```public```, then no additional data from the ```aux``` directory will be included into the feature matrix.  This step will take ~5h on a typical tumor (or as little as ~2h for a tumor with relatively few samples and possibly much longer for a tumor with a large number of samples such as BRCA).

