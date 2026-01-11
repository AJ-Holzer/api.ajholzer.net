# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


import requests  # type: ignore[import-untyped]
import time
import logging

from config import config
from typing import Any, Optional
from integrations.github.types import GitHubRepository


logger: logging.Logger = logging.getLogger(name=__name__)


class GitHub:
    def __init__(self) -> None:
        """Initializes the GitHub class."""
        logger.debug(f"Initializing '{self.__class__.__name__}'...")
        self.__FETCH_REPO_HEADERS: dict[str, str] = {
            "Authorization": f"Bearer {config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }

        # Store last update time
        self.__last_updated: Optional[float] = None

        # Store repositories for the given interval
        self.__cached_repositories: list[GitHubRepository] = []

    def __fetch_repositories(self) -> list[GitHubRepository]:
        """Fetch all repositories, sort by creation date descending, then take the configured max number."""
        logger.debug("Fetching repositories from GitHub...")
        query: str = """
            {{
                user(login: "{github_username}") {{
                    repositories(first: 100,{cursor_query} isFork: false) {{
                        nodes {{
                            name
                            url
                            description
                            updatedAt
                            defaultBranchRef {{
                                target {{
                                    ... on Commit {{
                                        history {{
                                            totalCount
                                        }}
                                    }}
                                }}
                            }}
                        }}
                        pageInfo {{
                            hasNextPage
                            endCursor
                        }}
                    }}
                }}
            }}
        """

        all_repos: list[dict[str, Any]] = []
        has_next_page: bool = True
        end_cursor: Optional[str] = None

        # Paginate through all repos
        while has_next_page:
            # Update paged query with the new
            paged_query: str = query.format(
                github_username=config.GITHUB_USERNAME,
                cursor_query="",
            )

            if end_cursor:
                paged_query = query.format(
                    github_username=config.GITHUB_USERNAME,
                    cursor_query=f'after: "{end_cursor}"',
                )

            # Fetch repos using graphql
            response: requests.Response = requests.post(
                "https://api.github.com/graphql",
                json={"query": paged_query},
                headers=self.__FETCH_REPO_HEADERS,
            )
            response.raise_for_status()

            # Convert the response to json and select the repos
            data: dict[str, Any] = response.json()["data"]["user"]["repositories"]

            # Get next page cursor
            has_next_page = data["pageInfo"]["hasNextPage"]
            end_cursor = data["pageInfo"]["endCursor"]

            # Add repos to all repos
            all_repos.extend(data["nodes"])

        # Sort all repos by creation date descending
        all_repos_sorted: list[dict[str, Any]] = sorted(
            all_repos, key=lambda r: r["updatedAt"], reverse=True
        )

        # Take only the configured max number of repos
        selected_repos: list[dict[str, Any]] = all_repos_sorted[
            : config.GITHUB_MAX_REPOS :
        ]

        # Convert repos to GitHubRepository dataclasses and add them to the list
        repositories: list[GitHubRepository] = []
        for repo in selected_repos:
            # Get commit count of the current repo
            commit_count: int = (
                repo.get("defaultBranchRef", {})
                .get("target", {})
                .get("history", {})
                .get("totalCount", 0)
            )

            # Add github repo to repos
            repositories.append(
                GitHubRepository(
                    url=repo["url"],
                    name=repo["name"],
                    description=repo.get("description", ""),
                    commit_count=commit_count,
                )
            )

        return repositories

    @property
    def repositories(self) -> list[GitHubRepository]:
        """Returns the most resent repositories within the interval.

        Returns:
            list[GitHubRepository]: The GitHub repositories.
        """
        logger.debug("Getting GitHub repositories...")

        # Get current time in seconds since the last epoch
        current_time: float = time.time()

        # Skip if repositories don't need to be updated (use cached repositories)
        if (
            self.__last_updated is not None
            and self.__last_updated + config.REPOSITORY_EXPIRATION_INTERVAL_MINUTES * 60
            > current_time
            and self.__cached_repositories
        ):
            logger.debug(
                "Using cached repositories as they are still cached for %.2f seconds...",
                self.__last_updated
                + config.REPOSITORY_EXPIRATION_INTERVAL_MINUTES * 60
                - current_time,
            )
            return self.__cached_repositories

        # Update cached repositories
        logger.debug("Updating cached GitHub repositories...")
        self.__cached_repositories = self.__fetch_repositories()

        # Update last update time
        self.__last_updated = current_time

        return self.__cached_repositories
