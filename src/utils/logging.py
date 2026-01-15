# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


import logging
import logging.config

from pathlib import Path


def setup_logging(loglevel: int | str, log_filepath: Path) -> None:
    """Fully set up logging configuration.

    Args:
        loglevel (int | str): The loglevel that is used as root.
        log_filepath (Path): The filepath of the logfile.
    """
    # Create parent directories
    log_filepath.parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s >> %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": loglevel,
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "level": "DEBUG",
                    "formatter": "default",
                    "filename": str(log_filepath),
                    "encoding": "UTF-8",
                },
            },
            "root": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
            },
        }
    )


def setup_bootstrap_logging() -> None:
    """Set up bootstrap logging configuration."""
    setup_logging(
        loglevel=logging.DEBUG,
        log_filepath=Path("api_bootstrap.log").resolve(),
    )
