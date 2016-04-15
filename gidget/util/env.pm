#!/usr/bin/perl
package env;

use strict;
use warnings;


use File::Basename;
use Cwd qw(abs_path);
use Env;

use Exporter;
our @ISA = 'Exporter';
our @EXPORT = qw( %gidgetConfigVars ); # automatically exported variables


Env::import();

my $required_env_vars = dirname(abs_path (__FILE__)) . "/../../config/required_env_vars";
open (REQUIRED_ENV_VARS, $required_env_vars) or die "Error: cannot read required_env_vars file: $!\n";

our %gidgetConfigVars = ();

my $allSet="true";
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
            print "\n";
            # print "$linedata[0]:\n";
            # print "  $linedata[1]\n";
            print "*** ERROR: $linedata[0] exists but unintialized or blank!\n(try \"export $linedata[0]=<YOUR_SETTING>\")\n";
            print "*** usage:\n";
            print "***  $linedata[0]: $linedata[1]\n\n";
            $allSet = "false"
        }
        else {
            # print "  defined!\n";
            $gidgetConfigVars{$linedata[0]} = $variableValue;
        }
    }
    else {
            # print "$linedata[0]:\n";
            # print "  $linedata[1]\n";
            print "*** ERROR: $linedata[0] not defined!\n(try \"export $linedata[0]=<YOUR_SETTING>\")\n";
            print "*** usage:\n";
            print "***  $linedata[0]: $linedata[1]\n\n";
            $allSet = "false";
    }
}
if ($allSet eq "false") {
        die "there were unset required variables; please see above.\nexiting with error\n\n"
}

close (REQUIRED_ENV_VARS);

1;
