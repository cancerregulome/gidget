#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


# =============================================================================

# outer loop is over center
for c in bcgsc.ca broad.mit.edu genome.wustl.edu hgsc.bcm.edu ucsc.edu
    do
        echo " "
        echo " "
        date
        echo " ************************************************************** "
        echo " CENTER " $c

        # next loop is over platform / pipeline
        for p in abi illuminaga_dnaseq illuminaga_dnaseq_automated illuminaga_dnaseq_curated \
                 illuminahiseq_dnaseq illuminahiseq_dnaseq_automated illuminahiseq_dnaseq_curated \
                 mixed_dnaseq_curated solid_dnaseq
            do
                echo "     PLATFORM " $p
                
                # and then over tumors ...
                for d in `cat $TCGAFMP_ROOT_DIR/config/tumor_list.txt`
                    do
                        echo "         TUMOR " $d

	                cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor/

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

                        # check that "mutations" subdirectory exists ...
                        if [ ! -d "mutations" ]; then
                            mkdir mutations
                            chmod g+w mutations
                        fi
                        cd mutations

                        echo "             CWD " `pwd`

	                rm -fr index.html
	                wget -e robots=off --wait 1 --debug --no-clobber --continue \
                             --server-response --no-directories \
	                     --accept "*Level_2*.tar.gz" --accept "*mage-tab*.tar.gz" \
                             --accept "*CHANGES*txt"  -R "*images*" \
	                     --verbose --recursive --level=1 \
	                     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/gsc/$c/$p/mutations

                    done
            done
    done



