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