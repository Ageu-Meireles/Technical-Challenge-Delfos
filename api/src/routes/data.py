from datetime import datetime
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from src.db import get_session
from src.db.models import Data

router = APIRouter(prefix="/data", tags=["data"])


@router.get("", response_model=List[Data])
async def get_data(
    start: datetime = Query(..., description="Start datetime (ISO 8601)"),
    end: datetime = Query(..., description="End datetime (ISO 8601)"),
    variables: Optional[
        List[Literal["wind_speed", "power", "ambient_temperature"]]
    ] = Query(
        None,
        description="Variables to include in the response (default: all)",
    ),
    session: Session = Depends(get_session),
):
    if start >= end:
        raise HTTPException(
            status_code=400,
            detail="start must be earlier than end",
        )

    statement = (
        select(Data)
        .where(
            Data.timestamp >= start,
            Data.timestamp <= end,
        )
        .order_by(Data.timestamp)
    )

    results = session.exec(statement).all()

    response = []

    include_wind_speed = variables is None or "wind_speed" in variables
    include_power = variables is None or "power" in variables
    include_ambient_temperature = (
        variables is None or "ambient_temperature" in variables
    )

    for row in results:
        item = {"timestamp": row.timestamp}

        if include_wind_speed:
            item["wind_speed"] = row.wind_speed

        if include_power:
            item["power"] = row.power

        if include_ambient_temperature:
            item["ambient_temperature"] = row.ambient_temperature

        response.append(item)

    return response
