#!/bin/bash

###
# usage

# every file in the TCGA Feature Matrix Construction project should begin
# by sourcing tcga_fmp_util.sh, NOT this file


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


# TODO more helpful error messages
verifyRequiredVariables () {
    : ${LD_LIBRARY_PATH:?" environment variable must be set and non-empty"}

    # path to top of this project's code
    : ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty"}

    # top level data directory, also containing FMP outputs
    : ${TCGAFMP_DATA_DIR:?" environment variable must be set and non-empty"}

    # path to dcc mirror
    : ${TCGAFMP_DCC_MIRROR:?" environment variable must be set and non-empty"}

    # path to dcc snapshot
    : ${TCGAFMP_DCC_SNAPSHOT:?" environment variable must be set and non-empty"}

    # path to firehose
    : ${TCGAFMP_FIREHOUSE_MIRROR:?" environment variable must be set and non-empty"}
}


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


# check that PYTHONPATH is set correctly
# TODO: the currently check only verifies that some version of
# gidget is in the path; to be more accurate, the test should make sure that
# the specific version in TCGAFMP_ROOT_DIR is being used
checkPythonPath() {
    if [[ "$PYTHONPATH" != *"gidget"* ]]; then
        echo " "
        echo " your PYTHONPATH should include paths to gidget/commands/... directories "
        echo " "
        exit 99
    fi
}



###
# run tests and set global variables

verifyRequiredVariables
getScriptPath
checkPythonPath

# this must be the last line; prevents re-execution of this script.
export TCGAFMP_IMPORTED_UTILS=IMPORTED
