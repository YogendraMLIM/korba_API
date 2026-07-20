from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class OwnerDetails(Base, TimestampMixin):
    __tablename__ = "owner_details"

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


    owner_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    father_husband_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    mobile_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    alternate_mobile: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    aadhaar_no: Mapped[str | None] = mapped_column(
        String(12),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    correspondence_address: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="owner_details"
    )