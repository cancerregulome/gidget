#!/usr/bin/perl
use warnings;
use strict;
use Pod::Usage;
use Getopt::Long;

our $VERSION = 			'$Revision: 409 $';
our $LAST_CHANGED_DATE =	'$LastChangedDate: 2010-08-16 11:36:18 -0400 (Mon, 16 Aug 2010) $';

our ($verbose, $help, $man);

our ($evffile, $genefile, $fastafile);

our %codon1 = (TTT=>"F", TTC=>"F", TCT=>"S", TCC=>"S", TAT=>"Y", TAC=>"Y", TGT=>"C", TGC=>"C", TTA=>"L", TCA=>"S", TAA=>"*", TGA=>"*", TTG=>"L", TCG=>"S", TAG=>"*", TGG=>"W", CTT=>"L", CTC=>"L", CCT=>"P", CCC=>"P", CAT=>"H", CAC=>"H", CGT=>"R", CGC=>"R", CTA=>"L", CTG=>"L", CCA=>"P", CCG=>"P", CAA=>"Q", CAG=>"Q", CGA=>"R", CGG=>"R", ATT=>"I", ATC=>"I", ACT=>"T", ACC=>"T", AAT=>"N", AAC=>"N", AGT=>"S", AGC=>"S", ATA=>"I", ACA=>"T", AAA=>"K", AGA=>"R", ATG=>"M", ACG=>"T", AAG=>"K", AGG=>"R", GTT=>"V", GTC=>"V", GCT=>"A", GCC=>"A", GAT=>"D", GAC=>"D", GGT=>"G", GGC=>"G", GTA=>"V", GTG=>"V", GCA=>"A", GCG=>"A", GAA=>"E", GAG=>"E", GGA=>"G", GGG=>"G");


GetOptions('verbose|v'=>\$verbose, 'help|h'=>\$help, 'man|m'=>\$man, ) or pod2usage ();
	
$help and pod2usage (-verbose=>1, -exitval=>1, -output=>\*STDOUT);
$man and pod2usage (-verbose=>2, -exitval=>1, -output=>\*STDOUT);
@ARGV or pod2usage (-verbose=>0, -exitval=>1, -output=>\*STDOUT);
@ARGV == 3 or pod2usage ("Syntax error");

($evffile, $genefile, $fastafile) = @ARGV;

open (EVF, $evffile) or die "Error: cannot read from evffile $evffile: $!\n";
open (GENE, $genefile) or die "Error: cannot read from genefile $genefile: $!\n";
open (FASTA, $fastafile) or die "Error: cannot read from fastafile $fastafile: $!\n";

my (@queue, %need_trans);
while (<EVF>) {
	s/[\r\n]+$//;
	m/^line\d+/ or die "Error: invalid record found in exonic_variant_function file $evffile (line number expected): <$_>\n";
	my @field = split (/\t/, $_);

	$field[1] =~ m/^unknown/ and next;
	$field[2] =~ m/^.+:wholegene/ and next;	
	
	#$field[2] =~ m/^.+:([^\s]+):exon\d+:c.(\w+)/ or next; #die "Error: invalid record found in exonic_variant_function file (exonic format error): <$_>\n"; # xueling changed the regular expression

	# xueling debug
	#print "$field[2]\r\n";

	#use a split instead of regex
	#here is an example of what has to be parsed
	#filtering has already been done - so just take the first transcript
	#DIP2C:uc001ifp.1:exon19:c.2209_2210insTG:p.A737fs,
	#keep uc001ifp.1 and c2209_2210insTG - fields 1 and 3

	HERE my @all_transcripts=split("," $field[2]);
	     foreach my 
	my @transcript_info=split(":", $field[2]);
	my $transcript=$transcript_info[1];
	#get cchange
	$transcript_info[3] =~ m/^c.(.+)/;
	my $cchange=$1;
	
	#my ($transcript, $cchange) = ($1, $2);
	my ($start, $end, $obs);
	
	if ($cchange =~ m/^\w\d+\w$/) {
		next;
	} elsif ($cchange =~ m/^(\d+)_(\d+)delins(\w+)/) {
		($start, $end, $obs) = ($1, $2, $3);
	} elsif ($cchange =~ m/^(\d+)del\w+/) {
		($start, $end, $obs) = ($1, $1, '');
	} elsif ($cchange =~ m/^(\d+)_(\d+)del(\w*)/) {
		($start, $end, $obs) = ($1, $2, '');
	} elsif ($cchange =~ m/^(\d+)_(\d+)ins(\w+)/) {
		($start, $end, $obs) = ($1, $1, $3);		#if end is equal to start, this is an insertion
	} elsif ($cchange =~ m/^(\d+)_(\d+)([TCGA]+)/) {
                ($start, $end, $obs) = ($1, $2, $3);
        } else {
		die "Error: invalid coding change format: <$cchange> within <$_>\n";
		#next;
	}
	push @queue, [$field[0], $transcript, $start, $end, $obs, $cchange];
	$need_trans{$transcript}++;
}

my (%mrnastart);
while (<GENE>) {
	s/[\r\n]+$//;
	my @field = split (/\t/, $_);
	@field >= 11 or die "Error: invalid record found in gene file (>=11 fields expected): <$_>\n";
	$field[0] =~ m/^\d+$/ and shift @field;		#refGene and ensGene has bin as the first column

	my ($name, $strand, $txstart, $txend, $cdsstart, $cdsend, $exonstart, $exonend) = @field[0, 2, 3, 4, 5, 6, 8, 9];
	$need_trans{$name} or next;
	
	my $mrnastart;
	
	if ($strand eq '+') {
		$mrnastart = $cdsstart-$txstart;
	} elsif ($strand eq '-') {
		$mrnastart = $txend-$cdsend;
	}
	
	#next we need to make sure that there is no intron between transcription start and translation start (this is rare but it happens when cdsstart is not in the first exon)
	my @exonstart = split (/,/, $exonstart);
	my @exonend = split (/,/, $exonend);
	
	$txstart++;
	$cdsstart++;
	@exonstart = map {$_+1} @exonstart;
	
	if ($field[2] eq '+') {
		for my $i (0 .. @exonstart-1) {
			if ($exonend[$i] < $cdsstart) {
				$mrnastart -= ($exonstart[$i+1] - $exonend[$i] - 1);
			} else {
				last;
			}
		}
	} elsif ($field[2] eq '-') {
		for (my $i=@exonstart-1; $i>=0; $i--) {
			if ($exonstart[$i] > $cdsstart) {
				$mrnastart -= ($exonstart[$i]-$exonend[$i-1]-1);
			} else {
				last;
			}
		}
	}
	$mrnastart{$name} = $mrnastart;
}

my (%mrnaseq);
my ($curname, $curseq);

while (<FASTA>) {
	s/[\r\n]+$//;
	if (m/^>([^\s]+)/) { # xueling changed the regular expression
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

#process each element in the queue
for my $i (0 .. @queue-1) {
	my ($line, $transcript, $start, $end, $obs, $cchange) = @{$queue[$i]};
	print STDERR "NOTICE: Processing $line with $cchange\n";
	defined $mrnaseq{$transcript} or die "Error: cannot find mRNA sequence for $transcript in the fastafile $fastafile\n";
	defined $mrnastart{$transcript} or die "Error: cannot find annotation for $transcript in the genefile $genefile\n";
	
	my $dna = substr ($mrnaseq{$transcript}, $mrnastart{$transcript});
	my @dna = split (//, $dna);
	
	if ($start == $end and $obs) {		#this is an insertion
		splice (@dna, $start, 0, $obs);
	} else {
		splice (@dna, $start-1, $end-$start+1, $obs);
	}
	
	$dna = join ('', @dna);
	
	my $protein = translateDNA ($dna);
	$protein =~ s/(.{100})/$1\n/g;
	print ">$line $transcript $cchange\n";
	print "$protein\n";
}


sub translateDNA {
	my ($seq) = @_;
	my ($nt3, $protein);
	$seq = uc $seq;
	#length ($seq) % 3 == 0 or printerr "WARNING: length of DNA sequence to be translated is not multiples of 3: <length=${\(length $seq)}>\n";
	while ($seq =~ m/(...)/g) {
		defined $codon1{$1} or print "WARNING: invalid triplets found in DNA sequence to be translated: <$1>\n" and die;
		$protein .= $codon1{$1};
	}
	return $protein;
}



=head1 SYNOPSIS

 coding_change.pl [arguments] <exonic-variant-function-file> <gene-def-file> <fasta-file>

 Optional arguments:
        -h, --help                      print help message
        -m, --man                       print complete documentation
        -v, --verbose                   use verbose output

 Function: a pipeline to convert FASTQ files to ANNOVAR input files
 
 Example: coding_change.pl ex1.human.exonic_variant_function humandb/hg18_refGene.txt humandb/hg18_refGeneMrna.fa
 
 Version: $LastChangedDate: 2010-08-16 11:36:18 -0400 (Mon, 16 Aug 2010) $

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
