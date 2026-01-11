# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


import re


def normalize_path(path: str) -> str:
    path = re.sub(r"/+", "/", path)
    path = "/" + path.lstrip("/")
    return path.rstrip("/") or "/"
