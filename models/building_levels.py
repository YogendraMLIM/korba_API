from sqlalchemy import (
    ForeignKey,
    Integer,
    Numeric,
    String
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from core.database import Base

class BuildingLevel(Base):
    __tablename__ = "building_levels"

    id: Mapped[int] = mapped_column(primary_key=True)

    property_uid: Mapped[str] = mapped_column(
        ForeignKey("propertytax.parcel_master.property_uid"),
       nullable=True,
        index=True
    )

    level_type: Mapped[str] = mapped_column(
        String(20),
       nullable=True
    )
    # Basement / Floor

    level_no: Mapped[int] = mapped_column(
        Integer,
       nullable=True
    )

    area: Mapped[float] = mapped_column(
        Numeric(12,2),
       nullable=True
    )

    building = relationship(
        "ParcelMaster",
        back_populates="building_levels"
    )
