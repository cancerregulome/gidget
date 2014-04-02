#!/usr/bin/perl
use warnings;
use strict;

my $maf_file="BI_and_BCM_1.4.aggregated.tcga.maf";
my $maf_output="test";

open (MAF, $maf_file) or die "Error: cannot read from MAF $maf_file: $!\n";
open (MAF_OUTPUT, ">> $maf_output") or die "Error: cannot open MAF output $maf_output: $!\n";

while(my $line = <MAF>) {    
    #$line = s/[\r\n]+$//;
    $line=~ s/\r\n$/\n/;

    print MAF_OUTPUT "$line";
}


