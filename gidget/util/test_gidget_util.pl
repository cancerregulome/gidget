#!/usr/bin/perl
use warnings;
use strict;

use File::Basename;
use Cwd qw(abs_path);

use lib dirname(abs_path(__FILE__));
use Gidget_Util;

foreach my $var (keys %tcgaMAFVars) {
    print "found $var: $tcgaMAFVars{$var}\n";
}
