from sqlalchemy import (
    Boolean,
    String,
    Integer,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class SmartAddressing(Base, TimestampMixin):
    __tablename__ = "smart_addressing"

    __table_args__ = (
        UniqueConstraint(
            name="uq_street_building_sequence",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # parcel_no: Mapped[str] = mapped_column(
    #     String(50),
    #     nullable=False,
    #     index=True,
    # )

    # property_id: Mapped[str] = mapped_column(
    #     ForeignKey("propertytax.parcel_master.property_id"),
    #     nullable=False,
    #     index=True,
    # )
    
    property_uid: Mapped[str] = mapped_column(
    ForeignKey("propertytax.parcel_master.property_uid"),
    nullable=False,
    index=True
)

    ddn_generated: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    ddn_sticker_affixed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    qr_code_affixed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    street_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    building_sequence_no: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="smart_addressing",
    )
