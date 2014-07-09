# gidget changelog

## 0.4.0

### required envionmental variables
* The commandline tools should give errors and documentation on unset variables.  Currently all required variables should be set to use any of the scripts.  Also see ```gidget/config/required_env_vars```.  See the author for her own sample config file.

### gidget/commands/feature_matrix_construction
#### major updates
* new pairwise version 2 code is now tested and fully incorporated -- handling of categorical features is slightly different (better) than the previous version, so you may see some changes in the results
* "v2" versions of top-level scripts should now be used: ```doAllC_refactor_v2.sh```, ```doAllC_refactor_450_v2.sh```, and ```PairProcess-v2.sh```
* ```doAllC_refactor_*v2.sh``` scripts allow the specification of a non-standard "aux" directory -- for example if you want to be able to build different feature matrices for STAD using different "aux" information, then you can have multiple directories, eg ```stad/aux_new/``` ,  ```stad/aux_draft/```,  ```stad/aux_publication/``` and build feature matrices using them by specifing ```aux_new``` or ```aux_draft```, etc on the command-line when running either of these new ```doAllC*``` scripts
* ```PairProcess-v2.sh``` is the new pairwise helper script and will also create a template META file for loading the feature matrix and pairwise results into RE (this template file still needs to be edited by hand before the actual loading, but hopefully this will be helpful)
* ```run-pairwise-v2.py``` is the new lower level script for running pairwise (supersedes the previous ```run_pwRK3.py```)
* "loose" black-listing of features during the FMx construction process has been modified to allow for partial substring matching rather than prefix-only matching

#### MINOR UPDATES:
* RPPA features are now generated for each gene symbol if an antibody is non-specific (eg features for AKT1, AKT2, and AKT3 for antibody Akt_pS473-R-V (note that these features will be otherwise identical to each other and will correlate perfectly with one another)
* Spearman correlation coefficient is now written out to two decimal places rather than 3
* compare2TSVs script now only compares the "important" parts of feature names
* CNVR features are now never annotated with a gene symbol, always with the locus (in the past, if the segment overlapped only one gene it was annotated with that gene symbol, but in order to have a more uniform approach they are now annotated only with a locus -- obtaining the mapping from segment to gene symbol(s) must be done using a secondary look-up table)

### gidget/commands/binarization
*  Mutation summary generation: Updated to parse MAF protein change codes for in-frame deletions.  'AA pos' output column takes the first position mentioned in the deletion; "to aa" and "from aa" are left blank in this case.

### gidget/commands/maf_processing
* additional user documentation for manually running the pipeline

