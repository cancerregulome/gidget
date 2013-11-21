#!/usr/bin/env python

"""
This is a comand line and python api interface to a golem master.
For portabilityu, it is designed to be compatible with diffrent versions of python and have few
nonstandard dependencies so it includes some boiler plate functionality for making
http requests etc.

For commandline usage run
    golem.py -h
For programatic ussage see the doc strings of individual functions
"""

import sys
import httplib
import urlparse
import exceptions
import socket
supporttls = True

try:
    import json  # python 2.6 included simplejson as json
except ImportError:
    import simplejson as json
try:
    import ssl
except ImportError:
    supporttls = False
    print "Error importing ssl module. Https will not be supported."


usage = """Usage: golem.py [http://]hostname[:port] [-p password] [-L label] [-u email] command and args

Hosts are assumed to be serving over https unless http is specified.

Command and args can be:
run n job_executable exeutable args : run job_executable n times with the supplied args
runlist listofjobs.txt              : run each line (n n job_executable exeutable args) of the file
list                                : list statuses of all submissions on cluster
jobs                                : same as list
status subid                        : get status of a single submission
stop subid                          : stop a submission from submitting more jobs but let running jobs finish
kill subid                          : stop a submission from submitting more jobs and kill running jobs
nodes                               : list the nodes connected to the clus  ter
resize nodeid newmax                : change the number of tasks a node takes at once
resizeall newmax                    : change the number of taska of all nodes that aren't set to take 0 tasks
resizehost cname newmax             : change max tasks of a worker by cname
restart                             : cycle all golem proccess on the cluster...use only for udating core components
die                                 : kill everything ... rarelly used
"""


def runOneLine(count, args, pwd, url, loud=True, label="", email=""):
    """
    Runs a single command on a specified Golem cluster.
    Parameters:
        count - Number of times to run the command.
        args - Argument list to the command, including the command itself and all parameters.
        pwd - password to the Golem server.
        url - URL to the Golem server.
        label - optional header to label job
        email - optional email to indicate ownership
        loud - whether or not to print status messages on stdout. Defaults to True.
    Returns:
        A 2-tuple of the Golem server's response number and the body of the response.
    Throws:
        Any failure of the HTTP channel will go uncaught.
    """
    jobs = [{"Count": int(count), "Args": args}]
    jobs = json.dumps(jobs)
    data = {'command': "run"}
    if loud:
        print "Submitting run request to %s." % url
    return doPost(url, data, jobs, pwd, loud, label, email)


def runBatch(jobs, pwd, url, loud=True, label="", email=""):
    """
    Runs a Python list of jobs on the specified Golem cluster.
    Parameters:
        jobs - iterable sequence of dict-like objects fitting the job schema. Keys are of type string:
            "Count" - integer representing the number of times to run this job
            "Args" - list of strings representing the command line to run, including executable
        pwd - password for the Golem server
        url - URL to reach the Golem server, including protocol and port
        label - optional header to label job
        email - optional email to indicate ownership
        loud - whether to print status messages on stdout. Defaults to True.
    Returns:
        A 2-tuple of the Golem server's response number and the body of the response.
    Throws:
        Any failure of the HTTP channel will go uncaught.
    """
    jobs = json.dumps([job for job in jobs])
    data = {'command': "runlist"}
    if loud:
        print "Submitting run request to %s." % url
    return doPost(url, data, jobs, pwd, loud, label, email)


def runList(fo, pwd, url, loud=True, label="", email=""):
    """
    Interprets an open file as a runlist, then executes it on the specified Golem cluster.
    Parameters:
        fo - Readable open file-like-object representing a runlist.
        pwd - password for the Golem server
        url - URL to reach the Golem server, including protocol and port
        label - optional header to label job
        email - optional email to indicate ownership
        loud - whether to print status messages on stdout. Defaults to True.
    Returns:
        A 2-tuple of the Golem server's response number and the body of the response.
    Throws:
        Any failure of the HTTP channel will go uncaught.
    """
    jobs = generateJobList(fo)
    return runBatch(jobs, pwd, url, loud, label, email)


def runOnEach(jobs, pwd, url, loud=True, label="", email=""):
    """
    Runs a single job on each machine in a Golem cluster.
    Parameters:
        jobs - a single dict fitting the job schema. Keys are of type string:
            "Count" - integer representing the number of times to run this job
            "Args" - list of strings representing the command line to run, including executable
        pwd - the password for the Golem server
        url - URL to reach the Golem server, including protocol and port
        label - optional header to label job
        email - optional email to indicate ownership
        loud - whether to print status messages on stdout. Defaults to True.
    Returns:
        A 2-tuple of the Golem server's response number and the body of the response.
    Throws:
        Any failure of the HTTP channel will go uncaught.
    """
    jobs = json.dumps(jobs)
    data = {'command': "runoneach"}
    print "Submitting run request to %s." % url
    return doPost(url, data, jobs, pwd, loud, label, email)


def getJobList(url, loud=True):
    """
    Queries the Golem server for the list of current and previous jobs.
    Parameters:
        url - URL to reach the Golem server, including protocol and port
        loud - whether to print the response on stdout. Defaults to True.
    Returns:
        A 2-tuple of the Golem server's response number and the body of the response.
    Throws:
        Any failure of the HTTP channel will go uncaught.
    """
    return doGet(url, loud)


def stopJob(jobId, pwd, url, loud=True):
    """Stop a job identified by ID.
    Parameters:
        jobId - String of the ID of job to stop
        pwd - password for the Golem server
        url - URL to reach the Golem server, including protocol and port
        loud - whether to print the response on stdout. Defualts to True.
    Returns:
        A 2-tuple of the Golem server's response number and the body of the response.
    Throws:
        Any failure of the HTTP channel will go uncaught.
    """
    return doPost(url + jobId + "/stop", {}, "", pwd, loud, "", "")


def killJob(jobId, pwd, url, loud=True):
    """
    Kill a job identified by ID.
    Parameters:
        jobId - String of the ID of job to kill
        pwd - password for the Golem server
        url - URL to reach the Golem server, including protocol and port
        loud - whether to print the response on stdout. Defualts to True.
    Returns:
        A 2-tuple of the Golem server's response number and the body of the response.
    Throws:
        Any failure of the HTTP channel will go uncaught.
    """
    return doPost(url + jobId + "/kill", {}, "", pwd, loud, "", "")


def getJobStatus(jobId, url, loud=True):
    """
    Queries the Golem server for the status of a particular job.
    Parameters:
        jobID - String of the ID of job to kill
        url - URL to reach the Golem server, including protocol and port
        loud - whether to print the response on stdout. Defaults to True.
    Returns:
        A 2-tuple of the Golem server's response number and the body of the response.
    Throws:
        Any failure of the HTTP channel will go uncaught.
    """
    return doGet(url + jobId, loud)


def getNodesStatus(master, loud=True):
    """
    Queries the golem server for the status of its nodes.
    Parameters:
        master - URL to reach the Golem server, including protocol and port
        loud - whether to print the response to stdout. Defaults to True.
    Returns:
        A 2-tuple of the Golem server's response number and the body of the response.
    Throws:
        Any failure of the HTTP channel will go uncaught.
    """
    return doGet(master + "/nodes/", loud)


def resize(nodeid, size, master, pwd):
    """
    Resize a single node by node id.

    Paramaters:
        nodeid - the nodeid to be resized
        size - an inte specifing the new size of the node
        master - the master to post to
        pwd - the pwd to use
     Returns:
        A 2-tuple of the Golem server's response number and the body of the response.
    Throws:
        Any failure of the HTTP channel will go uncaught.

    """
    return doPost(master + "/nodes/" + nodeid + "/resize/" + "%s" % (size), {}, "", pwd)


def resizeName(nodename, size, master, pwd):
    """
    Resize a single node by its hostname.

    Paramaters:
        nodename - the nodename to be resized
        size - an inte specifing the new size of the node
        master - the master to post to
        pwd - the pwd to use
    Returns:
        A 2-tuple of the Golem server's response number and the body of the response.
    Throws:
        Any failure of the HTTP channel will go uncaught.

    """
    nodes = json.JSONDecoder().decode(
        getNodesStatus(master, False)[1])["Items"]
    for node in nodes:
        if(node["Hostname"].split(".")[0] == nodename):
            print("Resizing %s from %i to %s") % (
                node["Hostname"], node["MaxJobs"], size)
            return doPost(master + "/nodes/" + node["NodeId"] + "/resize/" + "%s" % (size), {}, "", pwd)


def resizeAll(size, master, pwd):
    """
    Resize all nodes that haven't been sized down to zero.

    Paramaters:
        size - an int specifing the new size of the nodes
        master - the master to post to
        pwd - the pwd to use
    Throws:
        Any failure of the HTTP channel will go uncaught.


    """
    nodes = json.JSONDecoder().decode(
        getNodesStatus(master, False)[1])["Items"]
    for node in nodes:
        if int(node["MaxJobs"]) != 0:
            print("Resizing %s from %i to %s") % (
                node["Hostname"], node["MaxJobs"], size)
            doPost(master + "/nodes/" +
                   node["NodeId"] + "/resize/" + "%s" % (size), {}, "", pwd)


class HTTPSTLSv1Connection(httplib.HTTPConnection):

        """This class allows communication via TLS, it is version of httplib.HTTPSConnection that specifies TLSv1."""

        default_port = httplib.HTTPS_PORT

        def __init__(self, host, port=None, key_file=None, cert_file=None,
                     strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
            httplib.HTTPConnection.__init__(self, host, port, strict, timeout)
            self.key_file = key_file
            self.cert_file = cert_file

        def connect(self):
            """Connect to a host on a given (TLS) port."""

            sock = socket.create_connection((self.host, self.port),
                                            self.timeout)
            if self._tunnel_host:
                self.sock = sock
                self._tunnel()
            self.sock = ssl.wrap_socket(
                sock, self.key_file, self.cert_file, False, ssl.CERT_NONE, ssl.PROTOCOL_TLSv1)


def encode_multipart_formdata(data, filebody):
    """multipart encodes a form. data should be a dictionary of the the form fields and filebody
    should be a string of the body of the file"""
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for key, value in data.iteritems():
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    if filebody != "":
        L.append('--' + BOUNDARY)
        L.append(
            'Content-Disposition: form-data; name="jsonfile"; filename="data.json"')
        L.append('Content-Type: text/plain')
        L.append('')
        L.append(filebody)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


def doGet(url, loud=True):
    """
    posts a GET request to url
    """
    u = urlparse.urlparse(url)
    if u.scheme == "http":
        conn = httplib.HTTPConnection(u.hostname, u.port)
    else:
        # privateKey=key,certChain=X509CertChain([cert]))
        conn = HTTPSTLSv1Connection(u.hostname, u.port)

    try:
        conn.request("GET", u.path)
    except ssl.SSLError:
        print "Ssl error. Did you mean to specify 'http://'?"
        dieWithUssage()

    resp = conn.getresponse()
    output = None
    if resp.status == 200:
        output = resp.read()
        if loud:
            try:
                print json.dumps(json.JSONDecoder().decode(output), sort_keys=True, indent=4)
            except:
                print output
    elif loud:
        print resp.status, resp.reason

    return resp, output
    # conn.close()


def doPost(url, paramMap, jsondata, password, loud=True, label="", email=""):
    """
    posts a multipart form to url, paramMap should be a dictionary of the form fields, json data
    should be a string of the body of the file (json in our case) and password should be the password
    to include in the header
    """

    u = urlparse.urlparse(url)
    content_type, body = encode_multipart_formdata(paramMap, jsondata)
    headers = {"Content-type": content_type,
               'content-length': str(len(body)),
               "Accept": "text/plain",
               "x-golem-apikey": password,
               "x-golem-job-label": label,
               "x-golem-job-owner": email
               }

    if loud:
        print "scheme: %s host: %s port: %s" % (u.scheme, u.hostname, u.port)

    if u.scheme == "http":
        conn = httplib.HTTPConnection(u.hostname, u.port)
    else:

        # ,privateKey=key,certChain=X509CertChain([cert]))
        conn = HTTPSTLSv1Connection(u.hostname, u.port)
    try:
        conn.request("POST", u.path, body, headers)
    except ssl.SSLError:
        print "Ssl error. Did you mean to specify 'http://'?"
        dieWithUssage()
    output = None
    resp = conn.getresponse()
    if resp.status == 200:
        print "got 200"
        output = resp.read()
        if loud:
            try:
                print json.dumps(json.JSONDecoder().decode(output), sort_keys=True, indent=4)
            except:
                print output
    elif loud:
        print resp.status, resp.reason

    return resp, output
    # conn.close()


def canonizeMaster(master, loud=True):
    """Attaches an http or https prefix onto the master connection string if needed.
    """
    if master[0:4] != "http":
        if supporttls:
            if loud:
                print "Using https."
            master = "https://" + master
        else:
            if loud:
                print "Using http (insecure)."
            master = "http://" + master
    if master[0:5] == "https" and supporttls == False:
        raise ValueError(
            "HTTPS specified, but the SSL package tlslite is not available. Install tlslite.")
    return master


def generateJobList(fo):
    """Generator that produces a sequence of job dicts from a runlist file. More efficient than list approach.
    """
    for line in fo:
        values = line.split()
        yield {"Count": int(values[0]), "Args": values[1:]}


def dieWithUssage():
    """
    Print the usage and exit with an error code.
    """
    print "\n", usage
    sys.exit(1)


def main():
    """
    Parses argv and performs the user-specified commands. See usage info.

    Called if __name___ == "__main__". Not really intended to be called otherwise. Hardwired to reference sys.argv.
    """
    if len(sys.argv) < 3:
        print usage
        return
    master = sys.argv[1]
    commandIndex = 2
    pwd = ""
    label = ""
    email = ""
    nonflags = []
    flags = True
    # TODO: abstract and automate printing of ussage
    while commandIndex < len(sys.argv):
        if flags == True and sys.argv[commandIndex] == "-p":
            pwd = sys.argv[commandIndex + 1]
            commandIndex = commandIndex + 2

        elif flags == True and sys.argv[commandIndex] == "-L":
            label = sys.argv[commandIndex + 1]
            commandIndex = commandIndex + 2

        elif flags == True and sys.argv[commandIndex] == "-u":
            email = sys.argv[commandIndex + 1]
            commandIndex = commandIndex + 2
        else:
            flags = False
            nonflags.append(sys.argv[commandIndex])
            commandIndex = commandIndex + 1

    master = canonizeMaster(master)

    url = master + "/jobs/"

    try:
        cmd = nonflags[0].lower()
        if cmd == "run":
            runOneLine(int(nonflags[1]), nonflags[2:],
                       pwd, url, True, label, email)
        elif cmd == "runlist":
            fo = open(nonflags[1])
            runList(fo, pwd, url, True, label, email)
            fo.close()
        elif cmd == "runoneach":
            jobs = [{"Args": nonflags[1]}]
            runOnEach(jobs, pwd, url, True, label, email)
        elif cmd == "jobs" or cmd == "list":
            getJobList(url)
        elif cmd == "stop":
            jobId = nonflags[1]
            stopJob(jobId, pwd, url)
        elif cmd == "kill":
            jobId = nonflags[1]
            killJob(jobId, pwd, url)
        elif cmd == "status":
            jobId = nonflags[1]
            getJobStatus(jobId, url)
        elif cmd == "nodes":
            getNodesStatus(master)
        elif cmd == "resize":
            resize(nonflags[1], nonflags[2], master, pwd)
        elif cmd == "resizehost":
            resizeName(nonflags[1], nonflags[2], master, pwd)
        elif cmd == "resizeall":
            resizeAll(nonflags[1], master, pwd)
        elif cmd == "restart":
            input = raw_input(
                "This will kill all jobs on the cluster and is only used for updating golem version. Enter \"Y\" to continue.>")
            if input == "Y":
                doPost(master + "/nodes/restart", {}, "", pwd)
            else:
                print "Canceled"
        elif cmd == "die":
            input = raw_input(
                "This brings the entire cluster down and is almost never used. Enter \"Y\" to continue.>")
            if input == "Y":
                doPost(master + "/nodes/die", {}, "", pwd)
            else:
                print "Canceled"
        else:
            dieWithUssage()
    except exceptions.SystemExit:
        pass
    except:
        print "There was an error:", sys.exc_info()[0], "\n", usage, "\n"
        raise


if __name__ == "__main__":
    main()
