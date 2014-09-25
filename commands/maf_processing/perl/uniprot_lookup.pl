#!/usr/bin/perl
use warnings;
use strict;
use Pod::Usage;
use Getopt::Long;

#steps
#read in gene to uniprot mapping file
#read in transcript to uniprot mapping file
#read in Uniprot ID history file
#read in MAF file to retrieve default Uniprot ID
#read in isoform1 sequence file
#read in annovar output file and process records

#usage
# $scriptFolder/perl/uniprot_lookup.pl $annovarExonicOutput $gene2uniprot $knownGene $uniprot_sec $maf_uniprot $isoprot_seq> $annovarExonicOutput".isoform_filter"

@ARGV or pod2usage (-verbose=>0, -exitval=>1, -output=>\*STDOUT);
@ARGV == 6 or pod2usage ("Syntax error - you are missing an argument");

my ($annovar_output_file, $gene2uniprot, $knowngene2protein, $uniprot_sec, $maf_uniprot, $isoprot_seq) = @ARGV;

open (ANNOVAR_OUTPUT, $annovar_output_file) or die "Error: cannot read from ANNOVAR output file $annovar_output_file: $!\n";
open (HGNC2UNIPROT, $gene2uniprot) or die "Error: cannot read from file $gene2uniprot: $!\n";
open (GENE2PROTEIN, $knowngene2protein) or die "Error: cannot read from file $knowngene2protein: $!\n";
open (UNIPROT_SEC, $uniprot_sec) or die "Error: cannot read from Uniprot Secondary file $uniprot_sec: $!\n";
open (MAF_UNIPROT, $maf_uniprot) or die "Error: cannot read from MAF.NCM.UNIPROT file $maf_uniprot: $!\n";
open (ISOPROT, $isoprot_seq) or die "Error: cannot read from ISOFORM.sprot file $isoprot_seq: $!\n";

#read mapping between genes and uniprot IDs
my %hgnc2uniprot;
my %alias_hgnc2uniprot;
my %old_hgnc2uniprot;

#hashes for correspondence between gene and alias; between gene and old; between alias and old
my %gene_alias;
my %gene_old;
my %gene_alias_old;

while(my $line = <HGNC2UNIPROT>) {    
    chomp($line);
    my ($gene_id, $gene_symbol, $alias, $old, $uniprot) = split (/\t/, $line);
    chomp($gene_symbol);

#first get all primary gene to uniprot ID mapping    
#if gene symbol is withdrawn - it is skipped 
    if($gene_symbol && $uniprot) {
	$hgnc2uniprot{$gene_symbol}=$uniprot;
    }

#add more gene mapping - first aliases and then old genes

    #add aliases to mapping
      if($gene_symbol && $alias && $uniprot) {            

	  $gene_alias{$gene_symbol}=$alias;

  	if($alias =~ /;/) {
  	    my @aliases=split(";", $alias);
  	    foreach my $one_alias (@aliases) {
  		if (!$hgnc2uniprot{$one_alias}) {
  		    $alias_hgnc2uniprot{$one_alias}=$uniprot;
  		}else {
  		    next;
  		}
  	    }
  	}else {
  	    if (!$hgnc2uniprot{$alias}) {
  		$alias_hgnc2uniprot{$alias}=$uniprot;
  	    }
  	}	
      }

    #add old genes to mapping
     if($gene_symbol && $old && $uniprot) {
	 
	 $gene_old{$gene_symbol}=$old;
	 
 	if($old =~ /;/) {
 	    my @old_symbols=split(";", $old);
 	    foreach my $one_old_symbol (@old_symbols) {
 		if (!$hgnc2uniprot{$one_old_symbol}) {
 		    $old_hgnc2uniprot{$one_old_symbol}=$uniprot;
 		}else {
 		    next;
 		}
 	    }
 	}else {
 	    if (!$hgnc2uniprot{$old}){
 		$old_hgnc2uniprot{$old}=$uniprot;
 	    }
 	}
     }

    if($alias && $old) {
	$gene_old{$gene_symbol}=$old;
	my @alias_symbols;

	if($alias =~ /;/) {
 	    @alias_symbols=split(";", $alias);
	}else {
	    @alias_symbols=$alias;
 	}

	foreach my $one_alias(@alias_symbols) {
	    $gene_alias_old{$one_alias}=$old;
	}
    }
}

close HGNC2UNIPROT;

my $total1 = scalar (keys %hgnc2uniprot);
#print "You have $total1 primary gene to uniprot mappings\n";
my $total2 = scalar (keys %alias_hgnc2uniprot);
#print "You have $total2 secondary gene to uniprot mappings\n";


#read mapping between transcripts and uniprot IDs
#this includes hg18 and hg19 so you can have 1 transcript going to 2 different Uniprot IDs 
my %gene2uniprot;

while(my $line = <GENE2PROTEIN>) {
    chomp($line);

    my ($transcript, $uniprot) = split (/\t/, $line);

    #skip uniprot with dash which means this is not default isoform
    if($uniprot =~ /-/) {
	next;
    }
    if ($gene2uniprot{$transcript}) {
	$gene2uniprot{$transcript}=$gene2uniprot{$transcript}.":".$uniprot;
    }else {
	$gene2uniprot{$transcript}=$uniprot;
    }
}

my $total3 = scalar (keys %gene2uniprot);
#print "You have $total3 transcript to uniprot mappings\n";

close GENE2PROTEIN;

#read mapping between uniprot primary and uniprot secondary accessions
my %uniprotsecacc;

#storing primary to secondary uniprot mapping
while(my $line = <UNIPROT_SEC>) {
    chomp($line);

    my ($secondary, $primary) = split (/\s+/, $line);
    $primary =~s/^\s+//;
    $primary=~s/\s+$//;
    $secondary =~s/^\s+//;
    $secondary=~s/\s+$//;
    push(@{$uniprotsecacc{$primary}},$secondary);
}

my $total4 = scalar (keys %uniprotsecacc);
#print "You have $total4 secondary to primary uniprot mappings\n";

close UNIPROT_SEC;

#read in gene symbols form MAF file
#read in uniprot ID from MAF_UNIPROT file
my %maflist_gene;
my %uniprot;
my $count=0;

while (<MAF_UNIPROT>) {
    s/[\r\n]+$//;

    #skip first header line
    if($count==0) {
	$count++;
	next;
    }

    chomp($_);
    my @field = split (/\t/, $_);
    my $key="line"."$count";
    

    #gene_symbol is first field
    my $gene_symbol = $field[0];
    chomp ($gene_symbol);
    $maflist_gene{$key}=$gene_symbol;
    #print "This is your symbol:  $gene_symbol\n";

    #grab the UNIPROT ID - last field in line
    #can have more than 1 uniprot ID and can have dashes
    #one uniprot ID
    my $one_field=pop(@field); 
    chomp($one_field);
    #print "This is field:  $one_field\n";
    if($one_field =~ m/^(\D\d[\d\D][\d\D][\d\D]\d)$/) {
	my $uniprotid = $1;
	chomp($uniprotid);
	$uniprot{$key}=$uniprotid;
    }

    #has a dash
    if($one_field =~ m/^\-\;\D\d[\d\D][\d\D][\d\D]\d$/) {
	my @all=split(";", $one_field);
	my $uniprotid = $all[1];
	chomp($uniprotid);
	$uniprot{$key}=$uniprotid;
    }
    #more than one Uniprot ID
    if($one_field =~ m/^\D\d[\d\D][\d\D][\d\D]\d\;/) {
	my $uniprotid = $one_field;
	chomp($uniprotid);
	$uniprot{$key}=$uniprotid;
    }	
    $count++;
}

my $total5 = scalar (keys %uniprot);
#print "You have $total5 Uniprot IDs from MAF file\n";

close MAF_UNIPROT;

#read in isoform1 file
my %isoform_results;
my $uniprot_id;
my $sequence;

while (my $line = <ISOPROT>) {
    chomp($line);

    #get uniprot ID
    if ($line =~ /^\>sp\|(\D\d[\d\D][\d\D][\d\D]\d)/) {
	$uniprot_id=$1;
	$sequence="";
    }else {
	$sequence.=$line;
	$isoform_results{$uniprot_id}=$sequence;
    }
}

close ISOPROT;
my $total6 = scalar (keys %isoform_results);
#print "You have $total6 isoform 1 sequences\n";

my $bad_line=0;

#read ANNOVAR OUTPUT file
while (<ANNOVAR_OUTPUT>) {
    s/[\r\n]+$//;
    m/^line\d+/ or die "Error: invalid record found in exonic_variant_function file $annovar_output_file (line number expected): <$_>\n";
    my @field = split (/\t/, $_);
    if($field[1] =~ m/^unknown/) {
	$field[2].=",NO UNIPROT MATCH";
	print_fields(@field);
	$bad_line++;
	next;
    }

    if($field[2] =~ m/^\w+:(\w+):wholegene/) {
	$field[2].=",NO UNIPROT MATCH";
	print_fields(@field);
	$bad_line++;
	next;
    }

    #here is an example of what has to be parsed
    #DIP2C:uc001ifp.1:exon19:c.2209_2210insTG:p.A737fs,DIP2C:uc009xhi.1:exon2:c.367_368insTG:p.A123fs,
	
    $field[2] =~ m/^(\S+)/ or die "Error: invalid record found in exonic_variant_function file (exonic format error): <$_>\n";

    my $required_info=$1;
    my @all_transcripts=split(",", $required_info);
    
    #line number is $field[0] in ANNOVAR output file
    my $maf_line_number=$field[0];

    #first check if there is a UNIPROT ID present for this line
    my $default_isoform;

    if ($uniprot{$maf_line_number}) {
	$default_isoform=$uniprot{$maf_line_number};
	#print "This is your default isoform:$maf_line_number\t$default_isoform\n";
    }

    #No Default Isoform 
    if (!$default_isoform) {	    
	$field[2].="NO UNIPROT ID";
	print_fields(@field);
	$bad_line++;
	next; #no uniprot ID for this gene in the MAF file so go to the next line in file
    }

    #second check if gene symbol corresponds to a Uniprot ID
    #gene symbol comes from original MAF
    my $no_uniprot_id_warning=1;
    my $gene_symbol=$maflist_gene{$maf_line_number};
    
    my @primary_keep_this_uniprot;
    my @alias_keep_this_uniprot;
    my @old_keep_this_uniprot;
    my @keep_this_uniprot;
    my @temp;
   
    #add primary information
    if($hgnc2uniprot{$gene_symbol}) {
	$no_uniprot_id_warning=0;	    
	my %new_uniprot=process_uniprot_id_field($hgnc2uniprot{$gene_symbol});
	if($new_uniprot{"primary"}) {
	    push(@primary_keep_this_uniprot, @{$new_uniprot{"primary"}});
	}
	if($new_uniprot{"old"}) {
	    push(@temp, @{$new_uniprot{"old"}});
	}
    #add alias information
    }elsif($alias_hgnc2uniprot{$gene_symbol}) {
	$no_uniprot_id_warning=0;
	my %new_uniprot=process_uniprot_id_field($alias_hgnc2uniprot{$gene_symbol});    
	if($new_uniprot{"primary"}) {
	    push(@alias_keep_this_uniprot, @{$new_uniprot{"primary"}});
	}
	if($new_uniprot{"old"}) {
	    push(@temp, @{$new_uniprot{"old"}});
	}
    #add old gene information 
    }elsif($old_hgnc2uniprot{$gene_symbol}) {
	$no_uniprot_id_warning=0;
	my %new_uniprot=process_uniprot_id_field($old_hgnc2uniprot{$gene_symbol});    
	if($new_uniprot{"primary"}) {
	    push(@old_keep_this_uniprot, @{$new_uniprot{"primary"}});
	}
	if($new_uniprot{"old"}) {
	    push(@temp, @{$new_uniprot{"old"}});
	}
    }

   
    push(@keep_this_uniprot, @primary_keep_this_uniprot);
    push(@keep_this_uniprot, @alias_keep_this_uniprot);
    push(@keep_this_uniprot, @old_keep_this_uniprot);
    push(@keep_this_uniprot, @temp);

    if ($no_uniprot_id_warning){
	$field[2].="NO UNIPROT MATCH1";
	print_fields(@field);
	$bad_line++;
	next; #no uniprot ID for this gene in all the mapping sources so go to the next line in file
    }

    #third: map transcript to uniprot IDs
    my %primary_keep_this_transcript;
    my %alias_keep_this_transcript;
    my %old_keep_this_transcript;
    my %keep_this_transcript;
    my $no_uniprot_transcript_warning=1;


    foreach my $one_transcript(@all_transcripts) {
	my @transcript_info=split(":", $one_transcript);
	my $transcript_gene_symbol=$transcript_info[0];
	my $transcript=$transcript_info[1];

	#check MAF gene symbol
	#if no match - skip to next transcript
	
	my $keep=check_MAF_gene($gene_symbol, $transcript_gene_symbol);

	if ($keep == 0) {
	    next;
	}

	if($gene2uniprot{$transcript}) {
	    my @uniprot=split(":", $gene2uniprot{$transcript});

	    #first: check primary hgnc2uniprot
	    if($hgnc2uniprot{$gene_symbol}) {
		foreach my $one_uniprot_id (@uniprot) {
		    if ($hgnc2uniprot{$gene_symbol} =~/($one_uniprot_id)/) {
			$primary_keep_this_transcript{$transcript}++;
			$no_uniprot_transcript_warning=0;
		    }
		}
	    }
	
	    #second: check alias hgnc2uniprot    
	    if($alias_hgnc2uniprot{$gene_symbol}) {
		foreach my $one_uniprot_id (@uniprot) {
		    if ($alias_hgnc2uniprot{$gene_symbol} =~ /($one_uniprot_id)/) {
			$alias_keep_this_transcript{$transcript}++;
			$no_uniprot_transcript_warning=0;
		    }
		}
	    }

	    #third: check old hgnc2uniprot    
	    if($old_hgnc2uniprot{$gene_symbol}) {
		foreach my $one_uniprot_id (@uniprot) {
		    if ($old_hgnc2uniprot{$gene_symbol} =~ /($one_uniprot_id)/) {
			$old_keep_this_transcript{$transcript}++;
			$no_uniprot_transcript_warning=0;
		    }
		}
	    }

	    #fourth:  check retired uniprot IDs by checking the complete list
	    foreach my $one_uniprot_id (@uniprot) {
		if (grep {$_ eq $one_uniprot_id} @keep_this_uniprot) {
		    $keep_this_transcript{$transcript}++;
		    $no_uniprot_transcript_warning=0;
		}
	    }
	}
    }

    if ($no_uniprot_transcript_warning){
	$field[2].="NO UNIPROT MATCH2";
	print_fields(@field);
	$bad_line++;
	next; #no mapping between transcript and defined uniprot for this gene so go to the next line in file
    }

    #perform isoform filtering here
    
    if ($default_isoform){
	if (%primary_keep_this_transcript) {
	    my %primary_result=isoform_filter(\@all_transcripts, \%primary_keep_this_transcript, $default_isoform);

	    if($primary_result{"match"}==1 && $primary_result{"isoform"}) {
	    
		#at this point you should have 1 transcript to keep
		foreach my $one_transcript(@all_transcripts) {
		    my @transcript_info=split(":", $one_transcript);
		    my $transcript=$transcript_info[1];
		    if ($primary_result{"isoform"} && $transcript =~ m/($primary_result{"isoform"})/) {
			$field[2]=$one_transcript;
		    }
		}
		print_fields(@field);
		next;
	    }
	}

	if (%alias_keep_this_transcript) {
	    my %alias_result=isoform_filter(\@all_transcripts, \%alias_keep_this_transcript, $default_isoform);
	
	    if($alias_result{"match"}==1 && $alias_result{"isoform"}) {
	    
		#at this point you should have 1 transcript to keep
		foreach my $one_transcript(@all_transcripts) {
		    my @transcript_info=split(":", $one_transcript);
		    my $transcript=$transcript_info[1];
		    if ($alias_result{"isoform"} && $transcript =~ m/($alias_result{"isoform"})/) {
			$field[2]=$one_transcript;
		    }
		}
		print_fields(@field);
		next;
	    }
	}

	if (%old_keep_this_transcript) {
	    my %old_result=isoform_filter(\@all_transcripts, \%old_keep_this_transcript, $default_isoform);
	
	    if($old_result{"match"}==1 && $old_result{"isoform"}) {
	    
		#at this point you should have 1 transcript to keep
		foreach my $one_transcript(@all_transcripts) {
		    my @transcript_info=split(":", $one_transcript);
		    my $transcript=$transcript_info[1];
		    if ($old_result{"isoform"} && $transcript =~ m/($old_result{"isoform"})/) {
			$field[2]=$one_transcript;
		    }
		}
		print_fields(@field);
		next;
		
	    }
	}

	if (%keep_this_transcript) {
	    #first match will win here
	    my %result=isoform_filter(\@all_transcripts, \%keep_this_transcript, $default_isoform);
	
	    if($result{"match"}==1 && $result{"isoform"}) {
	    
		#at this point you should have 1 transcript to keep
		foreach my $one_transcript(@all_transcripts) {
		    my @transcript_info=split(":", $one_transcript);
		    my $transcript=$transcript_info[1];
		    if ($result{"isoform"} && $transcript =~ m/($result{"isoform"})/) {
			$field[2]=$one_transcript;
		    }
		}
		print_fields(@field);
		next;
		
	    #if you have reached this point, that means there was no isoform match or there was a deletion
	    }else {

		my @filtered_transcript_list=generate_filtered_transcript_list(\%keep_this_transcript, \@all_transcripts);

		#NEW ADDITION:7/2/14
		#need to flag true no isoform matches and not deletions
		if($result{"match"}==-1 && $result{"isoform"}) {
		    print_fields(@field);
		}else {    
		    push(@filtered_transcript_list, "NO ISOFORM MATCH");
		    $field[2]=join(",", @filtered_transcript_list);
		    print_fields(@field);
		    $bad_line++;
		
		}
	    }
	}
    }
}

close ANNOVAR_OUTPUT;

#print"There are $bad_line lines which were not processed.\n";
#print "COMPLETE\n";

#print a line to file
sub print_fields {
    my @field=@_;

    foreach my $field (@field) {
	print "$field\t";
    }
    print"\n";

}

#perform isoform check and select transcript which matches isoform protein sequence
sub isoform_filter {
    my($all_transcripts,$keep_this_transcript, $default_isoform)=@_;

    my @all_transcripts=@$all_transcripts;
    my %keep_this_transcript=%$keep_this_transcript;

    #there are special cases where there is more than 1 default isoform;
    my @default_isoform;
    
    if ($default_isoform =~ /;/) {
	@default_isoform=split(";", $default_isoform);
    }else {
	@default_isoform=$default_isoform;
    }
	
    #print "All transcripts:@all_transcripts\n";
    my $keep_list=join(",", (keys %keep_this_transcript));
    #print "Keep transcript:  $keep_list\n";
    #print "Default isoform:  $default_isoform\n";

    #first set isoform match to all good transcripts; overwrite this if filter works
    my $isoform_match=join(",", (keys %keep_this_transcript));
    my %overall_result;

    foreach my $one_transcript(@all_transcripts) {

	#parse the transcript information
	my @fields=split(":", $one_transcript);
	my $transcript=$fields[1];

	#double-check against keep_this_transcript
	#if it doesn't match, don't test it
	my $keep_flag=0;
	foreach my $keep (keys %keep_this_transcript) {
	    if ($transcript eq $keep) {
		$keep_flag=1;
	    }
	}

	if($keep_flag == 0) {
	    next;
	}

	my $annovar_protein;
	
	#get the protein amino acid information
	#need to parse this: p.A737fs

	foreach my $one_annovar_field (@fields) {
	    if($one_annovar_field =~ m/^p\.(\S+)$/) {
		$annovar_protein=$1;
		last;
	    }else {
		$annovar_protein="none";
	    }
	}
	
	#print "$annovar_protein\n";

	#get the amino acid
	$annovar_protein =~ /^(\D)/;
	my $annovar_aa=$1;

	#get the amino acid position
	my $annovar_position;
	if($annovar_protein =~/^\D(\d+)(\D)+$/) {
	   $annovar_position=$1;	

	   #NEW ADDITION:7/2/14
	   #check delins but set del as -1
        }elsif($annovar_protein=~/^\D(\d+)_/) {
	    $annovar_position=$1;
	    #print "DASH:$annovar_protein:amino acid position is $annovar_position\n";
	    

	}elsif($annovar_protein=~/^\d+_\d+del/) {
	    $overall_result{"match"}=-1;
	    #print "$annovar_protein: has a deletion\n";
	    $overall_result{"isoform"}=$isoform_match;
	    return %overall_result;
    
	}else {
	    #print "$annovar_protein:DID NOT PROCESS\n";
	}



	#then check wildtype amino acid against amino acid in default isoform	
	foreach my $isoform (@default_isoform) {

	    my $aa_sequence = $isoform_results{$isoform};

	    if($annovar_aa && $annovar_position && $aa_sequence) {
		my $result=check_isoform_aa($annovar_aa, $annovar_position, $aa_sequence);
		
		#print "Your check isoform result:  $result\n";
		if ($result==1) {
		    $isoform_match=$transcript;
		    #there is no need to check again
		    $overall_result{"match"}=1;
		    $overall_result{"isoform"}=$isoform_match;
		    return %overall_result;
		}		
	    }
		
	}
    }
	#print "After isoform filter: $isoform_match\n";
	$overall_result{"match"}=0;
	$overall_result{"isoform"}=$isoform_match;
	return %overall_result;
    }


#compare isoform aa sequence and ANNOVAR aa sequence
sub check_isoform_aa {
    my ($aa, $position, $isoform_sequence)=@_;
    my $result;
    my $mod_position=$position-1;

    #print "AA:$aa\tposition:$position\n";
    #print "$isoform_sequence\n";
    my $length=length($isoform_sequence);
    #print "Length of sequence:$length\n";
    #print "Modified position: $mod_position\n";

    if (length($isoform_sequence) < $mod_position) {
	$result=-1;
    }else {
	my $wildtype_aa=substr($isoform_sequence, $mod_position, 1);
	#print "This is the wildtype aa:  $wildtype_aa\n";
	if($wildtype_aa && ($aa eq $wildtype_aa)){
	    $result=1;
	}else {
	    $result=0;
	}
    } 
     return $result;
}

#filter transcript list
sub generate_filtered_transcript_list {

    my @final_list;
    my ($keep_this_transcript, $all_transcripts)=@_;
    my %keep_this_transcript=%$keep_this_transcript;
    my @all_transcripts=@$all_transcripts;

    foreach my $filtered (keys %keep_this_transcript) {

	foreach my $one_transcript(@all_transcripts) {
	    my @transcript_info=split(":", $one_transcript);
	    my $transcript=$transcript_info[1];
	    
	    if ($transcript =~ m/($filtered)/) {
		push(@final_list,$one_transcript);
	    }
	}
    }
    return @final_list;
}

#process Uniprot IDs assigned to a given gene symbol; add in old Uniprot IDs
sub process_uniprot_id_field {
    my ($uniprot_field) = @_;
    my @primary_ids_keep_uniprot;
    my @old_ids_keep_uniprot;
    my %results;

    #print "This is the starting uniprot field:  $uniprot_field\n";
    #check for dashes and multiple uniprot IDs
    if (!($uniprot_field =~ /\;/)) {
	push(@primary_ids_keep_uniprot, $uniprot_field);
		
	#print "@keep_uniprot\n";
	#if this is a newer Uniprot ID, then store old Uniprot IDs also
	my @old_uniprots=add_old_uniprot($uniprot_field);
	if (@old_uniprots) {
	    push(@old_ids_keep_uniprot, @old_uniprots);
	}
   } else {
       #dashes in Uniprot field
       if($uniprot_field =~ m/^\-\;\D\d[\d\D][\d\D][\d\D]\d$/) {
	   my @all=split(";", $uniprot_field);
	   my $uniprotid = $all[1];
	   chomp($uniprotid);
	   push(@primary_ids_keep_uniprot, $uniprotid);
	   my @old_uniprots=add_old_uniprot($uniprotid);
	   if (@old_uniprots) {
	       push(@old_ids_keep_uniprot, @old_uniprots);
	   }
       }

       #more than one Uniprot ID
       if($uniprot_field =~ m/^\D\d[\d\D][\d\D][\d\D]\d\;/) {
	   my @uniprotid = split(";", $uniprot_field);
	   foreach my $one_id (@uniprotid) {
	       chomp($one_id);
	       push(@primary_ids_keep_uniprot, $one_id);
	       my @old_uniprots=add_old_uniprot($one_id);
	       if (@old_uniprots) {
		   push(@old_ids_keep_uniprot, @old_uniprots);
	       }
	   }
       }
   }
    #print "These are your uniprot IDs:@primary_ids_keep_uniprot followed by @old_ids_keep_uniprot\n";

    $results{"primary"}=\@primary_ids_keep_uniprot;
    $results{"old"}=\@old_ids_keep_uniprot;
    return %results;
}

#adds old Uniprot IDs for a current Uniprot ID
sub add_old_uniprot {
    my ($uniprot_id) = @_;
    my @old_uniprot=[];
    if($uniprotsecacc{$uniprot_id}) {
	@old_uniprot =@{$uniprotsecacc{$uniprot_id}};
    } 
    #print "Old uniprots added:  @old_uniprot\n";
    return @old_uniprot;
}

#checks MAF gene symbol to see if it is valid
#if gene_symbol is a LOC, we'll assume it is related to MAF gene symbol.  May need to change this assumption?
#need to check MAF gene symbol against ANNOVAR gene symbol; 
#need to check MAF gene symbol alias against ANNOVAR gene symbol;
#need to check MAF gene symbol old against ANNOVAR gene symbol;
#need to check MAF gene symbol alias to old mapping against ANNOVAR gene symbol;

sub check_MAF_gene {
    
    my ($gene_symbol, $transcript_gene_symbol)=@_;

    my $keep=0;

    if ($transcript_gene_symbol =~/^LOC/) {
	$keep=1;
    }
    
    if($gene_symbol eq $transcript_gene_symbol) {
	$keep=1;
    }else {
	if ($gene_alias{$gene_symbol}){
	    if ($gene_alias{$gene_symbol} =~ /($transcript_gene_symbol)/) {
		$keep=1;
	    }
	}
	    
	if ($gene_old{$gene_symbol}){
	    if ($gene_old{$gene_symbol} =~ /($transcript_gene_symbol)/) {
		$keep=1;
	    }
	}

	#strange case 1
	if ($gene_alias_old{$gene_symbol}) {
	    if ($gene_alias_old{$gene_symbol} =~ /($transcript_gene_symbol)/) {
		$keep=1;
	    }
	}

	#strange case 2
	if ($gene_alias_old{$transcript_gene_symbol}) {
	    if ($gene_alias_old{$transcript_gene_symbol} =~ /($gene_symbol)/) {
		$keep=1;
	    }
	}

	#strange case 3
	if ($gene_alias{$transcript_gene_symbol}) {
	    if ($gene_alias{$transcript_gene_symbol} =~ /($gene_symbol)/) {
		$keep=1;
	    }
	}	
    }
    return $keep;
}


=head1 SYNOPSIS

 uniprot_lookup.pl [arguments] 

 Optional arguments:
        -h, --help                      print help message
        -m, --man                       print complete documentation
        -v, --verbose                   use verbose output

 Function: a script to annotate a MAF with protein information
 
 Example: uniprot_lookup.pl $annovarExonicOutput $gene2uniprot $knownGene $uniprot_sec $maf_uniprot $isoprot_seq > $annovarExonicOutput".isoform_filter

 Version: 

=head1 OPTIONS

=over 8

=item B<--help>

print a brief usage message and detailed explanation of options.

=item B<--man>

print the complete manual of the program.

=item B<--verbose>

use verbose output.

=back

=head1 DESCRIPTION



=cut

