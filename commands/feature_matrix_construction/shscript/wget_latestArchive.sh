#!/bin/bash

# every TCGA FMP script should start with these lines:
: ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty; defines the path to the TCGA FMP scripts directory"}
source ${TCGAFMP_ROOT_DIR}/../../gidget/util/env.sh


cd $TCGAFMP_DCC_REPOSITORIES/dcc-mirror/datareports/resources

rm -fr latestarchive
rm -fr latestarchive.public
rm -fr latestarchive.secure
rm -fr a? p? s? a?.* p?.* s?.*

wget http://tcga-data.nci.nih.gov/datareports/resources/latestarchive

wc -l latestarchive

grep "anonymous" latestarchive >& latestarchive.public
grep "tcga4yeo"  latestarchive >& latestarchive.secure

rm -fr t?
rm -fr tumor_archive_counts.Level_?.txt
rm -fr platform_archive_counts.Level_?.txt

cut -f1 latestarchive        | sed -e '1,$s/_/	/' | cut -f2 | sed -e '1,$s/\./	/g' >& a0
cut -f1 latestarchive.public | sed -e '1,$s/_/	/' | cut -f2 | sed -e '1,$s/\./	/g' >& p0
cut -f1 latestarchive.secure | sed -e '1,$s/_/	/' | cut -f2 | sed -e '1,$s/\./	/g' >& s0

grep "Level_1"  a0 >& a1
grep "Level_2"  a0 >& a2
grep "Level_3"  a0 >& a3
grep "Level_"   a0 >& ax
grep "mage-tab" a0 >& am

grep "Level_1"  p0 >& p1
grep "Level_2"  p0 >& p2
grep "Level_3"  p0 >& p3
grep "Level_"   p0 >& px
grep "mage-tab" p0 >& pm

grep "Level_1"  s0 >& s1
grep "Level_2"  s0 >& s2
grep "Level_3"  s0 >& s3
grep "Level_"   s0 >& sx
grep "mage-tab" s0 >& sm

cut -f1,2 ax | sort | uniq | grep -v bio | grep -v images | grep -v pathology  >& ax.su
cut -f1,2 am | sort | uniq >& am.su

cut -f1,2 px | sort | uniq | grep -v bio | grep -v images | grep -v pathology  >& px.su
cut -f1,2 pm | sort | uniq >& pm.su

cut -f1,2 sx | sort | uniq | grep -v bio | grep -v images | grep -v pathology  >& sx.su
cut -f1,2 sm | sort | uniq >& sm.su

cut -f1 p1 | sort | uniq -c >& tumor_archive_counts.Level_1.txt
cut -f1 p2 | sort | uniq -c >& tumor_archive_counts.Level_2.txt
cut -f1 p3 | sort | uniq -c >& tumor_archive_counts.Level_3.txt

cut -f2 p1 | sort | uniq -c >& platform_archive_counts.Level_1.txt
cut -f2 p2 | sort | uniq -c >& platform_archive_counts.Level_2.txt
cut -f2 p3 | sort | uniq -c >& platform_archive_counts.Level_3.txt

