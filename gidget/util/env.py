#!/usr/bin/env python

# verify that all required environmental variables are present,
# and set in the global namespace if they aren't already

# all python scripts in the gidget project should include this line:

# from env import gidgetConfigVars

# which checks to make sure that all required environmental variables are defined,
# and if so, populates a dictionary "gidgetConfigVars" with the env var names and values

import os
import sys

gidgetConfigVars={}

try:
    rootDir = os.getenv("GIDGET_SOURCE_ROOT")
    requiredEnvVarFilePath = rootDir + "/config/required_env_vars"
except:
    print " ERROR ... GIDGET_SOURCE_ROOT environment variable is required"
    sys.exit(-1)

f = open(requiredEnvVarFilePath, 'r')

allSet = True
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
		print "*** ERROR: required environmental variable " + varName + " was not defined;"
		print "*** usage:\n" + "***  " + varName + ": " + varDesc
		print
		allSet = False
	elif os.environ.get(varName) == "":
		print "ERROR: required environmental variable " + varName + " was defined, but blank;"
		print "*** usage:\n" + "***  " + varName + ": " + varDesc
		print
		allSet = False

	gidgetConfigVars[varName] = os.environ.get(varName)

if allSet != True:
		print
		print "there were unset required variables; please see above."
		print "exiting with error"
		exit(-1)

#print "all required variables defined!"
