"""
Transmission Control Software (TCS)
===================================
Modified: 2021-06

Initialization for the transmission software driver

Copyright © 2021 LEAP. All Rights Reserved.
"""
import yaml
import logging
import logging.config

from pathlib import Path


# cleanup all previous logs for new runtime environment
CONFIG_PATH = Path(__file__).parent.joinpath("config/log.yaml")

# check for existance of config.yaml
if not CONFIG_PATH.exists(): raise FileNotFoundError

# configure the logger
with open(CONFIG_PATH) as file:
    logging.config.dictConfig(yaml.full_load(file))
