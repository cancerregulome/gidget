#!/usr/bin/perl
use warnings;
use strict;

use File::Basename;
use Cwd qw(abs_path);

use lib dirname(abs_path(__FILE__));
use env;

foreach my $var (keys %gidgetConfigVars) {
    print "found $var: $gidgetConfigVars{$var}\n";
}
