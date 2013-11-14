
cd /users/sreynold/to_be_checked_in/TCGAfmp/shscript

echo " "
date
## in first test on Fri Jul 12, this took ~1h
echo " calling wget_bio.sh "
./wget_bio.sh
echo " "
date
## and this took ~10min (before I added the parse script)
echo " calling wget_biotab.sh "
./wget_biotab.sh
./parse_biospecimen_biotab_files.sh
echo " "
date
## and this took ~20min
echo " calling untar.mirror.sh "
./untar.mirror.sh

nohup ./doAllC.sh 16jul13 dcc-snapshot brca &
sleep 4400

nohup ./doAllC.sh 16jul13 dcc-snapshot kirc &
sleep 2400

nohup ./doAllC.sh 16jul13 dcc-snapshot thca &
sleep 2300

nohup ./doAllC.sh 16jul13 dcc-snapshot luad &
sleep 2200

nohup ./doAllC.sh 16jul13 dcc-snapshot lusc &
sleep 1800

nohup ./doAllC.sh 16jul13 dcc-snapshot hnsc &
sleep 1500

nohup ./doAllC.sh 16jul13 dcc-snapshot skcm &
sleep 1200

nohup ./doAllC.sh 16jul13 dcc-snapshot ov &
sleep 1200

nohup ./doAllC.sh 16jul13 dcc-snapshot lgg &
sleep 1000

nohup ./doAllC.sh 16jul13 dcc-snapshot prad &
sleep 1000

nohup ./doAllC.sh 16jul13 dcc-snapshot gbm &
sleep 700

nohup ./doAllC.sh 16jul13 dcc-snapshot blca &
sleep 700

nohup ./doAllC.sh 16jul13 dcc-snapshot laml &
sleep 700

nohup ./doAllC.sh 16jul13 dcc-snapshot kirp &
sleep 600


echo " "
echo " "
echo " weekendRun is DONE !!! "
date
echo " "
echo " "


