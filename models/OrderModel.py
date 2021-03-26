from typing import List
from datetime import datetime

from pydantic import BaseModel, StrictStr, StrictInt, Field


class OrderModel(BaseModel):
    order_id: StrictInt
    weight: float = Field(gt=0.01, lt=50.0)
    region: StrictInt
    delivery_hours: List[StrictStr]


class OrderCompleteModel(BaseModel):
    courier_id: StrictInt
    order_id: StrictInt
    complete_time: datetime
