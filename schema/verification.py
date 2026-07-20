from pydantic import BaseModel, ConfigDict


class VerificationBase(BaseModel):


    unassessed_property: bool

    under_assessed_property: bool

    property_use_changed: bool

    additional_floor_constructed: bool

    boundary_changed: bool

    ownership_changed: bool

    demolished_property: bool

    new_property: bool


class VerificationCreate(VerificationBase):
    pass


class VerificationUpdate(BaseModel):

    unassessed_property: bool | None = None
    under_assessed_property: bool | None = None
    property_use_changed: bool | None = None
    additional_floor_constructed: bool | None = None
    boundary_changed: bool | None = None
    ownership_changed: bool | None = None
    demolished_property: bool | None = None
    new_property: bool | None = None


class VerificationResponse(VerificationBase):

    id: int

    model_config = ConfigDict(
        from_attributes=True
    )