from datetime import date

from sqlalchemy import (
    String,
    Boolean,
    Date,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class TaxRelatedInformation(Base, TimestampMixin):
    __tablename__ = "tax_related_information"

    id: Mapped[int] = mapped_column(primary_key=True)

#     parcel_no: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         index=True
#     )
    
#     property_id: Mapped[str] = mapped_column(
#     ForeignKey("propertytax.parcel_master.property_id"),
#     nullable=False,
#     index=True
# )

    property_uid: Mapped[str] = mapped_column(
        ForeignKey("propertytax.parcel_master.property_uid"),
        nullable=False,
        index=True
    )


    existing_property_tax_no: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True
    )
    
    

    tax_paid_till: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    outstanding_tax: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False
    )

    exempted_property: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    exemption_category: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="tax_related_information"
    )
