#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


# =============================================================================

# outer loop is over center
for c in bcgsc.ca broad.mit.edu genome.wustl.edu hgsc.bcm.edu ucsc.edu unc.edu
    do
        echo " "
        echo " "
        date
        echo " ************************************************************** "
        echo " CENTER " $c

        # next loop is over platform / pipeline
        for p in abi illuminaga_dnaseq_cont illuminaga_dnaseq_cont_automated illuminaga_dnaseq_cont_curated \
                 illuminahiseq_dnaseq_cont illuminahiseq_dnaseq_cont_automated illuminahiseq_dnaseq_cont_curated \
                 mixed_dnaseq_cont_curated solid_dnaseq mixed_dnaseq_cont_automated
            do
                echo "     PLATFORM " $p
                
                # and then over tumors ...
                for d in `cat $TCGAFMP_ROOT_DIR/config/tumor_list.txt`
                    do
                        echo "         TUMOR " $d

	                cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/secure/tumor/

                        # check that tumor subdirectory exists ...
                        if [ ! -d "$d" ]; then
                            mkdir $d
                            chmod g+w $d
                        fi
                        cd $d

                        # check that "gsc" subdirectory exists ...
                        if [ ! -d "gsc" ]; then
                            mkdir gsc
                            chmod g+w gsc
                        fi
                        cd gsc

                        # check that center subdirectory exists ...
                        if [ ! -d "$c" ]; then
                            mkdir $c
                            chmod g+w $c
                        fi
                        cd $c

                        # check that platform subdirectory exists ...
                        if [ ! -d "$p" ]; then
                            mkdir $p
                            chmod g+w $p
                        fi
                        cd $p

                        # check that "mutations_protected" subdirectory exists ...
                        if [ ! -d "mutations_protected" ]; then
                            mkdir mutations_protected
                            chmod g+w mutations_protected
                        fi
                        cd mutations_protected

                        echo "             CWD " `pwd`

	                rm -fr index.html
	                wget -e robots=off --wait 1 --debug --no-clobber --continue \
                             --server-response --no-directories \
	                     --accept "*Level_2*.tar.gz" --accept "*mage-tab*.tar.gz" \
                             --accept "*CHANGES*txt"  -R "*images*" \
	                     --verbose --recursive --level=1 \
                             --user=USERNAME_HERE --password=PASSWD_HERE \
	                     https://tcga-data-secure.nci.nih.gov/tcgafiles/tcga4yeo/tumor/$d/gsc/$c/$p/mutations_protected

                    done
            done
    done



