
for d in brca gbm ov
    do
        for f in /titan/cancerregulome14/TCGAfmp_outputs/$d/24may13/$d.seq.24may13.T?.tsv
            do
                echo $d $f
                date
	        python ./run_pwRK2.py --pvalue 2.  --tsvFile $f  --one "N:SAMP:Sustained_Angiogenesis:::::TK" 
	        python ./run_pwRK2.py --pvalue 2.  --tsvFile $f  --one "N:SAMP:Tumor-Promoting_Inflammation:::::TK" 
	        python ./run_pwRK2.py --pvalue 2.  --tsvFile $f  --one "N:SAMP:Genome_Instability:::::TK" 
	        python ./run_pwRK2.py --pvalue 2.  --tsvFile $f  --one "N:SAMP:Sustaining_Proliferative_Signaling:::::TK"  
	        python ./run_pwRK2.py --pvalue 2.  --tsvFile $f  --one "N:SAMP:Evading_Immune_Destruction:::::TK" 
	        python ./run_pwRK2.py --pvalue 2.  --tsvFile $f  --one "N:SAMP:Replicative_immortality:::::TK" 
	        python ./run_pwRK2.py --pvalue 2.  --tsvFile $f  --one "N:SAMP:Resisting_Cell_Death:::::TK"  
	        python ./run_pwRK2.py --pvalue 2.  --tsvFile $f  --one "N:SAMP:Evading_Growth_Suppressors:::::TK" 
	        python ./run_pwRK2.py --pvalue 2.  --tsvFile $f  --one "N:SAMP:Reprogramming_Energy_Metabolism:::::TK" 
	        python ./run_pwRK2.py --pvalue 2.  --tsvFile $f  --one "N:SAMP:Tissue_Invasion_and_Metastasis:::::TK"
            done
    done

