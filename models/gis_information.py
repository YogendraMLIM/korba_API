
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class GISInformation(Base, TimestampMixin):
    __tablename__ = "gis_information"

    id: Mapped[int] = mapped_column(primary_key=True)

    parcel_no: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    
    property_id: Mapped[str] = mapped_column(
    ForeignKey("propertytax.parcel_master.property_id"),
    nullable=False,
    index=True
)


    gis_property_polygon_available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    property_boundary_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    geo_tag_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    property_photo_captured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    front_elevation_photo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    name_plate_photo: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="gis_information"
    )