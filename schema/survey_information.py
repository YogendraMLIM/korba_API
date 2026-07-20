from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
)


class SurveyInformationBase(BaseModel):
    # survey_id: str = Field(..., max_length=50)

    parcel_no: str = Field(..., max_length=100)

    survey_date: datetime

    surveyor_name: str = Field(..., max_length=150)
   
    surveyor_id: str = Field(..., max_length=30)

    ward_no: str = Field(..., max_length=20)

    zone: str = Field(..., max_length=50)

    colony_locality: str = Field(..., max_length=150)

    street_road_name: str = Field(..., max_length=150)

    lane_no: str | None = Field(default=None, max_length=20)

    property_id: str | None = Field(
        default=None,
        max_length=50
    )
    
    existing_property_id: str | None = Field(default=None, max_length=50)

    digital_door_number: str | None = Field(
        default=None,
        max_length=50
    )

    gps_latitude: float = Field(
        ...,
        ge=-90,
        le=90
    )

    gps_longitude: float = Field(
        ...,
        ge=-180,
        le=180
    )

    @field_validator("surveyor_name")
    @classmethod
    def validate_name(cls, value):
        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Surveyor name should contain only alphabets and spaces."
            )
        return value


class SurveyInformationCreate(SurveyInformationBase):
    pass


class SurveyInformationUpdate(BaseModel):

    parcel_no: str | None = None
    property_id: str | None = None
    survey_date: datetime | None = None
    surveyor_name: str | None = None
    surveyor_id: str | None = None
    ward_no: str = Field(..., max_length=20)
    zone: str | None = None
    colony_locality: str | None = None
    street_road_name: str | None = None
    lane_no: str | None = None
    digital_door_number: str | None = None
    gps_latitude: float | None = None
    existing_property_id: str | None = None
    gps_longitude: float | None = None


class SurveyInformationResponse(SurveyInformationBase):

    id: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)