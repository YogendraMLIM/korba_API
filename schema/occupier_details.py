import re
from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
)


class OccupierDetailsBase(BaseModel):

  
    occupier_name: str | None = None

    mobile_number: str | None = None

    occupancy_status: str

    tenant_since: date | None = None


class OccupierDetailsCreate(OccupierDetailsBase):
    pass


class OccupierDetailsUpdate(BaseModel):

    occupier_name: str | None = None
    mobile_number: str | None = None
    occupancy_status: str | None = None
    tenant_since: date | None = None


class OccupierDetailsResponse(OccupierDetailsBase):

    id: int

    model_config = ConfigDict(from_attributes=True)