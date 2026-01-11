# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


import threading
import subprocess
import time
import logging


logger: logging.Logger = logging.getLogger(name=__name__)


def restart_api(delay: int) -> None:
    """Runs the restart script located at '/var/www/html/api.ajholzer.net_restart.sh' with the specified delay.

    Args:
        delay (int): The time to wait before restarting the process in seconds.
    """

    def restart() -> None:
        logger.info(f"Restarting API in {delay} seconds...")

        # Wait a few seconds to ensure everything is done
        time.sleep(delay)

        logger.info("Restarting API...")

        # Run restart script
        subprocess.run(
            ["sudo", "/usr/bin/systemctl", "restart", "api.ajholzer.net"],
            check=True,
        )

    threading.Thread(target=restart, daemon=True).start()
