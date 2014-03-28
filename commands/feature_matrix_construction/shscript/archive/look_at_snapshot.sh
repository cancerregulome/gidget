
d1='22sep13'
d2='08aug13'

rm -fr ~/scratch/ls.lR.$d1.?
rm -fr ~/scratch/ls.lR.$d2.?

cd ${TCGAFMP_DCC_REPOSITORIES}/dcc-snapshot-$d1
ls -lR | grep "^lrwxrwxrwx" | grep "Level_" | grep -v "README" | grep -v "MANIFEST" | grep -v "CHANGES" | grep -v "DCC_ALTERED" | grep -v "ADDITIONS" | grep -v "REMOVED" | grep -v "DESCRIPTION" | grep -v ";O=" >& ~/scratch/ls.lR.$d1.a

cd ${TCGAFMP_DCC_REPOSITORIES}/dcc-snapshot-$d2
ls -lR | grep "^lrwxrwxrwx" | grep "Level_" | grep -v "README" | grep -v "MANIFEST" | grep -v "CHANGES" | grep -v "DCC_ALTERED" | grep -v "ADDITIONS" | grep -v "REMOVED" | grep -v "DESCRIPTION" | grep -v ";O=" >& ~/scratch/ls.lR.$d2.a

cd ~/scratch/
sed -e '1,$s/ -> /	/g' ls.lR.$d1.a | cut -f2 | sort >& ls.lR.$d1.b
sed -e '1,$s/ -> /	/g' ls.lR.$d2.a | cut -f2 | sort >& ls.lR.$d2.b

sed -e '1,$s/\//	/g' ls.lR.$d1.b >& ls.lR.$d1.c
sed -e '1,$s/\//	/g' ls.lR.$d2.b >& ls.lR.$d2.c

cut -f14 ls.lR.$d1.c >& ls.lR.$d1.d
cut -f14 ls.lR.$d2.c >& ls.lR.$d2.d

diff ls.lR.$d1.d ls.lR.$d2.d | grep "^>" | sort | uniq >& diff.a
diff ls.lR.$d1.d ls.lR.$d2.d | grep "^<" | sort | uniq >& diff.b

echo " "
echo " "
echo $d1 " vs " $d2

echo " "
echo " "
wc -l diff.a
echo " old (obsolete) archives: "
cat diff.a

echo " "
echo " "
wc -l diff.b
echo " new archives: "
cat diff.b

echo " "
echo " "


