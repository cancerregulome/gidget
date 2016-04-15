#!/usr/bin/perl
use warnings;
use strict;

#This script checks ANNOVAR amino acid change annotation against the default isoform amino acid sequence.  
#The wildtype amino acid in ANNOVAR should match the amino acid in the default isoform.  If not, raise a flag.
#TODO: configurable path
open(FILE1, "/titan/cancerregulome9/workspaces/users/liype/maf_protein/output/run6_BRCA/genome.wustl.edu_BRCA.IlluminaGA_DNASeq.Level_2.3.2.0.somatic.maf.ncm.with_uniprot") or die "Error:  cannot read from file\n"; # TODO:FILE_LAYOUT:EXPLICIT
my %annovar_results;
my %uniprot;
my $count=1;

while (my $line = <FILE1>) {
    
    chomp($line);

    my @field = split (/\t/, $line);
    my $line_gene=$count.$field[0];
    $count++;

    foreach my $one_field (@field) {   

	#grab the UNIPROT ID 
	if($one_field =~ m/^(\D\d[\d\D][\d\D][\d\D]\d)$/) {
	    my $uniprotid = $1;
	    #print "$uniprotid\n";
	    chomp($uniprotid);
	    $uniprot{$line_gene}=$uniprotid;
	}

	#match the ANNOVAR annotation
	#this is a very weak regex
	chomp($one_field);

	if($one_field =~ m/\,$/) {
	    
	    my $annovar=$one_field;

	    if ($annovar =~/NO UNIPROT MATCH1\,$/ || $annovar=~/NO UNIPROT MATCH2\,$/ || $annovar =~/NO ISOFORM MATCH\,$/ || $annovar =~/NO DEFAULT ISOFORM\,$/) {
		$annovar_results{$line_gene}="NO MATCH";
		last;
	    }
  	    
	    #here is an example of what has to be parsed
	    #DIP2C:uc001ifp.1:exon19:c.2209_2210insTG:p.A737fs,
	    #we just want the protein field

	    my @annovar_fields=split(":", $annovar);
	    foreach my $one_annovar_field (@annovar_fields) {
		if($one_annovar_field =~ m/^p\.(\S+)\,$/) {
		    #print"$one_field\t$1\n";
		    $annovar_results{$line_gene}=$1;
		    last;
		}
	    }
	    last;
	}
 
    }
}
my $total1 = scalar (keys %uniprot);
my $total2 = scalar (keys %annovar_results);
print "You have $total1 Uniprot IDs and $total2 annovar results.\n";

close FILE1;

#TODO: configurable path
#change file handles to use env variables
open(FILE2, "/titan/cancerregulome9/workspaces/users/liype/maf_protein/maf/reference/isoform1.sprot") or die "Error:  cannot read from file\n"; # TODO:FILE_LAYOUT:EXPLICIT
#open(FILE2, "test_isoform1") or die "Error:  cannot read from file\n";
my %isoform_results;
$count=1;

my $uniprot_id;
my $sequence;

while (my $line = <FILE2>) {
    
    chomp($line);

    #get uniprot ID
    if ($line =~ /^\>sp\|(\S+)/) {
	$uniprot_id=$1;
	$sequence="";
    }else {
	$sequence.=$line;
	$isoform_results{$uniprot_id}=$sequence;
    }
}



foreach my $line (sort keys %annovar_results) {
    if($annovar_results{$line} && $uniprot{$line}) {
	if($annovar_results{$line} =~ m/NO MATCH/) {
	    print "$line\tANNOVAR - NO UNIPROT MATCH\n";
	    next;
	}
	#print "$uniprot{$line}\n";

	if ($isoform_results{$uniprot{$line}}) {
	    
	    #get wildtype aa information
	    my $aa_sequence=$isoform_results{$uniprot{$line}};
	    my $annovar=$annovar_results{$line};
	    $annovar =~ /^(\D)/;
	    my $annovar_aa=$1;

	    if($annovar =~/^\D(\d+)(\D)+$/) {
		my $annovar_position=$1;
		#print "$annovar_aa\t$annovar_position\n";

		#check aa and position against isoform aa
		my $result=check_isoform_aa($annovar_aa, $annovar_position, $aa_sequence);

		if ($result==1) {
		    print "$line\tIsoform AA MATCH\n";
		}elsif ($result==0) {
		    print "$line\tIsoform AA NO MATCH\n";
		}elsif ($result==-1) {
		    print "$line\tAA position incorrect\n";
		}else {
		    print "$line\tWHY\n";
		}
	    }else {
		print "$line\tNo amino acid position\n";
	    }

	}else {
	    print"$line\tNo Protein Sequence\n";
	}
    }else {
	print "$line\tNo Assigned Uniprot ID\n";

    }
}

sub check_isoform_aa {
    my ($aa, $position, $isoform_sequence)=@_;
    my $result;
    my $mod_position=$position-1;
    
    if (length($isoform_sequence) < $mod_position) {
	$result=-1;
    }else {
	my $wildtype_aa=substr($isoform_sequence, $mod_position, 1);
	if($wildtype_aa && ($aa eq $wildtype_aa)){
	    $result=1;
	}else {
	    $result=0;
	}
    } 
     return $result;
}

	#if($one_field =~ m/\:p\.(.),$/) {
 # if ($annovar =~/NO UNIPROT MATCH1,$/ || $annovar=~/NO UNIPROT MATCH2,$/) {
#	$annovar_results{$line_gene}="NO MATCH";
#    }


#foreach my $check (keys %isoform_results) {
#    print "$check\t$isoform_results{$check}\n";
#}
