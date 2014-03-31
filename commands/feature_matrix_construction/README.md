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

- If you have only 450k data, then you need to pre-process this data prior to building a feature matrix combining all of the other data.  This is done by the ``` $TCGAFMP_ROOT_DIR/shscript/prep450k.sh ``` script as follows:

```
	$ $TCGAFMP_ROOT_DIR/shscript/prep450k.sh <tumor> <snpashot-name>
```

