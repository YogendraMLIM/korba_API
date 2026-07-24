from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Integer,
    DateTime,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class SurveyInformation(Base, TimestampMixin):
    __tablename__ = "survey_information"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    
    parcel_no: Mapped[str] = mapped_column(
        String(50),
       nullable=True,
        index=True
    )
    
    property_id: Mapped[str] = mapped_column(
   nullable=True,
    index=True
)
    
    property_uid: Mapped[str] = mapped_column(
    ForeignKey("propertytax.parcel_master.property_uid"),
   nullable=True,
    index=True
)
    
    existing_property_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )
    
    
    property_location: Mapped[str] = mapped_column(
        String(100),
       nullable=True
    )
    
    tax_rate_zone: Mapped[str] = mapped_column(
        String(30),
        nullable=True
    )



    survey_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
       nullable=True,
        index=True
    )

    survey_date: Mapped[datetime] = mapped_column(
        DateTime,
       nullable=True
    )

    surveyor_name: Mapped[str] = mapped_column(
        String(150),
       nullable=True
    )

    surveyor_id: Mapped[str] = mapped_column(
        String(30),
       nullable=True
    )

    ward_no: Mapped[int] = mapped_column(
        Integer,  
        default=1,
       nullable=True)

    zone: Mapped[str] = mapped_column(
        String(50),
       nullable=True
    )

    colony_locality: Mapped[str] = mapped_column(
        String(150),
       nullable=True
    )

    street_road_name: Mapped[str] = mapped_column(
        String(150),
       nullable=True
    )

    lane_no: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

  

    digital_door_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    gps_latitude: Mapped[float] = mapped_column(
        Numeric(10, 7),
       nullable=True
    )

    gps_longitude: Mapped[float] = mapped_column(
        Numeric(10, 7),
       nullable=True
    )
    
    
       # Relationship
    parcel = relationship(
        "ParcelMaster",
        back_populates="survey_information"
    )
