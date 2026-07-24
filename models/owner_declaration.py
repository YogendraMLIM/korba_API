from datetime import datetime

from sqlalchemy import (
    Boolean,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class OwnerDeclaration(Base, TimestampMixin):
    __tablename__ = "owner_declaration"

    id: Mapped[int] = mapped_column(primary_key=True)

    # parcel_no: Mapped[str] = mapped_column(
    #     ForeignKey("parcel_master.parcel_no"),
    #    nullable=True,
    #     index=True
    # )
    
    # parcel_no: Mapped[str] = mapped_column(
    #     String(50),
    #    nullable=True,
    #     index=True
    # )
    
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


    owner_declaration_accepted: Mapped[bool] = mapped_column(
        Boolean,
       nullable=True
    )

    owner_signature: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    owner_refusal_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    surveyor_signature: Mapped[str] = mapped_column(
        String(500),
       nullable=True
    )

    declaration_date: Mapped[datetime] = mapped_column(
        DateTime,
       nullable=True,
        default=datetime.utcnow
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="owner_declaration"
    )
    
