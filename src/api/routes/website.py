# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


import subprocess
import hmac
import hashlib
import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from config import config
from utils.restart import restart_api
from typing import Optional


logger: logging.Logger = logging.getLogger(name=__name__)

# Initialize router
router: APIRouter = APIRouter()
PREFIX: str = "/website"
TAGS: list[str] = ["website", "deployment"]

# Path to your website Git repository
REPO_PATH: str = "/var/www/html/ajholzer.net"

# Repo and venv path
VENV_PATH: str = "/var/www/venvs/api.ajholzer.net"
API_PATH: str = "/var/www/html/ajholzer.net/api"

COMMANDS: list[list[str]] = [
    ["git", "-C", REPO_PATH, "reset", "--hard", "HEAD"],
    ["git", "-C", REPO_PATH, "clean", "-fd"],
    ["git", "-C", REPO_PATH, "pull", "origin", "main"],
    [
        f"{VENV_PATH}/bin/pip3",
        "install",
        "-r",
        f"{API_PATH}/requirements.txt",
    ],
]


def run_update() -> None:
    """Updates the site data for ajholzer.net."""
    for command in COMMANDS:
        subprocess.run(
            args=command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


@router.post(path="/ajholzer.net/deploy", response_model=dict[str, str])
async def update_site(request: Request) -> dict[str, str]:
    """Updates the website hosted at ajholzer.net.

    Raises:
        HTTPException: When the update fails.

    Returns:
        dict[str, str]: When the update was successfully.
    """
    logger.debug("Attempting to update website and API hosted at ajholzer.net...")

    # Get the signature header from GitHub
    logger.debug("Getting signature from GitHub...")
    signature: Optional[str] = request.headers.get("X-Hub-Signature-256")
    if signature is None:
        logger.warning("Missing signature!")
        raise HTTPException(status_code=403, detail="Missing signature")

    # Read the raw body for signature verification
    body = await request.body()

    # Compute HMAC with the secret
    logger.debug("Computing secret using HMAC...")
    mac: hmac.HMAC = hmac.new(
        config.GITHUB_WEBSITE_SECRET,
        msg=body,
        digestmod=hashlib.sha256,
    )
    expected_signature: str = f"sha256={mac.hexdigest()}"

    # Compare the signature
    logger.debug("Comparing signature...")
    if not hmac.compare_digest(expected_signature, signature):
        logger.warning("Invalid signature!")
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Optional: check event type if you want
    logger.debug("Checking if event type matches PUSH event...")
    event_type: Optional[str] = request.headers.get("X-GitHub-Event")
    if event_type != "push":
        logger.warning("Not a PUSH event!")
        raise HTTPException(status_code=400, detail="Not a push event")

    try:
        logger.debug("Updating site data for ajholzer.net...")

        # Update local data
        await run_in_threadpool(run_update)

        # Restart api
        restart_api(delay=5)

        logger.debug("Site data updated for ajholzer.net.")

        return {
            "status": "success",
            "message": "Site updated",
        }
    except subprocess.CalledProcessError as exc:
        if exc.stdout:
            logger.error(exc.stdout.decode())
        if exc.stderr:
            logger.error(exc.stderr.decode())

        raise HTTPException(
            status_code=500,
            detail="Update failed",
        )
