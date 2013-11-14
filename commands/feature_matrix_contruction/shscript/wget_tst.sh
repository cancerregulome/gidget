cd ~/scratch/

for d in skcm
    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d

	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/secure/tumor/$d
        mkdir gsc
        chmod g+w gsc
        cd gsc
	mkdir broad.mit.edu
        chmod g+w broad.mit.edu
	cd broad.mit.edu
	mkdir illuminaga_dnaseq_cont
        chmod g+w illuminaga_dnaseq_cont
	cd illuminaga_dnaseq_cont
	mkdir mutations_protected
        chmod g+w mutations_protected
	cd mutations_protected

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_2*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     --user=ShmulevI --password=C@ncerReg22 \
	     https://tcga-data-secure.nci.nih.gov/tcgafiles/tcga4yeo/tumor/$d/gsc/broad.mit.edu/illuminaga_dnaseq_cont/mutations_protected

    done

