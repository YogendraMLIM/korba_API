from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class SurveyorRemarks(Base, TimestampMixin):
    __tablename__ = "surveyor_remarks"

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

    surveyor_remarks: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    supervisor_remarks: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="surveyor_remarks"
    )
