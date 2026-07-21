from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PropertyDetailsBase(BaseModel):


    property_type: Literal[
        "Residential",
        "Commercial",
        "Mixed",
        "Industrial",
        "Institutional",
        "Government",
        "Vacant Land"
    ]

    property_status: Literal[
        "Existing",
        "New Construction",
        "Under Construction"
    ]

    building_permission_available: bool

    property_ownership: Literal[
        "Freehold",
        "Leasehold",
        "Government"
    ]
    


class PropertyDetailsCreate(PropertyDetailsBase):
    pass


class PropertyDetailsUpdate(BaseModel):

    property_type: Literal[
        "Residential",
        "Commercial",
        "Mixed",
        "Industrial",
        "Institutional",
        "Government",
        "Vacant Land"
    ] | None = None

    property_status: Literal[
        "Existing",
        "New Construction",
        "Under Construction"
    ] | None = None

    building_permission_available: bool | None = None

    property_ownership: Literal[
        "Freehold",
        "Leasehold",
        "Government"
    ] | None = None
    


class PropertyDetailsResponse(PropertyDetailsBase):

    id: int

    model_config = ConfigDict(from_attributes=True)