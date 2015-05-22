available gidget pipeline commands
==================================

# update MAF pipeline's bioinformatics references
_This is an administration function and should NOT be run by most users_

commandline usage:
```
gidget run update-maf-pipeline-bioinformatics-references
```

# MAF annotation pipline
This pipeline takes an unannotated MAF (from AWGs or other sources) and annotates the file with additional information

commandline usage:
```
gidget run maf-annotation-pipeline
```

# binarization pipline
This pipeline takes an _annotated MAF_ (for ex, produced from the MAF annotation pipeline)

commandline usage:
```
gidget run binarization-pipeline
```


# "post-binarization processing in prep for feature matrix construction" pipeline
This pipeline takes output from the binarization pipeline.

*Fitering and other cleaning take place here.*

commandline usage:
```
gidget run prepare-binarized-maf-for-fmx-construction
```


# feature matrix (FMX) construction and merge pipeline
This pipeline takes ouput from the "post-binarization processing in prep for feature matrix construction" pipeline, and creates a feature matrix, merges in other data types (for ex, methylation from the DCC), and produces the final FMX tsv files.

commandline usage:
```
gidget run fmx-construction
```

# upload completed feature matrix (FMX) to Regulome Explorer (RE)
_This is currently an administration function and should NOT be run by most users_

commandline usage:
```
gidget run upload-fmx-to-regulome-explorer
```
