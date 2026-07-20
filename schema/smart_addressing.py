from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class SmartAddressingBase(BaseModel):
    ddn_generated: bool | None = None
    ddn_sticker_affixed: bool | None = None
    qr_code_affixed: bool | None = None
    street_code: str | None = Field(default=None, max_length=20)
    building_sequence_no: int | None = Field(
        default=None,
        ge=1,
        le=9999
    )


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