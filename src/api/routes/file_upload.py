# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


import hashlib
import hmac
import logging
import time

from fastapi import APIRouter, File, UploadFile, Header, HTTPException
from pathlib import Path
from pathlib import Path
from config.config import config


logger: logging.Logger = logging.getLogger(__name__)

# Initialize router
router: APIRouter = APIRouter()
PREFIX: str = "/data"
TAGS: list[str] = ["data", "upload"]

# Set directories
UPLOAD_DIR: Path = Path("/home/ghdeploy/uploads")
MAX_TIME_DIFF: int = 60  # In seconds

# Create upload dir if not exists
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post(path="/upload", response_model=dict[str, str])
async def list_repositories(
    file: UploadFile = File(...),
    x_timestamp: str = Header(...),
    x_signature: str = Header(...),
) -> dict[str, str]:
    # Validate timestamp format
    try:
        timestamp: int = int(x_timestamp)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp")

    # Replay protection
    now: int = int(time.time())
    if abs(now - timestamp) > MAX_TIME_DIFF:
        raise HTTPException(status_code=401, detail="Request expired")

    # Read file content
    content: bytes = await file.read()

    # Compute file hash
    file_hash: str = hashlib.sha256(content).hexdigest()

    # Recreate signed message
    message: bytes = f"{timestamp}:{file_hash}".encode()

    # Compute expected hmac
    expected_signature: str = hmac.new(
        config.API_UPLOAD_SECRET, message, hashlib.sha256
    ).hexdigest()

    # Constant time comparison
    if not hmac.compare_digest(expected_signature, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Save file safely
    safe_filename: str = Path(str(file.filename)).name
    save_path: Path = UPLOAD_DIR / safe_filename

    save_path.write_bytes(content)

    return {"status": "Upload successful"}
