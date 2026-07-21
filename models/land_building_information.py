from sqlalchemy import String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class LandBuildingInformation(Base, TimestampMixin):
    __tablename__ = "land_building_information"

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


    plot_area: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    ground_floor_area: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    first_floor_area: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    second_floor_area: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    third_floor_area: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    number_of_basement_levels: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    basement_area_1: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    basement_area_2: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    basement_area_3: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    basement_area_4: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    basement_area_5: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    total_builtup_area: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    number_of_floors: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    year_of_construction: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    building_age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    construction_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    roof_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    parcel = relationship(
        "ParcelMaster",
        back_populates="land_building_information"
    )
