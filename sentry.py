import logging
import platform

import sentry_sdk

from configuration import Configuration


class Sentry():
    config: Configuration
    logger: logging.Logger

    def __init__(self, config: Configuration, logger: logging.Logger):
        self.config = config
        self.logger = logger

    def initialize_sentry(self):
        if self.config.sentry_url:
            self.logger.info("Enabling Sentry")
            sentry_sdk.init(self.config.sentry_url, traces_sample_rate=1.0)
            sentry_sdk.set_tag("hostname", platform.node())
        else:
            self.logger.info("Sentry not enabled")

    def set_sentry_tag(self, record, target_zone):
        if self.config.sentry_url:
            sentry_sdk.set_tag("domain", ("%s.%s" % (record, target_zone)))
