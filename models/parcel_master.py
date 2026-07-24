from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class ParcelMaster(Base, TimestampMixin):
    __tablename__ = "parcel_master"

    # Combined Unique ID
    property_uid: Mapped[str] = mapped_column(
        String(120),
        primary_key=True,
        index=True
    )

    parcel_no: Mapped[str] = mapped_column(
        String(50),
       nullable=True,
        index=True
    )
    
    existing_property_id: Mapped[str | None] = mapped_column(
            String(50),
            nullable=True,
            index=True
        )

    property_id: Mapped[str] = mapped_column(
        String(50),
       nullable=True,
        index=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
       nullable=True
    )

    # Relationships
    survey_information = relationship(
        "SurveyInformation",
        back_populates="parcel",
        cascade="all, delete-orphan",
     
        uselist=False
    )

    owner_details = relationship(
        "OwnerDetails",
        back_populates="parcel",
        cascade="all, delete-orphan",

        uselist=False
    )

    occupier_details = relationship(
        "OccupierDetails",
        back_populates="parcel",
        cascade="all, delete-orphan",
        uselist=False
    )

    property_details = relationship(
        "PropertyDetails",
        back_populates="parcel",
        cascade="all, delete-orphan",
     
        uselist=False
    )

    land_building_information = relationship(
        "LandBuildingInformation",
        back_populates="parcel",
        cascade="all, delete-orphan",
        uselist=False
    )

    land_building_areas = relationship(
        "LandBuildingArea",
        back_populates="parcel",
        cascade="all, delete-orphan"
    )

    usage_details = relationship(
        "UsageDetails",
        back_populates="parcel",
        cascade="all, delete-orphan",
        uselist=False
    )

    tax_related_information = relationship(
        "TaxRelatedInformation",
        back_populates="parcel",
        cascade="all, delete-orphan",
        uselist=False
    )

    utility_connections = relationship(
        "UtilityConnections",
        back_populates="parcel",
        cascade="all, delete-orphan",
        uselist=False
    )

    gis_information = relationship(
        "GISInformation",
        back_populates="parcel",
        cascade="all, delete-orphan",
        uselist=False
    )

    smart_addressing = relationship(
        "SmartAddressing",
        back_populates="parcel",
        cascade="all, delete-orphan",
        uselist=False
    )

    verification = relationship(
        "Verification",
        back_populates="parcel",
        cascade="all, delete-orphan",
        uselist=False
    )

    documents_collected = relationship(
        "DocumentsCollected",
        back_populates="parcel",
        cascade="all, delete-orphan",
        uselist=False
    )

    surveyor_remarks = relationship(
        "SurveyorRemarks",
        back_populates="parcel",
        cascade="all, delete-orphan",
        uselist=False
    )

    owner_declaration = relationship(
        "OwnerDeclaration",
        back_populates="parcel",
        cascade="all, delete-orphan",
        uselist=False
    )
