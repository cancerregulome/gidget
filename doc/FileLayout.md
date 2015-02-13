# File Layout Dependencies  

This document is for describing the ways in which the gidget code expects or depends on a specific hierarchy of input files to some process. If you introduce a new dependency or find one that is not mentioned, please note it here.

## $TCGABINARIZATION_DATABASE_DIR

* `$TCGABINARIZATION_DATABASE_DIR`
    * _interpro/_
        * _data/_
            * _\<uniprot ID\>.txt_ - Is this actually needed?
    * _TRANSFAC_2010.1/_
        * _interpro_domains_vaquerizas_nature_2009.txt_ - Is this actually needed?
    

## $TCGAFMP_BIOINFORMATICS_REFERENCES

* `$TCGAFMP_BIOINFORMATICS_REFERENCES`
    * _ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info/_
    * _GAF/_
        * _Feb2011/GAF.hg18.Feb2011/GAF_bundle/outputs/TCGA.hg18.Feb2011.gaf_
        * _GAF3.0/all.gaf_
    * _gencode/_
        * _gencode.v19.gene.gtf_
    * _hg18/_
        * _cytoBand.hg18.txt_
    * _hg19/_
        * _cytoBand.hg19.txt_
        * _refGene.txt_
    * _nci_pid/_ 
        * _only_NCI_Nature_ver4.tab_
        * _only_NCI_Nature_ver5.tab_
    * _sig_genes.2k.26feb13.txt_
    * _tcga_platform_genelists/_
        * _featNames.09jul12.hg19.txt_
        * _featNames.15oct13.hg19.txt_
        * _featNames.16oct13.hg19.txt_
        * _MDA_antibody_annotation_2014_03_04.txt_
    

## $TCGAFMP_CLUSTER_HOME

* `$TCGAFMP_CLUSTER_HOME`
    * _GOLEMPW/_

## $TCGAFMP_DATA_DIR

The environment variable `$TCGAFMP_DATA_DIR` points to the directory where you want the feature matrix outputs to be added. **TODO:**  This is probably going to change when Max is finished with the top level pipeline. The pipeline uses the following hierarchy:

* `$TCGAFMP_DATA_DIR`
    * _\<tumor-type directories\>_ - One directory for each tumor type (e.g. _laml_, _brca_, etc).
        * _gnab/_ - Contains the outputs and temporary files of the post-maf processing
        * _scratch/_ 
        * _\<date directories\>_ - Referred to as date by the FMx code, but is really just a tag identifying a run of the FMx pipeline. Sepcified by the caller of fmx.sh. There will be one of these folders per run of the fmx code.
            * _\<fmx output\>_ - contains feature matrix tsv files and logs

## $TCGAFMP_DCC_REPOSITORIES

* `$TCGAFMP_DCC_REPOSITORIES`
    * _bio_clin/_
        * _featNames.tsv_
    * _mirna_bcgsc/_
        * _mature.fa.flat.human.mirbase_v19.txt_
        * _tcga_mirna_bcgsc_hg19.adf_
    * _rppa/_
        * _MDA_antibody_annotation.txt_
    * _uuids/_
        * _get_metadata.sh_
        * _metadata.current.txt_
    * _\<Snapshot name\>_
        * _metadata.current.txt_
        * _public/_ AND _secure/_
            * _tumor/_
                * _\<tumor type\>/_
                    * ... **TODO** This file hierarchy is very deep. Do we need to document this? 

## $TCGAFMP_FIREHOSE_MIRROR

* `$TCGAFMP_FIREHOSE_MIRROR`
    * _metadata/_
        * _meth.probes.15oct13.txt_
        * _name_map.tsv_
    * _\< **TODO** other stuff \>_
        * ...

## $TCGAFMP_PAIRWISE_ROOT
    
* `$TCGAFMP_PAIRWISE_ROOT`
    * _pairwise-1.1.2_ - executable
    * _pairwise-2.0.0-current_ - executable
    * _prep4pairwise.py_
                        

## $TCGAMAF_REFERENCES_DIR

* `$TCGAMAF_REFERENCES_DIR`
    * _gene2uniprot.sprot_
    * _gene2uniprot.trembl_
    * _gene_refseq_uniprotkb_collab/_
    * _HumanDB/_
    * _isoform1.sprot_
    * _isoform1.trembl_
    * _knowgene_to_protein/_
    * _uniprot_sec_ac.txt_
    * _uniprot_sprot_human.dat_
    * _uniprot_trembl_human.dat_
    
## $TCGAMAF_TOOLS_DIR

* `$TCGAMAF_TOOLS_DIR`
    * _anotate_variation.pl_
