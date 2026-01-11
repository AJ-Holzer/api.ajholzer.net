# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


from dataclasses import dataclass
from typing import Optional


@dataclass
class GitHubRepository:
    url: str
    name: str
    description: Optional[str]
    commit_count: int
