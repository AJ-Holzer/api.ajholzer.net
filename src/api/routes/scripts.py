# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


import hashlib
import hmac
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, Response
from config.config import config
from typing import Optional
from pathlib import Path


router: APIRouter = APIRouter()
PREFIX: str = "/scripts"
TAGS: list[str] = ["scripts"]

script_cache: dict[str, tuple[float, bytes]] = {}


def verify_request(target: str, x_timestamp: str, x_signature: str) -> None:
    try:
        timestamp: int = int(x_timestamp)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp")

    now: int = int(time.time())
    if abs(now - timestamp) > config.API_MAX_TIME_DIFF:
        raise HTTPException(status_code=401, detail="Request expired")

    message: bytes = f"{timestamp}:{target}".encode()

    expected: str = hmac.new(
        config.API_UPLOAD_SECRET, message, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")


def load_script(name: str) -> bytes:
    global script_mtime, script_cache

    # Validate name
    if name not in config.API_SCRIPTS_ALLOWED:
        raise HTTPException(status_code=404, detail="Unknown target")

    # Get filepath
    filepath: Path = config.API_SCRIPTS_PATH / config.API_SCRIPTS_ALLOWED[name]

    # Check if filepath exists
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Script not configured")

    # Get cached script data
    mtime: float = filepath.stat().st_mtime
    cached: Optional[tuple[float, bytes]] = script_cache.get(name)

    # Return cached data if cached
    if cached and cached[0] == mtime:
        return cached[1]

    data = filepath.read_bytes()
    script_cache[name] = (mtime, data)

    return data


@router.get(path="/{target}", response_class=PlainTextResponse)
def get_script(target: str, x_timestamp: str, x_signature: str) -> Response:
    # Verify request
    verify_request(target=target, x_timestamp=x_timestamp, x_signature=x_signature)

    # Get script
    script: bytes = load_script(name=target)

    # Create mime
    mime: str = "text/plain" if target == "w" else "text/x-shellscript"

    return Response(
        content=script,
        media_type=mime,
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )
