# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


import os
import dotenv
import logging

from typing import Optional
from pathlib import Path


# Create logger
logger: logging.Logger = logging.getLogger(name=__name__)


# Define valid log levels
NAME_TO_LEVEL: list[str] = [
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARN",
    "WARNING",
    "INFO",
    "DEBUG",
    "NOTSET",
]


class Config:
    def __init__(self) -> None:
        """Loads the .env and .config file."""
        # Load .env file
        logger.debug("Loading environment variables...")
        dotenv.load_dotenv(dotenv_path=Path("/etc/api.ajholzer.net/.env").resolve())

        # Define logging config
        self.LOGLEVEL: str = os.getenv(key="LOGLEVEL", default="INFO")
        self.LOG_FILEPATH: Path = (
            Path(os.getenv(key="LOG_FILEPATH", default="api.log"))
            .expanduser()
            .resolve()
        )

        # Define GitHub config
        self.GITHUB_TOKEN: Optional[str] = os.getenv(key="GITHUB_TOKEN")
        self.GITHUB_USERNAME: Optional[str] = os.getenv(key="GITHUB_USERNAME")
        self.GITHUB_MAX_REPOS: int = int(os.getenv(key="GITHUB_MAX_REPOS", default=20))

        # Expiration config
        self.REPOSITORY_EXPIRATION_INTERVAL_MINUTES: int = int(
            os.getenv(
                key="REPOSITORY_EXPIRATION_INTERVAL_MINUTES",
                default=60,
            )
        )

        # Server config
        self.HOST_IP: str = os.getenv("HOST_IP", "127.0.0.1")
        self.HOST_PORT: int = int(os.getenv("HOST_PORT", 5000))
        self.RELOAD_API: bool = os.getenv("RELOAD_API", "False").lower() in (
            "true",
            "1",
        )

        # API config
        self.API_TITLE: str = "api.ajholzer.net"
        self.API_VERSION: str = "1.0.0"
        self.API_PREFIX: str = os.getenv("API_PREFIX", "")

    def check(self) -> None:
        """Checks the config for missing values.

        Raises:
            ValueError: When a value is not specified for a config key.
        """
        logger.debug("Checking config...")
        if not self.GITHUB_TOKEN or self.GITHUB_TOKEN.lower() == "none":
            logger.exception("'GITHUB_TOKEN' must be specified in the .env file!")

        if not self.GITHUB_USERNAME or self.GITHUB_USERNAME.lower() == "none":
            logger.exception("'GITHUB_USERNAME' must be specified in the .env file!")

        if not self.LOGLEVEL.isdigit() and self.LOGLEVEL not in NAME_TO_LEVEL:
            logger.exception(f"Invalid LOGLEVEL: {self.LOGLEVEL}")


config = Config()
