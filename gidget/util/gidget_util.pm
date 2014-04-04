#!/usr/bin/perl
package Gidget_Util;

use warnings;
use strict;

use File::Basename;
use Cwd qw(abs_path);

use parent 'Exporter'; # imports and subclasses Exporter

use Env;

Env::import();

my $required_env_vars = dirname(abs_path (__FILE__)) . "/../config/required_env_vars";
open (REQUIRED_ENV_VARS, $required_env_vars) or die "Error: cannot read required_env_vars file: $!\n";

our %tcgaMAFVars = ();

LINE: while (<REQUIRED_ENV_VARS>) {
    chomp;
    if (m/^#/) {
        # print "skipping comment line: $_\n";
        next LINE;
    }
    if (m/^$/ ) {
        # print "skipping blank line: $_\n";
        next LINE;
    }
    # print "splitting: $_\n";
    my @linedata;
    @linedata = split(/\t/);
    # print "got $linedata[0], $linedata[1]\n";
    my $variableValue;
    if (exists $ENV{$linedata[0]}) {
        $variableValue = $ENV{$linedata[0]};
        if ($variableValue eq "") {
            print "  exists but unintialized or blank!\n"
        }
        else {
            # print "  defined!\n";
            $tcgaMAFVars{$linedata[0]} = $variableValue;
        }
    }
    else {
        die "$linedata[0] not defined!\n"
    }
}

our @EXPORT = qw(%tcgaMAFVars); # put stuff here you want to export