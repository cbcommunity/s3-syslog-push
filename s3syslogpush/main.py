import os
import sys
import argparse
import logging
from logging.handlers import WatchedFileHandler
import time
import socket
import boto3
from tempfile import NamedTemporaryFile


log = logging.getLogger("s3-syslog-push")

from .globals import s3_settings, directory_settings, output_settings
from .config import read_parse_config


class Main(object):
    def __init__(self):
        self.input_dir = directory_settings.input_path

        boto_session = boto3.Session(profile_name=s3_settings.profile_name)
        self.s3 = boto_session.client('s3')
        self.input_bucket = boto_session.resource('s3').Bucket(s3_settings.bucket_name)

        self.ip = socket.gethostbyname(output_settings.hostname)
        self.port = int(output_settings.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def loop(self):
        while True:
            try:
                self.loop_iteration()
            except KeyboardInterrupt:
                log.info("Exiting due to keyboard interrupt")
                break
            except Exception as e:
                log.error("Error during processing loop iteration: {0}".format(str(e)), exc_info=True)

            time.sleep(30)

        return 0

    def push_file_syslog(self, fn):
        for ln in open(fn, 'r'):
            ln = ln.strip()
            self.sock.sendto(ln.encode('utf-8')+b'\n', (self.ip, self.port))
            time.sleep(0.01)

    def delete_input_file(self, s3fn, localfp):
        self.s3.delete_object(Bucket=s3_settings.bucket_name, Key=s3fn)
        os.unlink(localfp.name)

    def download_file(self, bucket_name, objkey):
        new_fp = NamedTemporaryFile(dir=self.input_dir, delete=False)
        self.s3.download_file(bucket_name, objkey, new_fp.name)
        return new_fp

    def loop_iteration(self):
        for obj in list(self.input_bucket.objects.all()):
            try:
                log.info("Downloading file {0}".format(obj.key))
                input_file = self.download_file(s3_settings.bucket_name, obj.key)
            except Exception as e:
                log.error("Error downloading file {1}: {0}".format(e, obj.key), exc_info=True)
                continue

            try:
                log.info("Pushing events from file {0}".format(obj.key))
                self.push_file_syslog(input_file.name)
            except Exception as e:
                log.error("Error pushing file {0} contents: {1}".format(obj.key, str(e)), exc_info=True)
                continue

            log.info("Deleting source file {0} from S3".format(obj.key))
            self.delete_input_file(obj.key, input_file)


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger("s3-syslog-push")

    logging.getLogger("botocore.vendored.requests.packages.urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger("boto3.resources.collection").setLevel(logging.ERROR)

    parser = argparse.ArgumentParser("S3-Syslog push connector")
    parser.add_argument('-c', '--config-file', help="Absolute path to configuration file", required=True)
    parser.add_argument('-d', '--debug', action='store_true', help="Debug flag")

    args = parser.parse_args()

    #
    # Read the config file
    #
    config_dict = read_parse_config(args.config_file)

    #
    # set up logging
    #
    formatter = logging.Formatter("%(asctime)s s3-syslog-push [%(process)d]: %(message)s",
                                  "%b %d %H:%M:%S")
    formatter.converter = time.gmtime
    file_handler = WatchedFileHandler(filename=os.path.join(config_dict['log_path'], 's3-syslog-forwarder.log'))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    #
    # s3 settings
    #
    s3_settings.profile_name = config_dict.get('aws_profile')
    s3_settings.bucket_name = config_dict['input_bucket_name']

    #
    # Temporary directory settings
    #
    directory_settings.input_path = config_dict['input_path']

    output_settings.hostname = config_dict["syslog_host"]
    output_settings.port = config_dict["syslog_port"]

    main_thread = Main()
    return main_thread.loop()


if __name__ == '__main__':
    sys.exit(main())
