from pydantic import BaseModel, ConfigDict


class ParcelMasterBase(BaseModel):
    parcel_no: str
    property_id: str
    existing_property_id: str | None = None


class ParcelMasterCreate(ParcelMasterBase):
    pass


class ParcelMasterUpdate(BaseModel):
    parcel_no: str | None = None
    property_id: str | None = None
    existing_property_id: str | None = None
    is_active: bool | None = None


class ParcelMasterResponse(ParcelMasterBase):
    property_uid: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)