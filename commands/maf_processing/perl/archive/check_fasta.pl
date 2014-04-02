#!/usr/bin/perl
use warnings;
use strict;

open (FASTA, "/users/liype/maf/reference/HumanDB/hg18_knownGeneMrna.fa") or die "Error: cannot read from fastafile: $!\n";

my (%mrnaseq);
my ($curname, $curseq);
while (<FASTA>) {
	s/[\r\n]+$//;
	if (m/^>([\w\.]+)/) {  #NEED TO CHECK THIS 
		if ($curseq) {
			$mrnaseq{$curname} = $curseq;
		}
		$curname = $1;
		$curseq = '';
	} else {
		$curseq .= $_;
	}
	$curseq and $mrnaseq{$curname} = $curseq;	#process the last sequence
}
