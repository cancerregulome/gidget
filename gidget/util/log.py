#!/usr/bin/env python

__author__ = 'nwilson'

import threading
import os
import datetime

LOG_DATE_FORMAT="[%H:%M:%S]"

class LogPipe(threading.Thread):

    def __init__(self, tag, logfile):
        """
        Setup the object with a logger
        and start the thread
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.tag = " " + tag
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.fdLog = logfile
        self.start()

    def fileno(self):
        """
        Return the write file descriptor of the pipe
        """
        return self.fdWrite

    def run(self):
        """
        Run the thread, logging everything.
        """
        for line in iter(self.pipeReader.readline, ''):
            # TODO
            self.fdLog.write("%s %s %s\n" % (datetime.now().strftime(LOG_DATE_FORMAT), self.tag, line.strip()))

        self.pipeReader.close()

    def close(self):
        """
        Close the write end of the pipe.
        """
        # TODO
        os.close(self.fdWrite)
        self.logfile.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
