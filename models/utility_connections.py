from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class UtilityConnections(Base, TimestampMixin):
    __tablename__ = "utility_connections"

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


    water_connection_no: Mapped[str | None] = mapped_column(
        String(30),
        unique=True,
        nullable=True,
        default=None
    )

    is_water_connection: Mapped[str | None] = mapped_column(
        String(30),
        unique=True,
        nullable=True,
        default=None
    )

    sewer_connection: Mapped[bool] = mapped_column(
        Boolean,
       nullable=True
    )
    
    is_electricity_connection: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=None
    )

    electricity_consumer_no: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    gas_connection: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
       nullable=True
    )
    
    gas_connection_no: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    trade_license_no: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    factory_license_no: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="utility_connections"
    )
