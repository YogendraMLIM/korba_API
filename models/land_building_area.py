from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class LandBuildingArea(Base, TimestampMixin):
    __tablename__ = "land_building_area"

    id: Mapped[int] = mapped_column(primary_key=True)

    property_uid: Mapped[str] = mapped_column(
        ForeignKey("propertytax.parcel_master.property_uid"),
       nullable=True,
        index=True
    )

    surveyor_id: Mapped[str] = mapped_column(
        String(30),
       nullable=True,
        index=True
    )

    area_type: Mapped[str] = mapped_column(
        String(20),
       nullable=True,
        index=True
    )

    level_no: Mapped[int] = mapped_column(
        Integer,
       nullable=True
    )

    level_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    area: Mapped[str] = mapped_column(
        Text,
       nullable=True
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="land_building_areas"
    )
