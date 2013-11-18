cd ~/scratch/

for d in acc blca brca cesc cntl coad dlbc esca gbm hnsc kich kirc kirp laml lgg lihc luad lusc meso ov paad pcpg prad read sarc skcm stad tgct thca ucs ucec

    do

	echo " "
	echo " "
	echo " ******************************************************************** "
	echo $d
	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor/$d/cgcc
        mkdir broad.mit.edu
        chmod g+w broad.mit.edu
        cd broad.mit.edu
        mkdir genome_wide_snp_6
        chmod g+w genome_wide_snp_6
        cd genome_wide_snp_6
        mkdir snp
        chmod g+w snp
        cd snp

	rm -fr index.html
	wget -e robots=off --wait 1 --debug --no-clobber --continue --server-response --no-directories \
	     --accept "*Level_3*.tar.gz" --accept "*mage-tab*.tar.gz" --accept "*CHANGES*txt" \
             -R "*images*" \
	     --verbose \
	     --recursive --level=1 \
	     https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/$d/cgcc/broad.mit.edu/genome_wide_snp_6/snp

    done

