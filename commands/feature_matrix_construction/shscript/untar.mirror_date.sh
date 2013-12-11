curDir=`pwd`

cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor

## note that the assumption below is that all <name>.tar.gz files un-tar
## to create a directory called <name>, but this is not true for the
## files like clinical_kich.tar.gz ... since these are small files it probably
## doesn't matter that we keep re-un-tar-ing them over and over ...

for arg in `find . -type d`
    do
	## echo " "
	## echo $arg
	cd $arg
	for f in *.tar.gz
	    do
		if [ -f $f ]
		    then
			## echo $f
			g=${f/.tar.gz/}
			if [ -d $g ]
			    then
				## echo " directory exists " $g
				k=1
			    else
				echo " directory does NOT exist " $g
				if [ "$f" == *image* ]
				    then
					echo " NOT un-taring images directory " $f
				    else
					echo " un-TARing " $f
					tar -xzf $f
                                        chmod g+w *.*
                                        chmod g+w $g/*.*
				    fi
			    fi
		    fi
	    done
	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/public/tumor
    done

## now same for secure side ...
cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/secure/tumor

for arg in `find . -type d`
    do
	## echo " "
	## echo $arg
	cd $arg
	for f in *.tar.gz
	    do
		if [ -f $f ]
		    then
			## echo $f
			g=${f/.tar.gz/}
			if [ -d $g ]
			    then
				## echo " directory exists " $g
				k=1
			    else
				echo " directory does NOT exist " $g
				if [ "$f" == *image* ]
				    then
					echo " NOT un-taring images directory " $f
				    else
					echo " un-TARing " $f
					tar -xzf $f
                                        chmod g+w *.*
                                        chmod g+w $g/*.*
				    fi
			    fi
		    fi
	    done
	cd /titan/cancerregulome11/TCGA/repositories/dcc-mirror/secure/tumor
    done

echo " "
echo " removing temporary mimat files ... "
cd /titan/cancerregulome11/TCGA/repositories/dcc-snapshot/public/tumor/
find . -type f -name "*expn_matrix_mimat*" -exec rm -f '{}' \;

echo " "
echo " running snapshot ... "
python2.7 $TCGAFMP_ROOT_DIR/shscript/make-dcc-snapshot.py /titan/cancerregulome11/TCGA/repositories/dcc-mirror /titan/cancerregulome11/TCGA/repositories/dcc-snapshot-`echo "$(date +"%d%b%y")" | tr '[A-Z]' '[a-z]'`

echo " recreating symbolic link ... "
rm /titan/cancerregulome11/TCGA/repositories/dcc-snapshot
ln -s /titan/cancerregulome11/TCGA/repositories/dcc-snapshot-`echo "$(date +"%d%b%y")" | tr '[A-Z]' '[a-z]'` /titan/cancerregulome11/TCGA/repositories/dcc-snapshot

echo " "
echo " DONE "
echo " "
date

cd $curDir

