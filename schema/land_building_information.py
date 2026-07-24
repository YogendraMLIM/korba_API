from datetime import date
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
)


class LandBuildingInformationBase(BaseModel):
    model_config = ConfigDict(extra="allow")

 
    plot_area: float

    ground_floor_area: float | None = None

    first_floor_area: float | None = None

    second_floor_area: float | None = None

    third_floor_area: float | None = None

    number_of_basement_levels: str | None = None

    basement_area_1: str | None = None

    basement_area_2: str | None = None

    basement_area_3: str | None = None

    basement_area_4: str | None = None

    basement_area_5: str | None = None

    floor_areas: dict[str, Any] | list[Any] | None = None

    basement_areas: dict[str, Any] | list[Any] | None = None

    number_of_floors: int

    year_of_construction: int | None = None
    
    total_builtup_area: float | None = None

    building_age: int | None = None

    construction_type: str

    roof_type: str


class LandBuildingInformationCreate(
    LandBuildingInformationBase
):
    pass


class LandBuildingInformationUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    plot_area: float | None = None
    ground_floor_area: float | None = None
    first_floor_area: float | None = None
    second_floor_area: float | None = None
    third_floor_area: float | None = None
    number_of_basement_levels: int | None = None
    basement_area_1: int | None = None
    basement_area_2: int | None = None
    basement_area_3: int | None = None
    basement_area_4: int | None = None
    basement_area_5: int | None = None
    floor_areas: dict[str, Any] | list[Any] | None = None
    basement_areas: dict[str, Any] | list[Any] | None = None
    number_of_floors: int | None = None
    year_of_construction: int | None = None
    total_builtup_area: float | None = None
    building_age: int | None = None
    construction_type: str | None = None
    roof_type: str | None = None


class LandBuildingInformationResponse(
    LandBuildingInformationBase
):

    id: int

    total_builtup_area: float

    building_age: int | None

    model_config = ConfigDict(from_attributes=True)
