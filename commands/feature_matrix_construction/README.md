#TCGA FMx pipeline

### How to create a new tumor-specific feature matrix (FMx) for your tumor-type of interest.

- If there is a MAF file for your tumor-type, then you should make sure that it has been processed and the binary mutation features are ready to be incorporated into the final FMx.  See the README under commands/maf_processing.

- The next thing you should know/decide is how you want to process the DNA methylation data.  Two DNA methylation platforms have been used over the course of the TCGA project: the 27k platform and the 450k platform.  For tumor types that contain data from both of these platforms (typically for disjoint sample sets), we typically process these in such a way as to only use the CpG probes that exist on both platforms (with a few extra microRNA specific probes from the 450k platform).  For tumor types that contain data only from the 450k platform, it is probably preferable not to restrict onesself to this limited set of probes.
