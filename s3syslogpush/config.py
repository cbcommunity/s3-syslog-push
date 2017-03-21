from six.moves.configparser import SafeConfigParser
import logging
import os

logger = logging.getLogger(__name__)

def verify_section_exists(config, section_name):
    """
    Verifies that a section exists
    :param config: ConfigParser object
    :param section_name: section name
    :return: returns True or False
    """
    if not config.has_section(section_name):
        logger.error("No {} section specifed".format(section_name))
        return False
    return True

def verify_option_exists(config, section_name, option_name):
    """
    Verifies that an option exists within a section and has at least a value
    :param config: ConfigParser object
    :param section_name: the section name
    :param option_name: the option name
    :return: returns True or False
    """
    if not config.has_option(section_name, option_name) or not config.get(section_name, option_name):
        logger.info("The {} section is missing option: {}".format(section_name, option_name))
        return False
    return True


def read_parse_config(filename):
    """
    Reads, validates and create a config dictionary
    :param filename: The filename to parse
    :return: return a dict with all config variables or None
    """

    config_dict = dict()

    config = SafeConfigParser()

    config.read(filename)

    #
    # Sanity checks for sections
    #
    if not verify_section_exists(config, 'general'):
        return None

    #
    # Default to port 33706
    #
    config_dict['http_server_port'] = 33706

    #
    # defaults for directories
    #
    config_dict['input_path'] = '/tmp/s3-syslog-push/input'
    config_dict['log_path'] = '/tmp/s3-syslog-push/log'

    try:
        os.makedirs(config_dict['input_path'], 0o755)
    except OSError as e:
        if e.errno == 17:  # FileExistsError
            # TODO: handle this scenario. Shouldn't happen.
            pass
    try:
        os.makedirs(config_dict['log_path'], 0o755)
    except OSError as e:
        if e.errno == 17:  # FileExistsError
            # TODO: handle this scenario. Shouldn't happen.
            pass

    for item in config.items('general'):
        config_dict[item[0]] = item[1]

    return config_dict

#
# For testing only
#
if __name__ == '__main__':
    print(read_parse_config('s3-syslog-push.conf'))


