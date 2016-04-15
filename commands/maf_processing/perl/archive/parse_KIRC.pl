#!/usr/bin/perl
use strict;
use warnings;

#this script looks at the KIRC file.
#examine the number of exonic and non-exonic mutations by sample ID

#sample ID is tumor_sample_barcode
#to tell if exonic or non-exonic, grab the last field from line
#non-exonic matches variant_type

#TODO: configurable path
my $maf_uniprot="/titan/cancerregulome9/workspaces/users/liype/maf_protein/output/run2_KIRC/BI_and_BCM_1.4.aggregated.tcga.maf.ncm.with_uniprot"; # TODO:FILE_LAYOUT:EXPLICIT

open (MAF_UNIPROT, $maf_uniprot) or die "Error: cannot read from MAF.NCM.UNIPROT file $maf_uniprot: $!\n";
my %sample_list;
my %sample_exonic;
my %sample_nonexonic;
my $count=0;
while (<MAF_UNIPROT>) {

    s/[\r\n]+$//;
    chomp($_);

    #skip first header line
    if($count==0) {
	$count++;
	next;
    }
    
    my @field = split (/\t/, $_);
    
    #sample id is column 16
    my $sample = $field[15];
    chomp ($sample);
    $sample_list{$sample}++;

    #grab the annotation - last field in line
    my $one_field=pop(@field); 
    chomp($one_field);
    #print "This is field:  $one_field\n";

    if($one_field =~ m/^variant_type/) {
	$sample_nonexonic{$sample}++;
    }else {
	$sample_exonic{$sample}++;
    }

}

close MAF_UNIPROT;

my $total1 = scalar (keys %sample_nonexonic);
my $total2 = scalar (keys %sample_exonic);
print "You have $total1 nonexonic samples and $total2 exonic samples\n";

my $output = "kirc_sample_output";

(open OUTPUT, ">>$output") or die "cannot open file - $output\n";

print OUTPUT "Tumor Sample Barcode\tNumber of Exonic\tNumber of Non-Exonic\n";

my $total_sample=0;
my $total_exonic=0;
my $total_nonexonic=0;

foreach my $id (sort keys %sample_list) {
    print OUTPUT "$id\t";
    $total_sample++;

    if ($sample_exonic{$id}) {
	print OUTPUT "$sample_exonic{$id}\t";
	$total_exonic+=$sample_exonic{$id};
    }else {
	print OUTPUT "0\t";
    }
    if ($sample_nonexonic{$id}) {
	print OUTPUT "$sample_nonexonic{$id}\n";
	$total_nonexonic+=$sample_nonexonic{$id};
    }else {
	print OUTPUT "0\n";
    }    
}
print OUTPUT "$total_sample\t$total_exonic\t$total_nonexonic\n";
close OUTPUT;



