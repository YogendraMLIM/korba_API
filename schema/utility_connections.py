import re

from pydantic import (
    BaseModel,
    ConfigDict,
)


class UtilityConnectionsBase(BaseModel):


    water_connection_no: str | None = None

    is_water_connection: str | None = None
    

    sewer_connection: bool | None = None

    is_electricity_connection: bool | None = None
    
    electricity_consumer_no: str | None = None

    gas_connection: bool | None = None
    
    gas_connection_no: str | None = None

    trade_license_no: str | None = None

    factory_license_no: str | None = None


class UtilityConnectionsCreate(UtilityConnectionsBase):
    pass


class UtilityConnectionsUpdate(BaseModel):

    water_connection_no: str | None = None
    is_water_connection: str | None = None
    gas_connection_no: str | None = None
    is_electricity_connection: bool | None = None
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