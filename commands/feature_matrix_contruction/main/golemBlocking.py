"""
Extension to golem.py. As a library, provides a method to wait for a specified job to complete.
As a script, performs the 'run' or 'runlist' operations from golem.py, but does not terminate
until the remote job is complete.
"""

import re
import sys

import golem
import optparse
import time

try:
    import json  # python 2.6 included simplejson as json
except ImportError:
    import simplejson as json

QUERY_INTERVAL = 3.0  # in seconds


def stall(jobid, composedUrl, loud=True):
    """
    Waits until the specified job is no longer Running.
    If it can't communicate with the server, it will throw an IOError.
    If there is no "Running" field in the response at all, Stall will terminate normally.
    If a sleep is interrupted via keyboard, stall will throw a KeyboardInterrupt.
    """
    decoder = json.JSONDecoder()
    while True:
        response, content = golem.getJobStatus(jobid, composedUrl, loud)
        if response.status != 200:
            raise IOError(
                "Unsuccessful status when communicating with server: " + response)
        contentDict = decoder.decode(content)
        if contentDict["State"] == "COMPLETE":
            return contentDict
        time.sleep(QUERY_INTERVAL)

usage = """Usage: golemBlocking.py hostname [-p password] command and args
where command and args can be:
run n job_executable exeutable args : run job_executable n times with the supplied args
runlist listofjobs.txt              : run each line (n n job_executable exeutable args) of the file

This version of the script waits for all machines to stop processing before halting.
If interrupted at the keyboard, the remote job is stopped.

golemBlocking produces a JOBID.DAT file containing only the ID of the job that the run of
golemBlocking created, to aid in finding the output later.
"""


def printUsage():
    """
    Prints a usage message. No parameters, returns None.
    """
    print usage


def jobIdFromResponse(content):
    """
    Extracts a jobID from the body of a Golem response.
    Parameter:
        content - String containing the body of the response from a Golem server to a job queue request.
    Returns:
        String representing the job ID embedded in that response.
    Throws:
        A creative variety of exceptions if the string isn't similar to the body of a Golem response. If this
        function starts throwing exceptions left and right, revisit it- perhaps the server protocol changed.
    """
    try:
        contentDict = json.JSONDecoder().decode(content)
        id = contentDict["JobId"]
    except (ValueError, KeyError, AttributeError):
        try:
            id = re.search(r'[\s\{]"?JobId:"(\w*)"', content).group(1)
        except AttributeError:
            id = re.search(r"[\s\{]'?JobId:'(\w*)'", content).group(1)
    return id


def main(argv):
    """
    Handles command line arguments and uses them to start a job (or job batch) and wait for it to finish.
    Intended to be used interactively from the __name__ == "__main__" check.
    """
    parser = optparse.OptionParser()
    parser.add_option(
        "-p", "--password", dest="password", help="Specify the password for connecting to the server.",
        default="")
    parser.add_option("-e", "--echo", dest="echo", action="store_true",
                      default=False, help="Not yet implemented")
    # because "late params" are actually arguments to the target script
    flags, args = parser.parse_args(argv[1:4])

    password = flags.password
    args = args + argv[4:]

    if len(args) < 3:
        print "Not enough arguments."
        printUsage()
        sys.exit(status=493)

    master = args[0]

    master = golem.canonizeMaster(master)
    url = master + "/jobs/"

    command = args[1]
    cmdArgs = args[2:]

    if command == "run":
        response, content = golem.runOneLine(
            int(cmdArgs[0]), cmdArgs[1:], password, url)
    elif command == "runlist":
        response, content = golem.runList(open(cmdArgs[0]), password, url)
    elif command == "runoneach":
        response, content = golem.runOnEach([{"Args": cmdArgs}], password, url)
    else:
        raise ValueError(
            "golemBlocking can only handle the commands 'run', 'runlist', and 'runoneach'.")

    id = jobIdFromResponse(content)

    try:
        stall(id, url)
    except KeyboardInterrupt:
        golem.stopJob(id, password, url)
        print "Job halted."

    jobid_dat = open("JOBID.DAT", "w")
    jobid_dat.write(id)
    jobid_dat.flush()
    jobid_dat.close()


if __name__ == "__main__":
    main(sys.argv)
