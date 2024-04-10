import logging
import platform

import sentry_sdk

from configuration import Configuration


def initialize_sentry(config: Configuration, logger: logging.Logger):
    if config.sentry_url:
        logger.info("Enabling Sentry")
        sentry_sdk.init(config.sentry_url, traces_sample_rate=1.0)
        sentry_sdk.set_tag("hostname", platform.node())
    else:
        logger.info("Sentry not enabled")


def set_sentry_tag(config: Configuration, record, target_zone):
    if config.sentry_url:
        sentry_sdk.set_tag("domain", ("%s.%s" % (record, target_zone)))
