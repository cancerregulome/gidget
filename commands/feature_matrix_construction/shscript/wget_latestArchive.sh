#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/datareports/resources

rm -fr latestarchive
wget http://tcga-data.nci.nih.gov/datareports/resources/latestarchive

wc -l latestarchive

rm -fr t?
rm -fr tumor_archive_counts.Level_?.txt
rm -fr platform_archive_counts.Level_?.txt

cut -f1 latestarchive | sed -e '1,$s/_/	/' | cut -f2 | sed -e '1,$s/\./	/g' >& t0


grep "Level_1" t0 >& t1
grep "Level_2" t0 >& t2
grep "Level_3" t0 >& t3
grep "mage-tab" t0 >& tm

cut -f1 t1 | sort | uniq -c >& tumor_archive_counts.Level_1.txt
cut -f1 t2 | sort | uniq -c >& tumor_archive_counts.Level_2.txt
cut -f1 t3 | sort | uniq -c >& tumor_archive_counts.Level_3.txt

cut -f2 t1 | sort | uniq -c >& platform_archive_counts.Level_1.txt
cut -f2 t2 | sort | uniq -c >& platform_archive_counts.Level_2.txt
cut -f2 t3 | sort | uniq -c >& platform_archive_counts.Level_3.txt

rm -fr t?
