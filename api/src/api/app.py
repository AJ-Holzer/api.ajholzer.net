# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


import importlib
import pkgutil
import uvicorn
import logging

from fastapi import FastAPI, APIRouter
from fastapi.params import Depends
from fastapi.datastructures import Default
from starlette.responses import Response, JSONResponse
from starlette.routing import BaseRoute
from typing import Optional, Sequence, Any
from enum import Enum
from config import config
from utils.paths import normalize_path


logger: logging.Logger = logging.getLogger(name=__name__)


class API:
    def __init__(self) -> None:
        """Initializes the API and registers all routes at api/routes."""
        logging.debug("Initializing API...")

        # Init FastAPI
        self.__api: FastAPI = FastAPI(
            title=config.API_TITLE,
            version=config.API_VERSION,
        )

        # Register routes
        self.__register_routes()

    def __register_routes(self) -> None:
        """Registers all routes in _api/routes/_"""
        logger.info("Registering routes...")
        import api.routes

        for module_info in pkgutil.iter_modules(api.routes.__path__):
            # Skip private modules
            if module_info.name.startswith("_"):
                continue

            # Import module from api/routes
            module = importlib.import_module(f"api.routes.{module_info.name}")

            # Get router from module
            router: Optional[APIRouter] = getattr(module, "router", None)

            # Skip if router is not specified
            if router is None:
                continue

            # Get route attributes
            prefix: str = normalize_path(
                path=f"{config.API_PREFIX}{getattr(module, 'PREFIX', '')}"
            )
            tags: Optional[list[str | Enum]] = getattr(module, "TAGS", None)
            dependencies: Optional[Sequence[Depends]] = getattr(
                module,
                "DEPENDENCIES",
                None,
            )
            responses: Optional[dict[int | str, dict[str, Any]]] = getattr(
                module,
                "RESPONSES",
                None,
            )
            deprecated: Optional[bool] = getattr(module, "DEPRECATED", None)
            include_in_schema: bool = getattr(module, "INCLUDE_IN_SCHEMA", True)
            default_response_class: type[Response] = getattr(
                module,
                "DEFAULT_RESPONSE_CLASS",
                Default(JSONResponse),
            )
            callbacks: Optional[list[BaseRoute]] = getattr(module, "CALLBACKS", None)

            # Add route to router
            self.__api.include_router(
                router=router,
                prefix=prefix,
                tags=tags,
                dependencies=dependencies,
                responses=responses,
                deprecated=deprecated,
                include_in_schema=include_in_schema,
                default_response_class=default_response_class,
                callbacks=callbacks,
            )

            # Log debug information
            logger.info("Registered route: '%s'", prefix)

    def start(self) -> None:
        """Starts the API."""
        # Log debug information
        logger.info("Starting API...")
        logger.debug(
            "Using: ip='%s', port=%d, auto-reload: %s",
            config.HOST_IP,
            config.HOST_PORT,
            config.RELOAD_API,
        )

        # Start api
        uvicorn.run(
            app=self.__api,
            host=config.HOST_IP,
            port=config.HOST_PORT,
            reload=config.RELOAD_API,
        )
