from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class SurveyInformationBase(BaseModel):
    parcel_no: str = Field(..., max_length=100)
    survey_date: datetime
    surveyor_name: str = Field(..., max_length=150)
    tax_rate_zone: str | None = Field(default=None, max_length=30)
    property_location: str | None = Field(default=None, max_length=100)
    surveyor_id: str = Field(..., max_length=30)
    ward_no: str = Field(..., max_length=20)
    zone: str = Field(..., max_length=50)
    colony_locality: str = Field(..., max_length=150)
    street_road_name: str = Field(..., max_length=150)
    lane_no: str | None = Field(default=None, max_length=20)
    property_id: str | None = Field(default=None, max_length=50)
    existing_property_id: str | None = Field(default=None, max_length=50)
    digital_door_number: str | None = Field(default=None, max_length=50)
    gps_latitude: float = Field(..., ge=-90, le=90)
    gps_longitude: float = Field(..., ge=-180, le=180)

    @field_validator("ward_no", mode="before")
    @classmethod
    def normalize_ward_no(cls, value):
        if value is None:
            raise ValueError("ward_no is required")
        return str(value).strip()

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
    parcel_no: str | None = Field(default=None, max_length=100)
    property_id: str | None = Field(default=None, max_length=50)
    survey_date: datetime | None = None
    surveyor_name: str | None = Field(default=None, max_length=150)
    surveyor_id: str | None = Field(default=None, max_length=30)
    ward_no: str | None = Field(default=None, max_length=20)
    zone: str | None = Field(default=None, max_length=50)
    colony_locality: str | None = Field(default=None, max_length=150)
    street_road_name: str | None = Field(default=None, max_length=150)
    lane_no: str | None = Field(default=None, max_length=20)
    digital_door_number: str | None = Field(default=None, max_length=50)
    tax_rate_zone: str | None = Field(default=None, max_length=30)
    gps_latitude: float | None = Field(default=None, ge=-90, le=90)
    existing_property_id: str | None = Field(default=None, max_length=50)
    gps_longitude: float | None = Field(default=None, ge=-180, le=180)

    @field_validator("ward_no", mode="before")
    @classmethod
    def normalize_ward_no(cls, value):
        if value is None:
            return None
        return str(value).strip()


class SurveyInformationResponse(SurveyInformationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
