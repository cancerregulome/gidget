#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


curDir=`pwd`

cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor

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
	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/public/tumor
    done

## now same for secure side ...
cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/secure/tumor

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
	cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/secure/tumor
    done

echo " "
echo " DONE "
echo " "
date

cd $curDir

