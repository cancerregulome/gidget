#!/usr/bin/perl

# version 6.1

$maf_file = $ARGV[0] || die "usage: $0 MAF_FILE\n";

@elements = split ('\.', $maf_file);
$tumor_type = $elements[0];

&read_tcga_mutation_data;

####################################################################################################
sub read_tcga_mutation_data
{
	%uniprot_annotation = ();
	%mutations = ();
	%themut = ();
	%tumor_ids = ();
	%nonsilent = ();
	%missense = ();
	%mnf = ();
	%mni = ();
	%code_potential = ();
	%annotation_seen = ();
	open (MAF, "< $maf_file") || die "cannot read maf file: $!\n";
	while ($line = <MAF>)
	{
		unless (($line =~ /^\#version/) || ($line =~ /^\Hugo_Symbol/))
		{
			#P51816		AFF2:uc004fcp.1:exon3:c.T305G:p.V102G,
			#TCGA-AG-A032-01A-01W-A00E-09
			if (($line =~ /^(\S*?)\t(\S*?)\t\S*?\t\S*?\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t\S*?\t\S*?\t(\S*?)\t(\S*?)\t.+\t(\S{6})\S*?\t\S*?\t.+?:p\.(\w+\d+\S+?),.*\t/) && ($line !~ /NO UNIPROT MATCH/) && ($line !~ /NO ISOFORM MATCH/) && ($line !~ /NO UNIPROT ID/))
			{
				($hugo_symbol, $entrez_gene_id, $chromo, $start_position, $end_position, $strand, $variant_classification, $variant_type, $reference_allele, $tumor_seq_allele1, $tumor_seq_allele2, $tumor_sample_barcode, $matched_norm_sample_barcode, $uniprot, $mutation) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15);
				
				if ($tumor_sample_barcode ne $matched_norm_sample_barcode)
				{
					if ($tumor_sample_barcode =~ /^(\w+?)\-(\w{2})\-(\w{4})\-/)
					{
						#looks good, do nothing
					}
					elsif ($tumor_sample_barcode =~ /^(\w+?\-\w+?)\-(\w{2})\-(\w{4})\-/)
					{
						#barcode has been modified
						$tumor_sample_barcode = "TCGA-" . $2 . "-" . $3 . "-";
					}
					
					$tumor_sample_barcode = $1 || die "die: could not truncate tumor sample barcode" if ($tumor_sample_barcode =~ /^(\S+?\-\S+?\-\S+?)\-/);
					
					$annotation_seen{$hugo_symbol}{$tumor_sample_barcode}{$start_position} = 1;
					
					if ($uniprot =~ /^http/)
					{
						if ($line =~ /^.+\t(\S{6})\S*?\t.+?:p\.(\w+\d+\S+?),.*\t/)
						{
							($uniprot, $mutation) = ($1, $2);
						}
					}
					
					#print "$uniprot\t$line\n";
					
					($one, $two, $three) = ($1, $2, $3) if ($mutation =~ /^(\S+?)(\d+)(\S+?)$/);
					
					#BLCA    KIAA0090        Silent  TCGA-BL-A0C8    Q8N766  I784I   784     I       I
					print "$tumor_type\t$hugo_symbol\t$variant_classification\t$tumor_sample_barcode\t$chromo\:$start_position\t$reference_allele\->$tumor_seq_allele1\t$uniprot\t$mutation\t$two\t$one\t$three\n";
					
					$uniprot_annotation{$hugo_symbol}{$uniprot} = 1;
					
					#print "$uniprot $mutation\n";
					
					if (($reference_allele ne $tumor_seq_allele1) || ($reference_allele ne $tumor_seq_allele2))
					{
						($wt, $position, $mut) = ($1, $2, $3) if ($mutation =~ /^([a-zA-Z]+)(\d+)([a-zA-Z]+|\*)$/);
						#print "muttype $mut\n";
						$mutations{$hugo_symbol}{$tumor_sample_barcode}{$position} = 1;
						$themut{$hugo_symbol}{$tumor_sample_barcode}{$mutation} = 1;
						$type{$hugo_symbol}{$tumor_sample_barcode}{$position} = $3;
						$tumor_ids{$tumor_sample_barcode} = 1;
						$nonsilent{$hugo_symbol}{$tumor_sample_barcode} = 1 if ($variant_classification !~ /^Silent$/);
						
						$missense{$hugo_symbol}{$tumor_sample_barcode} = 1 if ($variant_classification =~ /^Missense_Mutation$/);
						$mnf{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/));
						$mni{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/) || ($variant_classification =~ /^In_Frame/));
						$code_potential{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/) || ($variant_classification =~ /^In_Frame/) || ($variant_classification =~ /^Nonstop_Mutation$/) || ($variant_classification =~ /^Splice_Site$/) || ($variant_classification =~ /^Translation_Start_Site$/) || ($variant_classification =~ /^De_novo_Start_InFrame$/) || ($variant_classification =~ /^De_novo_Start_OutOfFrame$/));
						
						#Frame_Shift_Del
						#Frame_Shift_Ins
						#In_Frame_Del
						#In_Frame_Ins
						#Missense_Mutation
						#Nonsense_Mutation
						#Silent
						#Splice_Site
						#Translation_Start_Site
						#Nonstop_Mutation
						#3'UTR
						#3'Flank
						#5'UTR
						#5'Flank
						#IGR #intergenic region
						#Intron
						#RNA
						#Targeted_Region
						#Indel
						#De_novo_Start_InFrame
						#De_novo_Start_OutOfFrame
						
						
						
						#print "$hugo_symbol $tumor_sample_barcode $wt -> $mut mutation $mutation at position $position\n";
					}
				}
				else
				{
					print "warning: tumor sample barcode $tumor_sample_barcode matches normal sample barcode $matched_norm_sample_barcode\n$line\n";
				}
			}
			elsif ((($line =~ /^(\S*?)\t(\S*?)\t\S*?\t\S*?\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t\S*?\t\S*?\t(\S+\-\S*?)\t(\S+\-\S*?)\t/) && ($line !~ /^\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t\S*?\t.+\t\S{6}\S*?\t\S*?\t.+?:p\.\w+\d+\S+?,.*\t/)) || (($line =~ /^(\S*?)\t(\S*?)\t\S*?\t\S*?\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t\S*?\t\S*?\t(\S+\-\S*?)\t(\S+\-\S*?)\t/) && (($line =~ /NO UNIPROT MATCH/) || ($line =~ /NO ISOFORM MATCH/) || ($line =~ /NO UNIPROT ID/))))
			{
				if ($line =~ /^(\S*?)\t(\S*?)\t\S*?\t\S*?\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t\S*?\t\S*?\t(\S+\-\S*?)\t(\S+\-\S*?)\t/)
				{
					($hugo_symbol, $entrez_gene_id, $chromo, $start_position, $end_position, $strand, $variant_classification, $variant_type, $reference_allele, $tumor_seq_allele1, $tumor_seq_allele2, $tumor_sample_barcode, $matched_norm_sample_barcode) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13);
					
					if ($tumor_sample_barcode ne $matched_norm_sample_barcode)
					{
						if ($tumor_sample_barcode =~ /^(\w+?)\-(\w{2})\-(\w{4})\-/)
						{
							#looks good, do nothing
						}
						elsif ($tumor_sample_barcode =~ /^(\w+?\-\w+?)\-(\w{2})\-(\w{4})\-/)
						{
							#barcode has been modified
							$tumor_sample_barcode = "TCGA-" . $2 . "-" . $3 . "-";
						}
						
						$tumor_sample_barcode = $1 || die "die: could not truncate tumor sample barcode" if ($tumor_sample_barcode =~ /^(\S+?\-\S+?\-\S+?)\-/);
						
						if (not(defined($annotation_seen{$hugo_symbol}{$tumor_sample_barcode}{$start_position})))
						{
							if (($reference_allele ne $tumor_seq_allele1) || ($reference_allele ne $tumor_seq_allele2))
							{
								#set an arbitrary position since we do not have the actual annotation
								$position = 999999999;
								
								$manual_type = "fs" if (($variant_classification eq	"Frame_Shift_Del") || ($variant_classification eq	"Frame_Shift_Ins"));
								$manual_type = "X" if ($variant_classification eq	"Nonsense_Mutation");
								
								print "$tumor_type\t$hugo_symbol\t$variant_classification\t$tumor_sample_barcode\t$chromo\:$start_position\t$reference_allele\->$tumor_seq_allele1\tUNIPROT_FAIL\tUNIPROT_FAIL\n";
								
								$mutations{$hugo_symbol}{$tumor_sample_barcode}{$position} = 1;
								$type{$hugo_symbol}{$tumor_sample_barcode}{$position} = $manual_type;
								$tumor_ids{$tumor_sample_barcode} = 1;
								$nonsilent{$hugo_symbol}{$tumor_sample_barcode} = 1 if ($variant_classification !~ /^Silent$/);
								#print "$hugo_symbol $tumor_sample_barcode $wt -> $mut mutation $mutation at position $position\n";

								$missense{$hugo_symbol}{$tumor_sample_barcode} = 1 if ($variant_classification =~ /^Missense_Mutation$/);
								$mnf{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/));
								$mni{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/) || ($variant_classification =~ /^In_Frame/));
								$code_potential{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/) || ($variant_classification =~ /^In_Frame/) || ($variant_classification =~ /^Nonstop_Mutation$/) || ($variant_classification =~ /^Splice_Site$/) || ($variant_classification =~ /^Translation_Start_Site$/) || ($variant_classification =~ /^De_novo_Start_InFrame$/) || ($variant_classification =~ /^De_novo_Start_OutOfFrame$/));

							}
						}
					}
				}
				else
				{
					print "blah warning: tumor sample barcode $tumor_sample_barcode matches normal sample barcode $matched_norm_sample_barcode\n$line\n";
				}
			}
			else
			{
				warn "warn: could not parse line $line\n";
			}
		}
	}
	close (MAF);
}
####################################################################################################

