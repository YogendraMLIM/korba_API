from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class UsageDetailsBase(BaseModel):

    primary_use: str

    mixed_use: bool

    commercial_activity: str | None = None

    occupancy: str | None = None

    number_of_families: int | None = None

    number_of_shops: int | None = None


class UsageDetailsCreate(UsageDetailsBase):
    pass


class UsageDetailsUpdate(BaseModel):

    primary_use: str | None = None

    mixed_use: bool | None = None

    commercial_activity: str | None = None

    occupancy: str | None = None

    number_of_families: int | None = None

    number_of_shops: int | None = None


class UsageDetailsResponse(UsageDetailsBase):

    id: int

    model_config = ConfigDict(from_attributes=True)