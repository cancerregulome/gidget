
for d in `cat $TCGAFMP_ROOT_DIR/shscript/tumor_list.txt`
    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d
	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$d/bcr/
	mkdir biotab
        chmod g+w biotab
	cd biotab
	mkdir clin
        chmod g+w clin
	cd clin

	rm -fr index.html
	rm -fr *.tar.gz
	rm -fr *.txt

	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*.txt" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/bcr/biotab/clin

        chmod g+w *.*

    done

