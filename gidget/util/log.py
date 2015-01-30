#!/usr/bin/env python

__author__ = 'nwilson'

import threading
import os
import datetime
import sys

LOG_DATE_FORMAT = "%H:%M:%S"
LOGGER_ENV = "GIDGET_LOG_FILE"

def log(tag, msg):
    Logger._getOrCreate().log(tag, msg)

class Logger:
    _loggerThisProcess = None

    def __init__(self, logFilePath):
        self.fdLog = open(logFilePath, "a")

    def log(self, tag, msg):
        self.fdLog.write("[%s] %s %s\n" % (datetime.now().strftime(LOG_DATE_FORMAT), tag, msg.strip()))

    def close(self):
        self.fdLog.close()

    @staticmethod
    def _getOrCreate():
        if Logger._loggerThisProcess is not None:
            return Logger._loggerThisProcess

        assert os.getenv(LOGGER_ENV) is not None

        Logger._loggerThisProcess = Logger(os.getenv(LOGGER_ENV))
        return Logger._loggerThisProcess

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.logFile.closed():
            self.logFile.close()

class LogPipe(threading.Thread):
    def __init__(self, tag, logger):
        """
        Setup the object with a logger
        and start the thread
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.tag = tag
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.logger = logger
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
            self.logger.log(self.tag, line)

        self.pipeReader.close()

    def close(self):
        """
        Close the write end of the pipe.
        """
        # TODO
        os.close(self.fdWrite)
        self.join()
        self.pipeReader.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# for use when logging is needed from a shell script or Perl code
if __name__ == "__main__":

    if len(sys.argv) != 3:
        sys.stderr.write("Usage: python %s <tag> <message>" % sys.argv[0])
        exit(1)

    log(sys.argv[1], sys.argv[2])