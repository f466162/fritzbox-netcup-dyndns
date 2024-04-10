import logging

from configuration import Configuration


def initialize_logger(config: Configuration):
    logger = logging.getLogger(__name__)
    config.loglevel = logging.getLevelName(config.loglevel)
    logging.basicConfig(level=config.loglevel,
                        format="%(asctime)s %(levelname)s %(processName)s/%(module)s[%(process)d]: %(message)s "
                               "[%(pathname)s:%(lineno)d]")
    return logger
