from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class UsageDetails(Base, TimestampMixin):
    __tablename__ = "usage_details"

    id: Mapped[int] = mapped_column(primary_key=True)

#     parcel_no: Mapped[str] = mapped_column(
#         String(50),
#        nullable=True,
#         index=True
#     )
    
#     property_id: Mapped[str] = mapped_column(
#     ForeignKey("propertytax.parcel_master.property_id"),
#    nullable=True,
#     index=True
# )

    property_uid: Mapped[str] = mapped_column(
        ForeignKey("propertytax.parcel_master.property_uid"),
       nullable=True,
        index=True
    )


    primary_use: Mapped[str] = mapped_column(
        String(30),
       nullable=True
    )

    mixed_use: Mapped[bool] = mapped_column(
        Boolean,
       nullable=True
    )

    commercial_activity: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    occupancy: Mapped[str] = mapped_column(
        String(20),
       nullable=True
    )

    number_of_families: Mapped[int] = mapped_column(
        Integer,
        default=0,
       nullable=True
    )

    number_of_shops: Mapped[int] = mapped_column(
        Integer,
        default=0,
       nullable=True
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="usage_details"
    )
