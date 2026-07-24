from datetime import date

from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class OccupierDetails(Base, TimestampMixin):
    __tablename__ = "occupier_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_uid: Mapped[str] = mapped_column(
        ForeignKey("propertytax.parcel_master.property_uid"),
       nullable=True,
        index=True
)


    occupier_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    mobile_number: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    occupancy_status: Mapped[str] = mapped_column(
        String(20),
       nullable=True
    )

    tenant_since: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="occupier_details"
    )
