import re

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


ALPHANUMERIC_PATTERN = r"^[A-Za-z0-9\-]+$"


class UtilityConnectionsBase(BaseModel):


    water_connection_no: str | None = Field(
        default=None,
        max_length=30
    )

    sewer_connection: bool

    electricity_consumer_no: str | None = Field(
        default=None,
        max_length=30
    )

    gas_connection: bool = False

    trade_license_no: str | None = Field(
        default=None,
        max_length=30
    )

    factory_license_no: str | None = Field(
        default=None,
        max_length=30
    )

    @field_validator(
        "water_connection_no",
        "electricity_consumer_no",
        "trade_license_no",
        "factory_license_no"
    )
    @classmethod
    def validate_alphanumeric(cls, value):

        if value is None:
            return value

        if not re.fullmatch(ALPHANUMERIC_PATTERN, value):
            raise ValueError(
                "Only letters, numbers and '-' are allowed."
            )

        return value


class UtilityConnectionsCreate(UtilityConnectionsBase):
    pass


class UtilityConnectionsUpdate(BaseModel):

    water_connection_no: str | None = None
    sewer_connection: bool | None = None
    electricity_consumer_no: str | None = None
    gas_connection: bool | None = None
    trade_license_no: str | None = None
    factory_license_no: str | None = None


class UtilityConnectionsResponse(
    UtilityConnectionsBase
):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )