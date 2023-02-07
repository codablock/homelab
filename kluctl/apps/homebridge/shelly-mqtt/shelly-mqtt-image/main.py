#!/usr/bin/env python3
import logging

import yaml

from shelly import update_shellies
from mqtt import start_mqtt
from update_homebridge import update_homebridge_accessories

logger = logging.getLogger(__name__)


def main():
    format = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=format)

    logger.info("starting...")

    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    update_shellies(config)
    update_homebridge_accessories(config)

    start_mqtt(config)


if __name__ == "__main__":
    main()

