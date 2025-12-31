from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Signal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    data: list["Data"] = Relationship(back_populates="signal")


class Data(SQLModel, table=True):
    timestamp: datetime = Field(primary_key=True)
    signal_id: int = Field(foreign_key="signal.id", primary_key=True)
    value: float

    signal: Signal = Relationship(back_populates="data")
