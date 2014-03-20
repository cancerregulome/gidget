#!/bin/bash

###
# usage

# every file in the TCGA Feature Matrix Construction project should begin
# by sourcing this file


###
# description

# This file defines global variables, defines functions,
# and then runs tests and set global variables


###
# global variables
SCRIPT_PATH=


###
# functions


# TODO more helpful error messages
verifyRequiredVariables () {
    : ${LD_LIBRARY_PATH:?" environment variable must be set and non-empty"}

    # path to top of this project's code
    : ${TCGAFMP_ROOT_DIR:?" environment variable must be set and non-empty"}

    # top level data directory
    : ${TCGAFMP_DATA_DIR:?" environment variable must be set and non-empty"}

    # top level outputs directory
    : ${TCGAFMP_OUTPUTS_DIR:?" environment variable must be set and non-empty"}
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
