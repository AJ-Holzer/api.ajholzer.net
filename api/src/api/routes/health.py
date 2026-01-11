# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


from fastapi import APIRouter
from api.models import HealthModel


router: APIRouter = APIRouter()
PREFIX: str = "/health"
TAGS: list[str] = ["health"]


@router.get(path="", response_model=HealthModel)
def get_health() -> HealthModel:
    return HealthModel(status="OK")
