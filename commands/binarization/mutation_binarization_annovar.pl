#!/usr/bin/perl

use strict;
use warnings;

use File::Basename;
use Cwd qw(abs_path);

use lib dirname(abs_path(__FILE__)) . "/../../gidget/util";
use gidget_util;



my $VERSION = "7.1";


my $maf_file = $ARGV[0] || die "usage: $0 MAF_FILE\n";
my $databaseDirectory = $gidgetConfigVars{'TCGABINARIZATION_DATABASE_DIR'} || die "did not get config variable\n";

print "\n" . basename(abs_path(__FILE__)) . " version $VERSION\n\n";
print "using:\n";
print "  database directory => $databaseDirectory\n";
print "  input MAF file => $maf_file\n";
print "\n";

&read_tcga_mutation_data;

&define_dna_binding_domains;

##potentially lots of unnecessary code in these two routines as they were taken from DoDoMa web server
&read_interpro_domain_info;
&extract_domain_sequences;

&binarize;

&print_matrix;


####################################################################################################
sub read_tcga_mutation_data
{
	my %uniprot_annotation = ();
	my %mutations = ();
	my %themut = ();
	my %tumor_ids = ();
	my %nonsilent = ();
	my %missense = ();
	my %mnf = ();
	my %mni = ();
	my %code_potential = ();
	my %annotation_seen = ();
	open (MAF, "< $maf_file") || die "cannot read maf file: $!\n";
	while (my $line = <MAF>)
	{
		unless (($line =~ /^\#version/) || ($line =~ /^\Hugo_Symbol/))
		{
			if (($line =~ /^(\S*?)\t(\S*?)\t\S*?\t\S*?\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t(\S*?)\t\S*?\t\S*?\t(\S*?)\t(\S*?)\t.+\t(\S{6})\S*?\t\S*?\t.+?:p\.(\w+\d+\S+?),.*\t/) && ($line !~ /NO UNIPROT MATCH/) && ($line !~ /NO ISOFORM MATCH/) && ($line !~ /NO UNIPROT ID/))
			{
				my $hugo_symbol = "UNDEFINED";
				my $entrez_gene_id = "UNDEFINED";
				my $chromo = "UNDEFINED";
				my $start_position = "UNDEFINED";
				my $end_position = "UNDEFINED";
				my $strand = "UNDEFINED";
				my $variant_classification = "UNDEFINED";
				my $variant_type = "UNDEFINED";
				my $reference_allele = "UNDEFINED";
				my $tumor_seq_allele1 = "UNDEFINED";
				my $tumor_seq_allele2 = "UNDEFINED";
				my $tumor_sample_barcode = "UNDEFINED";
				my $matched_norm_sample_barcode = "UNDEFINED";
				my $uniprot = "UNDEFINED";
				my $mutation = "UNDEFINED";
				($hugo_symbol, $entrez_gene_id, $chromo, $start_position, $end_position, $strand, $variant_classification, $variant_type, $reference_allele, $tumor_seq_allele1, $tumor_seq_allele2, $tumor_sample_barcode, $matched_norm_sample_barcode, $uniprot, $mutation) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15);
				
				if ($tumor_sample_barcode ne $matched_norm_sample_barcode)
				{
					if ($tumor_sample_barcode =~ /^(\w+?)\-(\w{2})\-(\w{4})\-(\w{2})\-/)
					{
						#looks good, do nothing
					}
					elsif ($tumor_sample_barcode =~ /^(\w+?\-\w+?)\-(\w{2})\-(\w{4})\-(\w{2})\-/)
					{
						#barcode has been modified
						$tumor_sample_barcode = "TCGA-" . $2 . "-" . $3 . "-" . $4 . "-" ;
					}
					
					$tumor_sample_barcode = $1 || die "die: could not truncate tumor sample barcode" if ($tumor_sample_barcode =~ /^(\S+?\-\S+?\-\S+?\-\S+?)\-/);
					
					$annotation_seen{$hugo_symbol}{$tumor_sample_barcode}{$start_position} = 1;
					
					if ($uniprot =~ /^http/)
					{
						if ($line =~ /^.+\t(\S{6})\S*?\t.+?:p\.(\w+\d+\S+?),.*\t/)
						{
							($uniprot, $mutation) = ($1, $2);
						}
					}
					
					#print "$uniprot\t$line\n";
					
					$uniprot_annotation{$hugo_symbol}{$uniprot} = 1;
					
					#print "$uniprot $mutation\n";
					
					if (($reference_allele ne $tumor_seq_allele1) || ($reference_allele ne $tumor_seq_allele2))
					{
						my $wt = "UNDEFINED";
						my $position = "UNDEFINED";
						my $mut = "UNDEFINED";
						($wt, $position, $mut) = ($1, $2, $3) if ($mutation =~ /^([a-zA-Z]+)(\d+)([a-zA-Z]+|\*)$/);
						$wt = "CURRENTLY_UNUSED"; # slience perl warning
						$mut = "CURRENTLY_UNUSED"; # slience perl warning
						#print "muttype $mut\n";
						$mutations{$hugo_symbol}{$tumor_sample_barcode}{$position} = 1;
						$themut{$hugo_symbol}{$tumor_sample_barcode}{$mutation} = 1;
						my %type = (); # TODO should this be initialzied above, along with other hashes?
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
					my $hugo_symbol = "UNDEFINED";
					my $entrez_gene_id = "UNDEFINED";
					my $chromo = "UNDEFINED";
					my $start_position = "UNDEFINED";
					my $end_position = "UNDEFINED";
					my $strand = "UNDEFINED";
					my $variant_classification = "UNDEFINED";
					my $variant_type = "UNDEFINED";
					my $reference_allele = "UNDEFINED";
					my $tumor_seq_allele1 = "UNDEFINED";
					my $tumor_seq_allele2 = "UNDEFINED";
					my $tumor_sample_barcode = "UNDEFINED";
					my $matched_norm_sample_barcode = "UNDEFINED";
					($hugo_symbol, $entrez_gene_id, $chromo, $start_position, $end_position, $strand, $variant_classification, $variant_type, $reference_allele, $tumor_seq_allele1, $tumor_seq_allele2, $tumor_sample_barcode, $matched_norm_sample_barcode) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13);
					
					if ($tumor_sample_barcode ne $matched_norm_sample_barcode)
					{
						if ($tumor_sample_barcode =~ /^(\w+?)\-(\w{2})\-(\w{4})\-(\w{2})\-/)
						{
							#looks good, do nothing
						}
						elsif ($tumor_sample_barcode =~ /^(\w+?\-\w+?)\-(\w{2})\-(\w{4})\-(\w{2})\-/)
						{
							#barcode has been modified
							$tumor_sample_barcode = "TCGA-" . $2 . "-" . $3 . "-" . $4 . "-" ;
						}
						
						$tumor_sample_barcode = $1 || die "die: could not truncate tumor sample barcode" if ($tumor_sample_barcode =~ /^(\S+?\-\S+?\-\S+?\-\S+?)\-/);
						
						if (not(defined($annotation_seen{$hugo_symbol}{$tumor_sample_barcode}{$start_position})))
						{
							if (($reference_allele ne $tumor_seq_allele1) || ($reference_allele ne $tumor_seq_allele2))
							{
								#set an arbitrary position since we do not have the actual annotation
								my $position = 999999999;
								
								my $manual_type = "fs" if (($variant_classification eq	"Frame_Shift_Del") || ($variant_classification eq	"Frame_Shift_Ins"));
								$manual_type = "X" if ($variant_classification eq	"Nonsense_Mutation");
								
								$mutations{$hugo_symbol}{$tumor_sample_barcode}{$position} = 1;
								my %type = (); # TODO should this be initialzied above, along with other hashes?
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
				{	my $tumor_sample_barcode = "[variable out of scope!]"; # TODO !
					my $matched_norm_sample_barcode = "[variable out of scope!]"; # TODO !
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

###################################################################################################################
sub define_dna_binding_domains
{
	my %interpro_dna_binding_domains = ();
	my @domain_contents = ();
	$#domain_contents = -1; # TODO why?
	open (DOMAINS, "< $gidgetConfigVars{'TCGABINARIZATION_DATABASE_DIR'}/TRANSFAC_2010.1/interpro_domains_vaquerizas_nature_2009.txt") || die "cannot read tf list file: $!\n";
	@domain_contents = <DOMAINS>;
	close (DOMAINS);
	foreach my $line (@domain_contents)
	{
		if ($line =~ /^(\S+)\s+(\S+)$/)
		{
			my $interpro_id = "UNDEFINED";
			my $domain_or_family = "UNDEFINED";
			($interpro_id, $domain_or_family) = ($1, $2);
			$domain_or_family = "CURRENTLY_UNUSED"; # slience perl warning
			$interpro_dna_binding_domains{$interpro_id} = 1;
			#print "$interpro_id\n";
		}
	}
}
###################################################################################################################

###################################################################################################################
my %species = (); # TODO move to the top of the file?
sub read_interpro_domain_info
{
	my %domain_sequences = ();
	my %zero_match = ();
	my %dna_binding_domain = ();
	#$mutations{$hugo_symbol}
	my %mutations = (); # TODO see next line's comment
	foreach my $hugo_symbol (sort keys %mutations) # TODO how is this possibly working? %mutations isn't defined here!
	{
		my %uniprot_annotation = ();  # TODO see next line's comment
		foreach my $uniprot_id (sort keys %{$uniprot_annotation{$hugo_symbol}}) # TODO how is this possibly working? %mutations isn't defined here!
		#foreach $uniprot_id (sort keys %{$hgnc_to_uniprot{$hugo_symbol}})
		{
			my @interpro_contents = ();
			$#interpro_contents = -1; # TODO why?
			open (INTERPRO, "< $gidgetConfigVars{'TCGABINARIZATION_DATABASE_DIR'}/interpro/data/$uniprot_id.txt") || warn "cannot read interpro file for $uniprot_id: $!\n";
			@interpro_contents = <INTERPRO>;
			close (INTERPRO);
			
			my $found_domain = 0;
			# $#non_dbd = -1; # currently unused
			for (my $ln=0; $ln <= $#interpro_contents; $ln++)
			{
				my $line = $interpro_contents[$ln];
				my $previous_line = $interpro_contents[$ln-1];
				if (($line =~ /\<ipr id\=\"(\S+)\"/) || (($previous_line =~ /dbname\=\"PROFILE\"/) || ($previous_line =~ /dbname\=\"PFAM\"/) || ($previous_line =~ /dbname\=\"SMART\"/))) #interpro data - need to get id and sequences associated with id, second part is because not all other ids (pfam, etc) have assigned interpro ids
				{
					my $interpro_id = "";
					$interpro_id = $1 if ($line =~ /\<ipr id\=\"(\S+)\"/);
					
					#print "interpro: $interpro_id\n";
					#print "pl $previous_line\n";
					#print "this l $line\n";
					
					#only keep the domains that are predicted by PROSITE profile, Pfam, and SMART
					if (($previous_line =~ /dbname\=\"PROFILE\"/) || ($previous_line =~ /dbname\=\"PFAM\"/) || ($previous_line =~ /dbname\=\"SMART\"/))
					{
						my $dna_binding = 0;
						# TODO the next line makes no sense as %interpro_dna_binding_domains is not defined here
						# !!commenting out next line!!
						#$dna_binding = 1 if (defined($interpro_dna_binding_domains{$interpro_id})); # we have flagged this interpro domain as dna binding
						$found_domain = 1;
						$ln++ if ($interpro_id =~ /\S+/);
						my $next_line = $interpro_contents[$ln];
						#print "nl $next_line\n";
						if ($next_line =~ /\<lcn start\=\"(\d+)\" end\=\"(\d+)\"/)
						{
							my $current_start = "UNDEFINED";
							my $current_end = "UNDEFINED";
							($current_start, $current_end) = ($1, $2);
							
							my $add_current = my $reject_current = 0; # initialize these values, look through all existing sequence segments, and decide what to do
							if (defined($domain_sequences{$uniprot_id}))
							{
								foreach my $startend (keys %{$domain_sequences{$uniprot_id}})
								{
									if ($startend =~ /^(\d+)_(\d+)$/)
									{	
										my $existing_start = "UNDEFINED";
										my $existing_end = "UNDEFINED";
										($existing_start, $existing_end) = ($1, $2);
									}
									else
									{
										die "die: cannot parse starting and ending sequence coordinates\n";
									}
									# TODO these lines make no sense; undefined variables
									my $existing_start = "UNDEFINED";
									my $existing_end = "UNDEFINED";
									my $current_length = $current_end - $current_start; # TODO: is these supposed to be a new variable?
									my $existing_length = $existing_end - $existing_start; # TODO: is these supposed to be a new variable?
									
									if (($existing_start == $current_start) && ($existing_end == $current_end)) # perfect match
									{
										$add_current = 1;
									}
									elsif ($current_end <= $existing_start) # completely different
									{
										$add_current = 1;
									}
									elsif ($existing_end <= $current_start) # completely different
									{
										$add_current = 1;
									}
									elsif (($existing_start > $current_start) && ($existing_end > $current_end) && ($current_end > $existing_start)) # shifted match with existing being towards right, so keep smallest
									{
										if ($current_length < $existing_length) #undefine existing and define current
										{
											delete $domain_sequences{$uniprot_id}{$startend};
											#print "removing $startend\n";
											$add_current = 1;
										}
										else #reject current and keep existing
										{
											$reject_current = 1;
										}
									}
									elsif (($existing_start < $current_start) && ($existing_end < $current_end) && ($existing_end > $current_start)) # shifted match with existing being towards left, so keep smallest
									{
										if ($current_length < $existing_length) #undefine existing and define current
										{
											delete $domain_sequences{$uniprot_id}{$startend};
											#print "removing $startend\n";
											$add_current = 1;
										}
										else #ignore current and keep existing
										{
											$reject_current = 1;
										}
									}
									elsif ($existing_start == $current_start) #match left, so keep smallest
									{
										if ($current_length < $existing_length) #undefine existing and define current
										{
											delete $domain_sequences{$uniprot_id}{$startend};
											#print "removing $startend\n";
											$add_current = 1;
										}
										else #ignore current and keep existing
										{
											$reject_current = 1;
										}
									}
									elsif ($existing_end == $current_end) #match right, so keep smallest
									{
										if ($current_length < $existing_length) #undefine existing and define current
										{
											#print "match right existing $startend ($existing_length) current $current_start\_$current_end ($current_length) - removing existing\n";
											delete $domain_sequences{$uniprot_id}{"$startend"};
											#print "removing $startend\n";
											$add_current = 1;
										}
										else #ignore current and keep existing
										{
											#print "match right existing $startend ($existing_length) current $current_start\_$current_end ($current_length) - ignoring current\n";
											$reject_current = 1;
										}
									}
									elsif (($existing_start < $current_start) && ($existing_end > $current_end)) # current is smaller, so undefine existing and define current
									{
										delete $domain_sequences{$uniprot_id}{"$startend"};
										#print "removing $startend\n";
										$add_current = 1;
									}
									elsif (($existing_start > $current_start) && ($existing_end < $current_end)) # current is larger, so ignore and keep existing
									{
										$reject_current = 1;
									}
									else
									{
										die "die: do not know how to handle $uniprot_id $interpro_id existing $existing_start $existing_end compared to $current_start $current_end\n";
									}
								}
								if (($add_current > 0) && ($reject_current < 1))
								{
									$domain_sequences{$uniprot_id}{"$current_start\_$current_end"} = 1;
									$dna_binding_domain{$hugo_symbol}{"$current_start\_$current_end"} = 1 if ($dna_binding > 0);
									#print "adding $current_start\_$current_end\n";
								}
							}
							else
							{
								$domain_sequences{$uniprot_id}{"$current_start\_$current_end"} = 1; #these segments are what we will use for blasting and identifying other swissprot ids with matrices in transfac
								$dna_binding_domain{$hugo_symbol}{"$current_start\_$current_end"} = 1 if ($dna_binding > 0);
							}
						}
					}
				}
			}
			if ($found_domain < 1)
			{
				my @uniprot_contents = ();
				$#uniprot_contents = -1; # TODO why?
				unless (-e "$gidgetConfigVars{'TCGABINARIZATION_DATABASE_DIR'}/uniprot/data/$uniprot_id.txt")
				{
					#print "downloading $uniprot_id from uniprot\n";
					`wget -q -O "$gidgetConfigVars{'TCGABINARIZATION_DATABASE_DIR'}/uniprot/data/$uniprot_id.txt"  "http://www.uniprot.org/uniprot/$uniprot_id.fasta"`;
				}
				open (UNIPROT, "< $gidgetConfigVars{'TCGABINARIZATION_DATABASE_DIR'}/uniprot/data/$uniprot_id.txt") || die "cannot read uniprot file: $!\n";
				@uniprot_contents = <UNIPROT>;
				close (UNIPROT);
				my $head = shift @uniprot_contents;
				$species{$uniprot_id} = $1 if ($head =~ /OS\=(.+?)\s+\S+\=/);
				
				#since we did not find dna binding domains, we need to consider the entire sequence to be the DBD for our homology search
				#also need to account for the fact that the matches do not have defined DBDs either, so the number of DBDs between search and match will both be zero
				chomp @uniprot_contents;
				my $sequence = join('', @uniprot_contents);
				my $query_seq_length = length $sequence;
				$domain_sequences{$uniprot_id}{"1_$query_seq_length"} = 1;
				$zero_match{$uniprot_id} = 1;
				
				
				#warn "warning: no domain(s) found in $hugo_symbol $uniprot_id ($species{$uniprot_id}) - using entire sequence\n";
				#foreach $other_domain (@non_dbd)
				#{
				#	#warn "warning: $uniprot_id ($species{$uniprot_id}) did find $other_domain\n";
				#}
			}
			last;
		}
	}
}
###################################################################################################################

###################################################################################################################
sub extract_domain_sequences
{
	my %query_seq_lengths = ();
	my %sortable_domain_sequences = ();
	my %mutations = (); # TODO see next line
	foreach my $hugo_symbol (sort keys %mutations) # TODO how does this even work?
	{
		my %uniprot_annotation = ();
		foreach my $uniprot_id (sort keys %{$uniprot_annotation{$hugo_symbol}}) # TODO how does this even work?
		{
			my @uniprot_contents = ();
			$#uniprot_contents = -1; # TODO why?
			unless (-e "$gidgetConfigVars{'TCGABINARIZATION_DATABASE_DIR'}/uniprot/data/$uniprot_id.txt")
			{
				#print "downloading $uniprot_id from uniprot\n";
				`wget -q -O "$gidgetConfigVars{'TCGABINARIZATION_DATABASE_DIR'}/uniprot/data/$uniprot_id.txt"  "http://www.uniprot.org/uniprot/$uniprot_id.fasta"`;
			}
			open (UNIPROT, "< $gidgetConfigVars{'TCGABINARIZATION_DATABASE_DIR'}/uniprot/data/$uniprot_id.txt") || die "cannot read uniprot file: $!\n";
			@uniprot_contents = <UNIPROT>;
			close (UNIPROT);
			my $head = shift @uniprot_contents;
			$species{$uniprot_id} = $1 if ($head =~ /OS\=(.+?)\s+\S+\=/);
			chomp @uniprot_contents;
			my $sequence = join('', @uniprot_contents);
			my $query_seq_length = length $sequence;
			$query_seq_lengths{$uniprot_id} = $query_seq_length;
			#print "$sequence\n";
			
			my %domain_sequences = (); # see next comment
			foreach my $startend (sort keys %{$domain_sequences{$uniprot_id}}) # TODO how does this even work?
			{
				#print "$hugo_symbol $uniprot_id kept $startend for evaluation\n";
				
				if ($startend =~ /^(\d+)_(\d+)$/)
				{
					my $this_start = "UNDEFINED";
					my $this_end = "UNDEFINED";
					($this_start, $this_end) = ($1, $2);
				}
				else
				{
					die "die: cannot parse starting and ending sequence coordinates\n";
				}
				#add one to the domain length to make sure we get full substring
				my $this_start = "UNDEFINED";
				my $this_end = "UNDEFINED";
				my $domain_length = $this_end - $this_start + 1; # TODO how could this work? scope issue
				#subtract one from start position to go from 1-based domain position to 0-based substring
				my $subsequence = substr($sequence,$this_start-1,$domain_length);
				#print "$uniprot_id $startend $subsequence\n";
				
				$sortable_domain_sequences{$hugo_symbol}{$this_start}{$startend} = $subsequence;
			}
			#do this only for one uniprot id that is cross referenced to hgnc
			last;
		}
	}
}
###################################################################################################################

###################################################################################################################
sub binarize
{
	
	my %binarization = ();
	my %dna_bin = ();
	
	my %tumor_ids = ();
	foreach my $sample (sort keys %tumor_ids) # TODO how could this work?
	{
		my %mutations = ();
		foreach my $hugo_symbol (sort keys %mutations) # TODO how could this work?
		{
			foreach my $position (sort {$a <=> $b} keys %{$mutations{$hugo_symbol}{$sample}})
			{
				my %type = ();
				my $mut_type = $type{$hugo_symbol}{$sample}{$position}; # TODO how could this work?
				
				my %sortable_domain_sequences = ();
				foreach my $domain_start (sort {$a <=> $b} keys %{$sortable_domain_sequences{$hugo_symbol}}) # TODO how could this work?
				{
					foreach my $startend (sort keys %{$sortable_domain_sequences{$hugo_symbol}{$domain_start}})
					{
						#print "$startend from $hugo_symbol $domain_start\n";
						
						if ($startend =~ /^(\d+)_(\d+)$/)
						{
							my $this_start = "UNDEFINED";
							my $this_end = "UNDEFINED";
							($this_start, $this_end) = ($1, $2);
						}
						my $statement = "not_within";

						my $this_start = "UNDEFINED";
						my $this_end = "UNDEFINED";
						$statement = "within" if (($position >= $this_start) && ($position <= $this_end)); # TODO variable scope issue
						#print "$sample $hugo_symbol $position $statement $this_start $this_end\n";
						#print "$sample $hugo_symbol dna_binding\n" if (defined($dna_binding_domain{$hugo_symbol}{$startend}));
						
						# TODO: this makes no sense as dna_binding_domain isn't defined!
						# !!! commenting out line below!
						# $dna_bin{$sample}{$hugo_symbol} = 1  if (defined($dna_binding_domain{$hugo_symbol}{$startend}) && ($position >= $this_start) && ($position <= $this_end));
						
						my %nsfs = (); # scope issue?
						$nsfs{$sample}{$hugo_symbol}{$domain_start}{$startend} = 1  if ((($mut_type eq "*") || ($mut_type eq "fs") || ($mut_type eq "X")) && ($position <= $this_end)); # TODO how does this even work? see above line
						
						$binarization{$sample}{$hugo_symbol}{$domain_start}{$startend} = 1 if (($position >= $this_start) && ($position <= $this_end));
					}
				}
			}
		}
	}
}
###################################################################################################################

###################################################################################################################
sub print_matrix
{
	my $counter = 0;
	my $head = "";

	my %tumor_ids = (); # TODO scope?
	foreach my $sample (sort keys %tumor_ids) # TODO how could this work?
	{
		my $vector = "$sample";

		my %sortable_domain_sequences = (); # TODO scope
		foreach my $hugo_symbol (sort keys %sortable_domain_sequences) # TODO how could this work?
		{
			my $head .= "\t$hugo_symbol\_y_n";

			my %mutations = (); # scope?
			my $num = keys %{$mutations{$hugo_symbol}{$sample}}; # TODO how could this work?
			if ($num > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			$head .= "\t$hugo_symbol\_nonsilent";

			my %nonsilent = (); # TODO scope?
			$num = $nonsilent{$hugo_symbol}{$sample}; # TODO how could this work?

			if ($num > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			$head .= "\t$hugo_symbol\_dna_bin";

			my %dna_bin = (); # TODO scope?
			$num = $dna_bin{$sample}{$hugo_symbol}; # TODO how could this work?
			if ($num > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			###############
			$head .= "\t$hugo_symbol\_missense";

			my %missense = (); # TODO scope?
			$num = $missense{$hugo_symbol}{$sample}; # TODO how could this work?
			if ($num > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			$head .= "\t$hugo_symbol\_mnf";

			my %mnf = ();
			$num = $mnf{$hugo_symbol}{$sample}; # TODO how could this work?
			if ($num > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			$head .= "\t$hugo_symbol\_mni";

			my %mni = ();
			$num = $mni{$hugo_symbol}{$sample}; # TODO how could this work?
			if ($num > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			$head .= "\t$hugo_symbol\_code_potential";

			my %code_potential = ();
			$num = $code_potential{$hugo_symbol}{$sample}; # TODO how could this work?
			if ($num > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			###############
			
			foreach my $domain_start (sort {$a <=> $b} keys %{$sortable_domain_sequences{$hugo_symbol}})
			{
				foreach my $startend (sort keys %{$sortable_domain_sequences{$hugo_symbol}{$domain_start}})
				{
					$head .= "\t$hugo_symbol\_dom_$startend\_ns_or_fs";
					my $binary = 0;

					my %nsfs = ();
					$binary = 1 if ($nsfs{$sample}{$hugo_symbol}{$domain_start}{$startend} > 0); # TODO how could this work?
					$vector .= "\t$binary";
					
					
					$head .= "\t$hugo_symbol\_dom_$startend";
					$binary = 0;

					my %binarization = ();
					$binary = 1 if ($binarization{$sample}{$hugo_symbol}{$domain_start}{$startend} > 0); # TODO how could this work?
					#print "$sample $hugo_symbol $domain_start $startend $binary\n";
					$vector .= "\t$binary";
				}
			}
		}
		print "$head\n" if ($counter < 1);
		print "$vector\n";
		$counter++;
	}
}
###################################################################################################################

