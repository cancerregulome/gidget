#!/bin/bash

###
# usage

# every file in the TCGA Feature Matrix Construction project should begin
# by sourcing gidget_util.sh, NOT this file


###
# description

# This file defines global variables, defines functions,
# and then runs tests and set global variables


###
# global variables
#
# to avoid unnecessary re-execution, any global variables
# must be eventually exported, so that they will be picked up
# by any subshell.
#
# TODO: revisit this if there are any functions that a subshell
# might actually need to use.

SCRIPT_PATH=
TCGAFMP_IMPORTED_UTILS=



###
# functions


# remove any symlinks by recursively expanding path, in a POSIX-compliant way
# from # http://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself
getScriptPath() {
    pushd . > /dev/null
    SCRIPT_PATH="${BASH_SOURCE[0]}";
    while([ -h "${SCRIPT_PATH}" ]); do
        cd "`dirname "${SCRIPT_PATH}"`"
        SCRIPT_PATH="$(readlink "`basename "${SCRIPT_PATH}"`")";
    done
    cd "`dirname "${SCRIPT_PATH}"`" > /dev/null
    SCRIPT_PATH="`pwd`";
    popd  > /dev/null
    export SCRIPT_PATH
}


# checks for required variables, as described by the file named
# in the parameter 
verifyRequiredVariables () {
    while read line; do

        if [[ $line == \#* ]]; then
            # comment line
            continue
        fi

        if [ -z "$line" ]; then
            # blank line
            continue
        fi

        # the $'\t' syntax below is an 'ANSI-C' bash string:
        # http://stackoverflow.com/a/6656767
        varName=${line%%$'\t'*}
        descr=${line##*$'\t'}
        # echo [$varName]: $descr

        # the ${!varName} syntax is an indirect refernce,
        # supported since bash v2
        if [ -z ${!varName} ]; then
            echo "*** error: required environmental variable $varName was not set"
            echo "usage:"
            echo "  $varName: $descr"
            echo
            echo "*** exiting"
            exit -1
        fi
    done < $1
}


# check that PYTHONPATH is set correctly
# TODO: the currently check only verifies that some version of
# gidget is in the path; to be more accurate, the test should make sure that
# the specific version in TCGAFMP_ROOT_DIR is being used
checkPythonPath() {
    if [[ "$PYTHONPATH" != *"gidget"* ]]; then
        echo " "
        echo " your PYTHONPATH should include paths to gidget/commands/... and gidget/gidget/utils directories"
        echo " "
        exit 99
    fi
}



###
# run tests and set global variables

getScriptPath
verifyRequiredVariables ${TCGAFMP_ROOT_DIR}/../../config/required_env_vars
checkPythonPath

# this must be the last line; prevents re-execution of this script.
export TCGAFMP_IMPORTED_UTILS=IMPORTED
