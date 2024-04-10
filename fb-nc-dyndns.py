#!/usr/bin/env python
import math
import random
import signal
import sys
import time

from configuration import Configuration
from job import Job
from sentry import initialize_sentry
from utils import initialize_logger

# Load config
config = Configuration()

# Initialize logging
logger = initialize_logger(config)

# Initialize Sentry
initialize_sentry(config, logger)


# Trap shutdown signals
def shutdown(signum, stack):
    logger.info("Shutting down, signal={}".format(signum))
    sys.exit()


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

# Initialize job
job = Job(config, logger)

# Control loop
while True:
    # Store last addresses
    job.check_and_update()

    # If an interval is set > 0, sleep and run again
    if config.interval > 0:
        # Sleep up to config.interval + 10% to relax hard timing
        skew = random.randint(0, max(1, math.floor(config.interval * 0.1)))
        logger.debug("Next check for updating DNS records in {} (skew = {})".format(config.interval + skew, skew))
        time.sleep(config.interval + skew)
    else:
        break
