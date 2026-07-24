from pydantic import (
    BaseModel,
    ConfigDict,
)


class SmartAddressingBase(BaseModel):
    ddn_generated: bool | None = None
    ddn_sticker_affixed: bool | None = None
    qr_code_affixed: bool | None = None
    street_code: str | None = None
    building_sequence_no: int | None = None


class SmartAddressingCreate(SmartAddressingBase):
    pass


class SmartAddressingUpdate(SmartAddressingBase):
    pass


class SmartAddressingResponse(BaseModel):
    id: int | None = None
    ddn_generated: bool | None = None
    ddn_sticker_affixed: bool | None = None
    qr_code_affixed: bool | None = None
    street_code: str | None = None
    building_sequence_no: int | None = None

    model_config = ConfigDict(from_attributes=True)