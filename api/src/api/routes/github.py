# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


import logging

from fastapi import APIRouter
from api.models import GitHubRepositoryModel
from integrations.github.github_interface import GitHub


logger: logging.Logger = logging.getLogger(__name__)

# Initialize router
router: APIRouter = APIRouter()
PREFIX: str = "/github"
TAGS: list[str] = ["github"]

# Initialize github
github: GitHub = GitHub()


@router.get(path="/repositories", response_model=list[GitHubRepositoryModel])
def list_repositories() -> list[GitHubRepositoryModel]:
    """Get GitHub repositories.

    Returns:
        list[Repository]: The GitHub repositories.
    """
    logger.debug("Retrieving GitHub repositories...")
    return [
        GitHubRepositoryModel(
            url=repository.url,
            name=repository.name,
            description=repository.description or "",
            commit_count=repository.commit_count,
        )
        for repository in github.repositories
    ]
