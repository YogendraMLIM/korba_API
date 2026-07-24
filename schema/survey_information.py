from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class SurveyInformationBase(BaseModel):
    parcel_no: str
    survey_date: datetime
    surveyor_name: str| None = None
    tax_rate_zone: str | None = None
    property_location: str | None = None
    surveyor_id: str| None = None
    ward_no: int | None = None
    zone: str| None = None
    colony_locality: str| None = None
    street_road_name: str | None = None
    lane_no: str | None = None
    property_id: str | None = None
    existing_property_id: str | None = None
    digital_door_number: str | None = None
    gps_latitude: float
    gps_longitude: float


class SurveyInformationCreate(SurveyInformationBase):
    pass


class SurveyInformationUpdate(BaseModel):
    parcel_no: str | None = None
    property_id: str | None = None
    survey_date: datetime | None = None
    surveyor_name: str | None = None
    surveyor_id: str | None = None
    ward_no: int | None = None
    zone: str | None = None
    colony_locality: str | None = None
    street_road_name: str | None = None
    lane_no: str | None = None
    digital_door_number: str | None = None
    tax_rate_zone: str | None = None
    gps_latitude: float | None = None
    existing_property_id: str | None = None
    gps_longitude: float | None = None


class SurveyInformationResponse(SurveyInformationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
