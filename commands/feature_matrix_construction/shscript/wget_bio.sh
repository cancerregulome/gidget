cd ~/scratch/

for d in acc blca brca cesc cntl coad dlbc esca gbm hnsc kich kirc kirp laml lgg lihc luad lusc meso ov paad pcpg prad read sarc skcm stad tgct thca ucs ucec
    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d
	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$d/
        mkdir bcr
        chmod g+w bcr
        cd bcr
        mkdir nationwidechildrens.org
        chmod g+w nationwidechildrens.org
        cd nationwidechildrens.org
        mkdir bio
        chmod g+w bio
        cd bio
        mkdir clin
        chmod g+w clin
        cd clin

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*bio.Level_1*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/bcr/nationwidechildrens.org/bio/clin

    done

for d in laml luad
    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d
	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$d/bcr/genome.wustl.edu/bio/clin

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*bio.Level_1*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/bcr/genome.wustl.edu/bio/clin

    done


