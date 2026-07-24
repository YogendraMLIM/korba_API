# from sqlalchemy import String, ForeignKey
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from core.database import Base
# from models.base import TimestampMixin


# class DocumentsCollected(Base, TimestampMixin):
#     __tablename__ = "documents_collected"

#     id: Mapped[int] = mapped_column(primary_key=True)

#     parcel_no: Mapped[str] = mapped_column(
#         String(50),
#        nullable=True,
#         index=True
#     )
    
# #     property_id: Mapped[str] = mapped_column(
# #     ForeignKey("propertytax.parcel_master.property_id"),
# #    nullable=True,
# #     index=True
# # )

#     property_uid: Mapped[str] = mapped_column(
#         ForeignKey("propertytax.parcel_master.property_uid"),
#        nullable=True,
#         index=True
#     )


#     aadhaar_copy: Mapped[str | None] = mapped_column(
#         String(500),
#         nullable=True
#     )

#     electricity_bill: Mapped[str | None] = mapped_column(
#         String(500),
#         nullable=True
#     )

#     water_bill: Mapped[str | None] = mapped_column(
#         String(500),
#         nullable=True
#     )

#     sale_deed: Mapped[str | None] = mapped_column(
#         String(500),
#         nullable=True
#     )

#     property_tax_receipt: Mapped[str | None] = mapped_column(
#         String(500),
#         nullable=True
#     )

#     building_permission: Mapped[str | None] = mapped_column(
#         String(500),
#         nullable=True
#     )

#     other_documents: Mapped[str | None] = mapped_column(
#         String(500),
#         nullable=True
#     )

#     parcel = relationship(
#         "ParcelMaster",
#         back_populates="documents_collected"
#     )


from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class DocumentsCollected(Base, TimestampMixin):
    __tablename__ = "documents_collected"

    id: Mapped[int] = mapped_column(primary_key=True)

    property_uid: Mapped[str] = mapped_column(
        ForeignKey("propertytax.parcel_master.property_uid"),
       nullable=True,
        index=True
    )

    document_type: Mapped[str] = mapped_column(
        String(100),
       nullable=True,
        index=True
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
       nullable=True
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="documents_collected"
    )