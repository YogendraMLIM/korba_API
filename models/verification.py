from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class Verification(Base, TimestampMixin):
    __tablename__ = "verification"

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


    unassessed_property: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    under_assessed_property: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    property_use_changed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    additional_floor_constructed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    boundary_changed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    ownership_changed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    demolished_property: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    new_property: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="verification"
    )