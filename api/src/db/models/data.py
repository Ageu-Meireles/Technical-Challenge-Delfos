from datetime import datetime

from sqlmodel import Field, SQLModel


class Data(SQLModel, table=True):
    timestamp: datetime = Field(primary_key=True, index=True)
    wind_speed: float
    power: float
    ambient_temperature: float
