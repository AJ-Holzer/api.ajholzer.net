# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


import logging

from utils.logging import setup_logging
from api.app import API


logger: logging.Logger = logging.getLogger(name=__name__)


def main() -> None:
    # Load config
    from config import config

    # Set up logging from config
    setup_logging(loglevel=config.LOGLEVEL, log_filepath=config.LOG_FILEPATH)

    # Check config
    config.check()

    # Init api
    api: API = API()

    # Start api
    api.start()


if __name__ == "__main__":
    main()
