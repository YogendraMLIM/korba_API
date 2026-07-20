import re
from datetime import date
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

NAME_PATTERN = r"^[A-Za-z .'-]+$"
MOBILE_PATTERN = r"^[6-9]\d{9}$"


class OccupierDetailsBase(BaseModel):

  
    occupier_name: str | None = Field(
        default=None,
        max_length=200
    )

    mobile_number: str | None = Field(
        default=None,
        min_length=10,
        max_length=10
    )

    occupancy_status: Literal[
        "Owner Occupied",
        "Tenant",
        "Vacant"
    ]

    tenant_since: date | None = None

    @field_validator("occupier_name")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            return value

        if not re.fullmatch(NAME_PATTERN, value):
            raise ValueError(
                "Only alphabets, spaces, '.', '-', and apostrophe are allowed."
            )
        return value

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, value):
        if value is None:
            return value

        if not re.fullmatch(MOBILE_PATTERN, value):
            raise ValueError("Invalid Indian mobile number.")

        return value

    @model_validator(mode="after")
    def validate_business_rules(self):

        if self.occupancy_status == "Tenant":

            if not self.occupier_name:
                raise ValueError(
                    "Occupier Name is required for Tenant."
                )

            if not self.mobile_number:
                raise ValueError(
                    "Mobile Number is required for Tenant."
                )

            if not self.tenant_since:
                raise ValueError(
                    "Tenant Since is required for Tenant."
                )

        return self


class OccupierDetailsCreate(OccupierDetailsBase):
    pass


class OccupierDetailsUpdate(BaseModel):

    occupier_name: str | None = None
    mobile_number: str | None = None
    occupancy_status: Literal[
        "Owner Occupied",
        "Tenant",
        "Vacant"
    ] | None = None
    tenant_since: date | None = None


class OccupierDetailsResponse(OccupierDetailsBase):

    id: int

    model_config = ConfigDict(from_attributes=True)