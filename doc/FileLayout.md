# File Layout Dependencies  

This document is for describing the ways in which the gidget code expects or depends on a specific hierarchy of input files to some process. If you introduce a new dependency or find one that is not mentioned, please note it here.

## TCGAFMP_DATA_DIR

The environment variable `$TCGAFMP_DATA_DIR` points to the directory where you want the feature matrix outputs to be added. **TODO:**  This is probably going to change when Max is finished with the top level pipeline. The pipeline uses the following hierarchy:

* `$TCGAFMP_DATA_DIR`
    * _tumor-type directories_ - One directory for each tumor type (e.g. _laml_, _brca_, etc).
        * _"gnab"_ - Contains the outputs and temporary files of the post-maf processing
        * _"scratch"_ 
        * _date directories_ - Referred to as date by the FMx code, but is really just a tag identifying a run of the FMx pipeline. Sepcified by the caller of fmx.sh. There will be one of these folders per run of the fmx code.
            * _fmx output_ - contains feature matrix tsv files and logs
