from pydantic import BaseModel, ConfigDict, Field


class ParcelMasterBase(BaseModel):
    parcel_no: str = Field(..., max_length=50)
    property_id: str = Field(..., max_length=50)


class ParcelMasterCreate(ParcelMasterBase):
    pass


class ParcelMasterUpdate(BaseModel):
    parcel_no: str | None = Field(None, max_length=50)
    property_id: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class ParcelMasterResponse(ParcelMasterBase):
    property_uid: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)