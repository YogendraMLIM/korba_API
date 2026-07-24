from pydantic import BaseModel, ConfigDict, Field


class PropertyDetailsBase(BaseModel):


    property_type: str

    property_status: str

    building_permission_available: bool

    property_ownership: str
    


class PropertyDetailsCreate(PropertyDetailsBase):
    pass


class PropertyDetailsUpdate(BaseModel):

    property_type: str | None = None

    property_status: str | None = None

    building_permission_available: bool | None = None

    property_ownership: str | None = None
    


class PropertyDetailsResponse(PropertyDetailsBase):

    id: int

    model_config = ConfigDict(from_attributes=True)