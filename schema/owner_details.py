import re

from pydantic import (
    BaseModel,
    ConfigDict,
)


class OwnerDetailsBase(BaseModel):

    owner_name: str

    father_husband_name: str

    mobile_number: str

    alternate_mobile: str | None = None

    aadhaar_no: str | None = None

    email: str | None = None

    correspondence_address: str


class OwnerDetailsCreate(OwnerDetailsBase):
    pass


class OwnerDetailsUpdate(BaseModel):

    owner_name: str | None = None
    father_husband_name: str | None = None
    mobile_number: str | None = None
    alternate_mobile: str | None = None
    aadhaar_no: str | None = None
    email: str | None = None
    correspondence_address: str | None = None


class OwnerDetailsResponse(OwnerDetailsBase):

    id: int

    model_config = ConfigDict(from_attributes=True)