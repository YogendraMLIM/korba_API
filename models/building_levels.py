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

class BuildingLevel(Base):
    __tablename__ = "building_levels"

    id: Mapped[int] = mapped_column(primary_key=True)

    property_uid: Mapped[str] = mapped_column(
        ForeignKey("propertytax.parcel_master.property_uid"),
        nullable=False,
        index=True
    )

    level_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    # Basement / Floor

    level_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    area: Mapped[float] = mapped_column(
        Numeric(12,2),
        nullable=False
    )

    building = relationship(
        "ParcelMaster",
        back_populates="building_levels"
    )