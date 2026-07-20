from pydantic import BaseModel, ConfigDict


class GISInformationBase(BaseModel):

    

    gis_property_polygon_available: bool

    property_boundary_verified: bool

    geo_tag_completed: bool

    property_photo_captured: bool

    front_elevation_photo: bool

    name_plate_photo: bool = False


class GISInformationCreate(GISInformationBase):
    pass


class GISInformationUpdate(BaseModel):

    gis_property_polygon_available: bool | None = None

    property_boundary_verified: bool | None = None

    geo_tag_completed: bool | None = None

    property_photo_captured: bool | None = None

    front_elevation_photo: bool | None = None

    name_plate_photo: bool | None = None


class GISInformationResponse(GISInformationBase):

    id: int

    model_config = ConfigDict(
        from_attributes=True
    )