# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# -*- mode: python; indent-tabs-mode nil; tab-width 4; python-indent 4; -*-

"""
usage: gidget help
       gidget help [<subcommand-name>]

"""

from docopt import docopt


if __name__ == '__main__':
    print(docopt(__doc__))

def parse(args):
	helpArgs = docopt(__doc__, argv = args)
	requestedSubcommand = helpArgs['<subcommand-name>']
	if requestedSubcommand == None:
		print "Use 'gidget help <subcommand-name>' for detailed help on specific"
		print "gidget commands."
	else:
		# TODO: check for valid subcommand
		print "help requested on gidget subcommand \"%s\"" % requestedSubcommand
		# TODO: print specific help topic
