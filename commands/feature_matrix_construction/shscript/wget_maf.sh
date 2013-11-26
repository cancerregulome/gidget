
for d in `cat $TCGAFMP_ROOT_DIR/shscript/tumor_list.txt`

    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$d/
        mkdir gsc
        chmod g+w gsc
        cd gsc
	mkdir broad.mit.edu
        chmod g+w broad.mit.edu
	cd broad.mit.edu
	mkdir illuminaga_dnaseq
        chmod g+w illuminaga_dnaseq
	cd illuminaga_dnaseq
	mkdir mutations
        chmod g+w mutations
	cd mutations

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_2*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/gsc/broad.mit.edu/illuminaga_dnaseq/mutations

    done

for d in `cat $TCGAFMP_ROOT_DIR/shscript/tumor_list.txt`

    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$d/gsc/
	mkdir genome.wustl.edu
        chmod g+w genome.wustl.edu
	cd genome.wustl.edu
	mkdir illuminaga_dnaseq
        chmod g+w illuminaga_dnaseq
	cd illuminaga_dnaseq
	mkdir mutations
        chmod g+w mutations
	cd mutations

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_2*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/gsc/genome.wustl.edu/illuminaga_dnaseq/mutations

    done

for d in `cat $TCGAFMP_ROOT_DIR/shscript/tumor_list.txt`

    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$d/gsc/
	mkdir hgsc.bcm.edu
        chmod g+w hgsc.bcm.edu
	cd hgsc.bcm.edu
	mkdir illuminaga_dnaseq
        chmod g+w illuminaga_dnaseq
	cd illuminaga_dnaseq
	mkdir mutations
        chmod g+w mutations
	cd mutations

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_2*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/gsc/hgsc.bcm.edu/illuminaga_dnaseq/mutations

    done

