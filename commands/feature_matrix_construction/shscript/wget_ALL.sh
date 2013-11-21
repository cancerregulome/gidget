curDir=`pwd`

cd /users/sreynold/to_be_checked_in/TCGAfmp/shscript
date
echo " wget_bio "
./wget_bio.sh

cd /users/sreynold/to_be_checked_in/TCGAfmp/shscript
date
echo " wget_biotab "
./wget_biotab.sh

cd /users/sreynold/to_be_checked_in/TCGAfmp/shscript
date
echo " wget_maf "
./wget_maf.sh

cd /users/sreynold/to_be_checked_in/TCGAfmp/shscript
date
echo " wget_maf_prot "
./wget_maf_prot.sh

cd /users/sreynold/to_be_checked_in/TCGAfmp/shscript
date
echo " wget_msat_prot "
./wget_msat_prot.sh

cd /users/sreynold/to_be_checked_in/TCGAfmp/shscript
date
echo " wget_meth "
./wget_meth.sh

cd /users/sreynold/to_be_checked_in/TCGAfmp/shscript
date
echo " wget_mirn "
./wget_mirn.sh

cd /users/sreynold/to_be_checked_in/TCGAfmp/shscript
date
echo " wget_rnaseq "
./wget_rnaseq.sh

cd /users/sreynold/to_be_checked_in/TCGAfmp/shscript
date
echo " wget_rppa "
./wget_rppa.sh

cd /users/sreynold/to_be_checked_in/TCGAfmp/shscript
date
echo " wget_snp "
./wget_snp.sh

echo " DONE !!! "
date

cd $curDir

