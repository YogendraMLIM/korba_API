from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class UsageDetailsBase(BaseModel):

    primary_use: Literal[
        "Residential",
        "Commercial",
        "Industrial",
        "Institutional"
    ]

    mixed_use: bool

    commercial_activity: Literal[
        "Shop",
        "Office",
        "Hotel",
        "Clinic",
        "School",
        "Other"
    ] | None = None

    occupancy: Literal[
        "Self",
        "Tenant",
        "Vacant"
    ]

    number_of_families: int = Field(
        default=0,
        ge=0
    )

    number_of_shops: int = Field(
        default=0,
        ge=0
    )

    @model_validator(mode="after")
    def validate_usage(self):

        commercial_property = (
            self.primary_use == "Commercial"
            or self.mixed_use
        )

        if commercial_property:

            if self.commercial_activity is None:
                raise ValueError(
                    "Commercial Activity is required."
                )

            if self.number_of_shops <= 0:
                raise ValueError(
                    "Number of Shops is required."
                )

        else:
            self.number_of_shops = 0

        return self


class UsageDetailsCreate(UsageDetailsBase):
    pass


class UsageDetailsUpdate(BaseModel):

    primary_use: Literal[
        "Residential",
        "Commercial",
        "Industrial",
        "Institutional"
    ] | None = None

    mixed_use: bool | None = None

    commercial_activity: Literal[
        "Shop",
        "Office",
        "Hotel",
        "Clinic",
        "School",
        "Other"
    ] | None = None

    occupancy: Literal[
        "Self",
        "Tenant",
        "Vacant"
    ] | None = None

    number_of_families: int | None = Field(
        default=None,
        ge=0
    )

    number_of_shops: int | None = Field(
        default=None,
        ge=0
    )


class UsageDetailsResponse(UsageDetailsBase):

    id: int

    model_config = ConfigDict(from_attributes=True)