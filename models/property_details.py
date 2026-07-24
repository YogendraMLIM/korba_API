from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class PropertyDetails(Base, TimestampMixin):
    __tablename__ = "property_details"

    id: Mapped[int] = mapped_column(primary_key=True)

    # parcel_no: Mapped[str] = mapped_column(
    #     String(50),
    #    nullable=True,
    #     index=True
    # )
    
    # property_id: Mapped[str] = mapped_column(
    # ForeignKey("propertytax.parcel_master.property_id"),
    #nullable=True,
    # index=True
    # )
    
    property_uid: Mapped[str] = mapped_column(
    ForeignKey("propertytax.parcel_master.property_uid"),
   nullable=True,
    index=True
)


    property_type: Mapped[str] = mapped_column(
        String(30),
       nullable=True
    )

    property_status: Mapped[str] = mapped_column(
        String(30),
       nullable=True
    )

    building_permission_available: Mapped[bool] = mapped_column(
        Boolean,
       nullable=True
    )

    property_ownership: Mapped[str] = mapped_column(
        String(30),
       nullable=True
    )
    
   

    parcel = relationship(
        "ParcelMaster",
        back_populates="property_details"
    )
