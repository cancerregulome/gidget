#!/usr/bin/env python 

# verify that all required environmental variables are present,
# and set in the global namespace if they aren't already

# all python scripts in the TCGA FMP project should include this line:

# from tcga_fmp_util import tcgaFMPVars

# which checks to make sure that all required environmental variables are defined,
# and if so, populates a dictionary "tcgaFMPVars" the the env var names and values 

import os

tcgaFMPVars={}

try:
    rootDir = os.getenv("TCGAFMP_ROOT_DIR")
    requiredEnvVarFilePath = rootDir + "/config/required_env_vars"
except:
    print " ERROR ... TCGAFMP_ROOT_DIR environment variable is required "
    sys.exit(-1)

f = open(requiredEnvVarFilePath, 'r')

for line in f:
	line=line.strip()
	if len(line) == 0:
		#print "skipped blank line"
		continue
	if line[0] == "#":
		#print "skipped comment line: ", line
		continue
	#print "line to parse: ", line
	fields=line.split('\t')
	#print fields
	varName = fields[0]
	varDesc = fields[1]
	# print "variable name: " + varName
	# print "description: " + varDesc
	if os.environ.get(varName) == None:
		print "ERROR: required environmental variable " + varName + " was not defined;"
		print
		print "    " + varName + ": " + varDesc
		print
		print "exiting with error"
		exit(-1)
	elif os.environ.get(varName) == "":
		print "ERROR: required environmental variable " + varName + " was defined, but blank;"
		print
		print "    " + varName + ": " + varDesc
		print
		print "exiting with error"
		exit(-1)

	tcgaFMPVars[varName] = os.environ.get(varName)

#print "all required variables defined!"
