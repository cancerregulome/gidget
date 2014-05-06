#!/usr/bin/perl

use strict;
use warnings;

use File::Basename;
use Cwd qw(abs_path);

use lib dirname(abs_path(__FILE__)) . "/../../gidget/util";
use gidget_util;



my $VERSION = "8.0";


my $maf_file = $ARGV[0] || die "usage: $0 MAF_FILE\n";
my $databaseDirectory = $gidgetConfigVars{'TCGABINARIZATION_DATABASE_DIR'} || die "did not get config variable\n";

print "\n" . basename(abs_path(__FILE__)) . " version $VERSION\n\n";
print "using:\n";
print "  database directory => $databaseDirectory\n";
print "  input MAF file => $maf_file\n";
print "\n";


###
# globals:
my %mutations_hash = ();
my %uniprot_annotations_hash = ();
my %tumor_ids_hash = ();
my %nonsilence_hash = ();
my %missense_hash = ();
my %mnf_hash = ();
my %mni_hash = ();
my %code_potential_hash = ();
my %type_hash = ();



#print "reading TCGA mutation data...\n";
&read_tcga_mutation_data($maf_file,
						 \%mutations_hash,
						 \%uniprot_annotations_hash,
						 \%tumor_ids_hash,
						 \%nonsilence_hash,
						 \%missense_hash,
						 \%mnf_hash,
						 \%mni_hash,
						 \%code_potential_hash,
						 \%type_hash);
#print "...done\n\n";



####
# global:
my %interpro_dna_binding_domains_hash = ();


#print "loading interpro dna binding domains...\n";
&define_dna_binding_domains($databaseDirectory,
							\%interpro_dna_binding_domains_hash);
#print "...done\n\n";


#potentially lots of unnecessary code in this routines as is was taken from DoDoMa web server
###
# global:
my %domain_sequences_hash = ();
my %dna_binding_domain_hash = ();
my %species_hash = ();


#print "reading interpro domain info...\n";
&read_interpro_domain_info($databaseDirectory,
						   \%mutations_hash,
						   \%uniprot_annotations_hash,
						   \%domain_sequences_hash,
						   \%dna_binding_domain_hash,
						   \%species_hash,
						   \%interpro_dna_binding_domains_hash);
#print "...done\n\n";



#potentially lots of unnecessary code in this routines as is was taken from DoDoMa web server
###
# global:
my %sortable_domain_sequences_hash = ();


#print "extracting domain sequences...\n";
&extract_domain_sequences($databaseDirectory,
						  \%mutations_hash,
						  \%uniprot_annotations_hash,
						  \%domain_sequences_hash,
						  \%sortable_domain_sequences_hash,
						  \%species_hash);
#print "...done\n\n";



###
# globals:
my %nsfs_hash = ();
my %dna_bin_hash = ();
my %binarization_hash = ();


#print "binarizing...\n";
&binarize(\%tumor_ids_hash,
		  \%mutations_hash,
		  \%uniprot_annotations_hash,
		  \%type_hash,
		  \%sortable_domain_sequences_hash,
		  \%dna_bin_hash,
		  \%dna_binding_domain_hash,
		  \%nsfs_hash,
		  \%binarization_hash);
#print "...done\n\n";



print "printing matrix...\n";
&print_matrix(\%tumor_ids_hash,
		  	  \%mutations_hash,
			  \%sortable_domain_sequences_hash,
		  	  \%nsfs_hash,
		  	  \%nonsilence_hash,
		  	  \%dna_bin_hash,
		  	  \%missense_hash,
		  	  \%mnf_hash,
		  	  \%mni_hash,
		  	  \%code_potential_hash,
		  	  \%binarization_hash);
print "...done\n\n";


exit(0);



###
# subroutines
#



####################################################################################################

###
# sub 
#
# required parameters:
# MAF file name
#
# HASH REFERENCES to:
# mutations
# uniprot_annotation
# 

sub read_tcga_mutation_data
{

	# subroutine parameters
	my $maf_file_name = shift @_;

	# these should all be passed in as blanks; they are poplulated here
	my $mutations_hashRef = shift @_;
	my $uniprot_annotation_hashRef = shift @_;
	my $tumor_ids_hashRef = shift @_;
	my $nonsilent_hashRef = shift @_;
	my $missense_hashRef = shift @_;
	my $mnf_hashRef = shift @_;
	my $mni_hashRef = shift @_;
	my $code_potential_hashRef = shift @_;
	my $type_hashRef = shift @_;


	# subroutine local variables
	#my %themut = (); # never used
	my %annotation_seen = (); # okay-- an actual subroutine local variable


	open (MAF, "< $maf_file_name") || die "cannot read maf file: $!\n";
	while (my $line = <MAF>)
	{
		unless (($line =~ /^\#version/) || ($line =~ /^Hugo_Symbol/))
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
					
					$uniprot_annotation_hashRef->{$hugo_symbol}{$uniprot} = 1;
					
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
						$mutations_hashRef->{$hugo_symbol}{$tumor_sample_barcode}{$position} = 1;
						#$themut{$hugo_symbol}{$tumor_sample_barcode}{$mutation} = 1;
						$type_hashRef->{$hugo_symbol}{$tumor_sample_barcode}{$position} = $3;
						$tumor_ids_hashRef->{$tumor_sample_barcode} = 1;
						$nonsilent_hashRef->{$hugo_symbol}{$tumor_sample_barcode} = 1 if ($variant_classification !~ /^Silent$/);
						
						$missense_hashRef->{$hugo_symbol}{$tumor_sample_barcode} = 1 if ($variant_classification =~ /^Missense_Mutation$/);
						$mnf_hashRef->{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/));
						$mni_hashRef->{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/) || ($variant_classification =~ /^In_Frame/));
						$code_potential_hashRef->{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/) || ($variant_classification =~ /^In_Frame/) || ($variant_classification =~ /^Nonstop_Mutation$/) || ($variant_classification =~ /^Splice_Site$/) || ($variant_classification =~ /^Translation_Start_Site$/) || ($variant_classification =~ /^De_novo_Start_InFrame$/) || ($variant_classification =~ /^De_novo_Start_OutOfFrame$/));
						
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
								
								$mutations_hashRef->{$hugo_symbol}{$tumor_sample_barcode}{$position} = 1;
								$type_hashRef->{$hugo_symbol}{$tumor_sample_barcode}{$position} = $manual_type;
								$tumor_ids_hashRef->{$tumor_sample_barcode} = 1;
								$nonsilent_hashRef->{$hugo_symbol}{$tumor_sample_barcode} = 1 if ($variant_classification !~ /^Silent$/);
								#print "$hugo_symbol $tumor_sample_barcode $wt -> $mut mutation $mutation at position $position\n";

								$missense_hashRef->{$hugo_symbol}{$tumor_sample_barcode} = 1 if ($variant_classification =~ /^Missense_Mutation$/);
								$mnf_hashRef->{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/));
								$mni_hashRef->{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/) || ($variant_classification =~ /^In_Frame/));
								$code_potential_hashRef->{$hugo_symbol}{$tumor_sample_barcode} = 1 if (($variant_classification =~ /^Missense_Mutation$/) || ($variant_classification =~ /^Nonsense_Mutation$/) || ($variant_classification =~ /^Frame_Shift/) || ($variant_classification =~ /^In_Frame/) || ($variant_classification =~ /^Nonstop_Mutation$/) || ($variant_classification =~ /^Splice_Site$/) || ($variant_classification =~ /^Translation_Start_Site$/) || ($variant_classification =~ /^De_novo_Start_InFrame$/) || ($variant_classification =~ /^De_novo_Start_OutOfFrame$/));

							}
						}
					}
					else
					{
						print "blah warning: tumor sample barcode $tumor_sample_barcode matches normal sample barcode $matched_norm_sample_barcode\n$line\n";
					}
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

###
# define_dna_binding_domains
#
# parameters:
# database directory name
# HASH REFERENCE to interpro_dna_binding_domains hash
# 

sub define_dna_binding_domains
{
	my $database_directory_name = shift @_;
	my $interpro_dna_binding_domains_hashRef = shift @_; # should be passed in as blank hash; populated here

	my @domain_file_contents = ();
	open (DOMAINS, "< $database_directory_name/TRANSFAC_2010.1/interpro_domains_vaquerizas_nature_2009.txt") || die "cannot read tf list file: $!\n";
	@domain_file_contents = <DOMAINS>;
	close (DOMAINS);
	foreach my $line (@domain_file_contents)
	{
		if ($line =~ /^(\S+)\s+(\S+)$/)
		{
			#my $domain_or_family = "UNDEFINED";
			#($interpro_id, $domain_or_family) = ($1, $2);
			my $interpro_id = $1;
			#$domain_or_family = "CURRENTLY_UNUSED"; # slience perl warning
			$interpro_dna_binding_domains_hashRef->{$interpro_id} = 1;
			#print "$interpro_id\n";
		}
	}
}
###################################################################################################################



###################################################################################################################

###
# sub read_interpro_domain_info
#
# required parameters:
# database directory name
#
# HASH REFERENCES to:
# mutations
# uniprot_annotation
# domain_sequences
# dna_binding_domain
# species_hash
# interpro_dna_binding_domains
# 

sub read_interpro_domain_info
{
	# subroutine arguments
	my $database_directory_name = shift @_;
	my $mutations_hashRef = shift @_;
	my $uniprot_annotation_hashRef = shift @_;
	my $domain_sequences_hashRef = shift @_;
	my $dna_binding_domain_hashRef = shift @_;
	my $species_hashRef = shift @_;
	my $interpro_dna_binding_domains_hashRef = shift @_;


	# subroutine local variables
	# my %zero_match = (); # never used

	foreach my $hugo_symbol (sort keys %$mutations_hashRef)
	{
		foreach my $uniprot_id (sort keys %{$uniprot_annotation_hashRef->{$hugo_symbol}})
		#foreach $uniprot_id (sort keys %{$hgnc_to_uniprot{$hugo_symbol}})
		{
			my @interpro_file_contents = ();
			open (INTERPRO, "< $database_directory_name/interpro/data/$uniprot_id.txt") || warn "cannot read interpro file for $uniprot_id: $!\n";
			@interpro_file_contents = <INTERPRO>;
			close (INTERPRO);
			
			my $found_domain = 0;
			# $#non_dbd = -1; # currently unused
			for (my $ln=0; $ln <= $#interpro_file_contents; $ln++)
			{
				my $line = $interpro_file_contents[$ln];
				my $previous_line = $interpro_file_contents[$ln-1];
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
						$dna_binding = 1 if (defined($interpro_dna_binding_domains_hashRef->{$interpro_id})); # we have flagged this interpro domain as dna binding
						$found_domain = 1;
						$ln++ if ($interpro_id =~ /\S+/);
						my $next_line = $interpro_file_contents[$ln];
						#print "nl $next_line\n";
						if ($next_line =~ /\<lcn start\=\"(\d+)\" end\=\"(\d+)\"/)
						{
							my $current_start = "UNDEFINED";
							my $current_end = "UNDEFINED";
							($current_start, $current_end) = ($1, $2);
							
							my $add_current = my $reject_current = 0; # initialize these values, look through all existing sequence segments, and decide what to do
							if (defined($domain_sequences_hashRef->{$uniprot_id}))
							{
								foreach my $startend (keys %{$domain_sequences_hashRef->{$uniprot_id}})
								{
									my $existing_start = "UNDEFINED";
									my $existing_end = "UNDEFINED";
									if ($startend =~ /^(\d+)_(\d+)$/)
									{	
										($existing_start, $existing_end) = ($1, $2);
									}
									else
									{
										die "die: cannot parse starting and ending sequence coordinates\n";
									}
									my $current_length = $current_end - $current_start;
									my $existing_length = $existing_end - $existing_start;
									
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
											delete $domain_sequences_hashRef->{$uniprot_id}{$startend};
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
											delete $domain_sequences_hashRef->{$uniprot_id}{$startend};
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
											delete $domain_sequences_hashRef->{$uniprot_id}{$startend};
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
											delete $domain_sequences_hashRef->{$uniprot_id}{"$startend"};
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
										delete $domain_sequences_hashRef->{$uniprot_id}{"$startend"};
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
									$domain_sequences_hashRef->{$uniprot_id}{"$current_start\_$current_end"} = 1;
									$dna_binding_domain_hashRef->{$hugo_symbol}{"$current_start\_$current_end"} = 1 if ($dna_binding > 0);
									#print "adding $current_start\_$current_end\n";
								}
							}
							else
							{
								$domain_sequences_hashRef->{$uniprot_id}{"$current_start\_$current_end"} = 1; #these segments are what we will use for blasting and identifying other swissprot ids with matrices in transfac
								$dna_binding_domain_hashRef->{$hugo_symbol}{"$current_start\_$current_end"} = 1 if ($dna_binding > 0);
							}
						}
					}
				}
			}
			if ($found_domain < 1)
			{
				my @uniprot_file_contents = ();

				my $uniprot_id_file_name = "$database_directory_name/uniprot/data/$uniprot_id.txt";
				unless (-e "$uniprot_id_file_name")
				{
					#print "downloading $uniprot_id from uniprot\n";
					`wget -q -O "$uniprot_id_file_name"  "http://www.uniprot.org/uniprot/$uniprot_id.fasta"`;
				}
				open (UNIPROT, "< $uniprot_id_file_name") || die "cannot read uniprot file: $!\n";
				@uniprot_file_contents = <UNIPROT>;
				close (UNIPROT);
				my $head = shift @uniprot_file_contents;
				$species_hashRef->{$uniprot_id} = $1 if ($head =~ /OS\=(.+?)\s+\S+\=/);
				
				#since we did not find dna binding domains, we need to consider the entire sequence to be the DBD for our homology search
				#also need to account for the fact that the matches do not have defined DBDs either, so the number of DBDs between search and match will both be zero
				chomp @uniprot_file_contents;
				my $sequence = join('', @uniprot_file_contents);
				my $query_seq_length = length $sequence;
				$domain_sequences_hashRef->{$uniprot_id}{"1_$query_seq_length"} = 1;
				#$zero_match{$uniprot_id} = 1;
				
				
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

###
# sub extract_domain_sequences
#
# required parameters:
# database directory name
#
# HASH REFERENCES to:
# mutation
# uniprot_annotation
# domain_sequences
# sortable_domain_sequences
# species
#

sub extract_domain_sequences
{

	#subroutine parameters
	my $database_directory_name = shift @_;

	my $mutations_hashRef = shift @_;
	my $uniprot_annotation_hashRef = shift @_;
	my $domain_sequences_hashRef = shift @_;
	my $sortable_domain_sequences_hashRef = shift @_;
	my $species_hashRef = shift @_;

	# subroutine local variables
	# my %query_seq_lengths = (); # never actually used

	foreach my $hugo_symbol (sort keys %$mutations_hashRef)
	{
		foreach my $uniprot_id (sort keys %{$uniprot_annotation_hashRef->{$hugo_symbol}})
		{
			my @uniprot_file_contents = ();
			my $uniprot_id_file_name = "$database_directory_name/uniprot/data/$uniprot_id.txt";
			unless (-e "$uniprot_id_file_name")
			{
				#print "downloading $uniprot_id from uniprot\n";
				`wget -q -O "$uniprot_id_file_name"  "http://www.uniprot.org/uniprot/$uniprot_id.fasta"`;
			}

			open (UNIPROT, "< $uniprot_id_file_name") || die "cannot read uniprot file: $!\n";
			@uniprot_file_contents = <UNIPROT>;
			close (UNIPROT);

			my $head = shift @uniprot_file_contents;
			$species_hashRef->{$uniprot_id} = $1 if ($head =~ /OS\=(.+?)\s+\S+\=/);
			chomp @uniprot_file_contents;
			my $sequence = join('', @uniprot_file_contents);
			my $query_seq_length = length $sequence;
			# $query_seq_lengths{$uniprot_id} = $query_seq_length;
			# print "$sequence\n";
			
			foreach my $startend (sort keys %{$domain_sequences_hashRef->{$uniprot_id}})
			{
				#print "$hugo_symbol $uniprot_id kept $startend for evaluation\n";
				
				my $this_start = "UNDEFINED";
				my $this_end = "UNDEFINED";
				if ($startend =~ /^(\d+)_(\d+)$/)
				{
					($this_start, $this_end) = ($1, $2);
				}
				else
				{
					die "die: cannot parse starting and ending sequence coordinates\n";
				}
				#add one to the domain length to make sure we get full substring
				my $domain_length = $this_end - $this_start + 1;
				#subtract one from start position to go from 1-based domain position to 0-based substring
				my $subsequence = substr($sequence,$this_start-1,$domain_length);
				#print "$uniprot_id $startend $subsequence\n";
				
				$sortable_domain_sequences_hashRef->{$hugo_symbol}{$this_start}{$startend} = $subsequence;
			}
			#do this only for one uniprot id that is cross referenced to hgnc
			last;
		}
	}
}
###################################################################################################################



###################################################################################################################

###
# sub binarize
#
# parameters:
# database directory name
# HASH REFERENCE to
# tumor_ids
# mutations
# uniprot_annotation
# type
# sortable_domain_sequences
# dna_bin
# dna_binding_domain
# nsfs
# binarization

sub binarize
{

	# subroutine parameters
	my $tumor_ids_hashRef = shift @_;
	my $mutations_hashRef = shift @_;
	my $uniprot_annotation_hashRef = shift @_;
	my $type_hashRef = shift @_;
	my $sortable_domain_sequences_hashRef = shift @_;
	my $dna_bin_hashRef = shift @_;
	my $dna_binding_domain_hashRef = shift @_;
	my $nsfs_hashRef = shift @_;
	my $binarization_hashRef = shift @_;
	

	foreach my $sample (sort keys %$tumor_ids_hashRef)
	{
		foreach my $hugo_symbol (sort keys %$mutations_hashRef)
		{
			foreach my $position (sort {$a <=> $b} keys %{$mutations_hashRef->{$hugo_symbol}{$sample}})
			{
				my $mut_type = $type_hashRef->{$hugo_symbol}{$sample}{$position};
				
				foreach my $domain_start (sort {$a <=> $b} keys %{$sortable_domain_sequences_hashRef->{$hugo_symbol}})
				{
					foreach my $startend (sort keys %{$sortable_domain_sequences_hashRef->{$hugo_symbol}{$domain_start}})
					{
						#print "$startend from $hugo_symbol $domain_start\n";
						
						my $this_start = "UNDEFINED";
						my $this_end = "UNDEFINED";
						if ($startend =~ /^(\d+)_(\d+)$/)
						{
							($this_start, $this_end) = ($1, $2);
						}
						my $statement = "not_within";

						$statement = "within" if (($position >= $this_start) && ($position <= $this_end));
						#print "$sample $hugo_symbol $position $statement $this_start $this_end\n";
						#print "$sample $hugo_symbol dna_binding\n" if (defined($dna_binding_domain{$hugo_symbol}{$startend}));
						
						$dna_bin_hashRef->{$sample}{$hugo_symbol} = 1  if (defined($dna_binding_domain_hashRef->{$hugo_symbol}{$startend}) && ($position >= $this_start) && ($position <= $this_end));
						
						if (defined $mut_type) {
							#print "mut_type is $mut_type\n";
							$nsfs_hashRef->{$sample}{$hugo_symbol}{$domain_start}{$startend} = 1  if ((($mut_type eq "*") || ($mut_type eq "fs") || ($mut_type eq "X")) && ($position <= $this_end));
						}
						$binarization_hashRef->{$sample}{$hugo_symbol}{$domain_start}{$startend} = 1 if (($position >= $this_start) && ($position <= $this_end));
					}
				}
			}
		}
	}
}
###################################################################################################################



###################################################################################################################

###
# sub print_matrix
#
# parameters:
#
# HASH REFERENCE to
# tumor_ids
# mutations
# sortable_domain_sequences
# nsfs
# nonsilence
# dna_bin
# missense
# mnf
# mni
# code_potential
# binarization
#

sub print_matrix
{
	# subroutine parameters
	my $tumor_ids_hashRef = shift @_;
	my $mutations_hashRef = shift @_;
	my $sortable_domain_sequences_hashRef = shift @_;
	my $nsfs_hashRef = shift @_;
	my $nonsilence_hashRef = shift @_;
	my $dna_bin_hashRef = shift @_;
	my $missense_hashRef = shift @_;
	my $mnf_hashRef = shift @_;
	my $mni_hashRef = shift @_;
	my $code_potential_hashRef = shift @_;
	my $binarization_hashRef = shift @_;


	my $counter = 0;
	my $head = "";

	foreach my $sample (sort keys %$tumor_ids_hashRef)
	{
		my $vector = "$sample";

		foreach my $hugo_symbol (sort keys %$sortable_domain_sequences_hashRef)
		{
			my $head .= "\t$hugo_symbol\_y_n";

			my $num = keys %{$mutations_hashRef->{$hugo_symbol}{$sample}};
			if ($num > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			$head .= "\t$hugo_symbol\_nonsilent";

			if (exists $nonsilence_hashRef->{$hugo_symbol}{$sample} && $nonsilence_hashRef->{$hugo_symbol}{$sample} > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			$head .= "\t$hugo_symbol\_dna_bin";

			if (exists $dna_bin_hashRef->{$sample}{$hugo_symbol} && $dna_bin_hashRef->{$sample}{$hugo_symbol} > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			###############
			$head .= "\t$hugo_symbol\_missense";

			if (exists $missense_hashRef->{$hugo_symbol}{$sample} && $missense_hashRef->{$hugo_symbol}{$sample} > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			$head .= "\t$hugo_symbol\_mnf";

			if (exists $mnf_hashRef->{$hugo_symbol}{$sample} && $mnf_hashRef->{$hugo_symbol}{$sample} > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			$head .= "\t$hugo_symbol\_mni";

			if (exists $mni_hashRef->{$hugo_symbol}{$sample} && $mni_hashRef->{$hugo_symbol}{$sample} > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			
			$head .= "\t$hugo_symbol\_code_potential";

			if ($num > 0)
			{
				$vector .= "\t1";
			}
			else
			{
				$vector .= "\t0";
			}
			###############
			
			foreach my $domain_start (sort {$a <=> $b} keys %{$sortable_domain_sequences_hashRef->{$hugo_symbol}})
			{
				foreach my $startend (sort keys %{$sortable_domain_sequences_hashRef->{$hugo_symbol}{$domain_start}})
				{
					$head .= "\t$hugo_symbol\_dom_$startend\_ns_or_fs";
					my $binary = 0;

					if (exists $nsfs_hashRef->{$sample}{$hugo_symbol}{$domain_start}{$startend}  && $nsfs_hashRef->{$sample}{$hugo_symbol}{$domain_start}{$startend} > 0)
					{
						#$binary = 1 if ($nsfs_hashRef->{$sample}{$hugo_symbol}{$domain_start}{$startend} > 0);
						$binary = 1;
					}
					$vector .= "\t$binary";
					
					
					$head .= "\t$hugo_symbol\_dom_$startend";
					$binary = 0;

					if (exists $binarization_hashRef->{$sample}{$hugo_symbol}{$domain_start}{$startend} && $binarization_hashRef->{$sample}{$hugo_symbol}{$domain_start}{$startend} > 0)
					{
						# $binary = 1 if ($binarization_hashRef->{$sample}{$hugo_symbol}{$domain_start}{$startend} > 0);
						$binary = 1;
					}
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

