from datetime import date
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class LandBuildingInformationBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

 
    plot_area: float = Field(..., gt=0)

    ground_floor_area: float | None = Field(default=0, ge=0)

    first_floor_area: float | None = Field(default=0, ge=0)

    second_floor_area: float | None = Field(default=0, ge=0)

    third_floor_area: float | None = Field(default=0, ge=0)

    number_of_basement_levels: int | None = Field(
        default=None,
        ge=0,
        le=5,
        alias="numberOfBasementLevels",
    )

    basement_area_1: float | None = Field(
        default=None,
        ge=0,
        alias="basementArea1",
    )

    basement_area_2: float | None = Field(
        default=None,
        ge=0,
        alias="basementArea2",
    )

    basement_area_3: float | None = Field(
        default=None,
        ge=0,
        alias="basementArea3",
    )

    basement_area_4: float | None = Field(
        default=None,
        ge=0,
        alias="basementArea4",
    )

    basement_area_5: float | None = Field(
        default=None,
        ge=0,
        alias="basementArea5",
    )

    number_of_floors: int = Field(..., ge=0, le=99)

    year_of_construction: int | None = None
    
    total_builtup_area: float = Field(default=0, ge=0)

    building_age: int | None = None

    construction_type: Literal[
        "Kutcha",
        "Semi Pucca",
        "Pucca"
    ]

    roof_type: Literal[
        "RCC",
        "Tin",
        "Tile",
        "Other"
    ]

    @field_validator(
        "number_of_basement_levels",
        "basement_area_1",
        "basement_area_2",
        "basement_area_3",
        "basement_area_4",
        "basement_area_5",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value):
        if value == "":
            return None
        return value

    @model_validator(mode="after")
    def validate_building(self):

        current_year = date.today().year

        total = (
            (self.ground_floor_area or 0)
            + (self.first_floor_area or 0)
            + (self.second_floor_area or 0)
            + (self.third_floor_area or 0)
        )

        if total > self.plot_area:
            raise ValueError(
                "Total built-up area cannot exceed plot area."
            )

        floor_count = sum([
            self.ground_floor_area > 0 if self.ground_floor_area else False,
            self.first_floor_area > 0 if self.first_floor_area else False,
            self.second_floor_area > 0 if self.second_floor_area else False,
            self.third_floor_area > 0 if self.third_floor_area else False,
        ])

        if floor_count != self.number_of_floors:
            raise ValueError(
                "Number of floors does not match entered floor areas."
            )

        if (
            self.year_of_construction
            and self.year_of_construction > current_year
        ):
            raise ValueError(
                "Year of construction cannot be in the future."
            )

        return self


class LandBuildingInformationCreate(
    LandBuildingInformationBase
):
    pass


class LandBuildingInformationUpdate(BaseModel):

    plot_area: float | None = None
    ground_floor_area: float | None = None
    first_floor_area: float | None = None
    second_floor_area: float | None = None
    third_floor_area: float | None = None
    number_of_basement_levels: int | None = Field(
        default=None,
        ge=0,
        le=5,
        alias="numberOfBasementLevels",
    )
    basement_area_1: float | None = Field(
        default=None,
        ge=0,
        alias="basementArea1",
    )
    basement_area_2: float | None = Field(
        default=None,
        ge=0,
        alias="basementArea2",
    )
    basement_area_3: float | None = Field(
        default=None,
        ge=0,
        alias="basementArea3",
    )
    basement_area_4: float | None = Field(
        default=None,
        ge=0,
        alias="basementArea4",
    )
    basement_area_5: float | None = Field(
        default=None,
        ge=0,
        alias="basementArea5",
    )
    number_of_floors: int | None = None
    year_of_construction: int | None = None
    total_builtup_area: float | None = None
    building_age: int | None = None
    construction_type: Literal[
        "Kutcha",
        "Semi Pucca",
        "Pucca"
    ] | None = None
    roof_type: Literal[
        "RCC",
        "Tin",
        "Tile",
        "Other"
    ] | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "number_of_basement_levels",
        "basement_area_1",
        "basement_area_2",
        "basement_area_3",
        "basement_area_4",
        "basement_area_5",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value):
        if value == "":
            return None
        return value


class LandBuildingInformationResponse(
    LandBuildingInformationBase
):

    id: int

    total_builtup_area: float

    building_age: int | None

    model_config = ConfigDict(from_attributes=True)
