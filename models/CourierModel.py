from typing import List
from pydantic import BaseModel, StrictStr, StrictInt


class CourierModel(BaseModel):
    courier_id: StrictInt
    courier_type: StrictStr
    regions: List[StrictInt]
    working_hours: List[StrictStr]
