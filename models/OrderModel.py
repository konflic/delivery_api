from typing import List
from pydantic import BaseModel, StrictStr, StrictInt, StrictFloat, Field


class OrderModel(BaseModel):
    order_id: StrictInt
    weight: float = Field(gt=0.01, lt=50.0)
    region: StrictInt
    delivery_hours: List[StrictStr]
