from threading import RLock
import json
import time
import sys
import copy
from six import iteritems
from collections import deque
from logging import StreamHandler
import datetime


__version__ = "1.0"


class S3Settings(object):
    def __init__(self, profile_name='default', bucket_name=None, output_profile_name='default'):
        self.profile_name = profile_name
        self.bucket_name = bucket_name


class DirectorySettings(object):
    def __init__(self,
                 input_path='/tmp/s3-input'):
        self.input_path = input_path


class OutputSettings(object):
    def __init__(self, hostname=None, port=None):
        self.hostname = hostname
        self.port = port


s3_settings = S3Settings()
directory_settings = DirectorySettings()
output_settings = OutputSettings()


class RecentLogHandler(StreamHandler):
    def __init__(self, log_handler):
        super(RecentLogHandler, self).__init__()
        self.log_handler = log_handler

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_handler.log_message(msg, level=record.levelname, filename=record.filename, line=record.lineno,
                                         createtime=record.created, thread=record.threadName, process=record.process)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


