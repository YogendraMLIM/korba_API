from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class UserAuth(Base):
    __tablename__ = "user_auth"
    __table_args__ = {"schema": "propertytax"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    surveyor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    surveyor_id: Mapped[str | None] = mapped_column(
        String(30),
        unique=True,
        nullable=True
    )

    email: Mapped[str] = mapped_column(String(200), nullable=True)
    mobile: Mapped[str] = mapped_column(String(15), nullable=True)
    zone: Mapped[str] = mapped_column(String(100), nullable=True)
    ward: Mapped[str] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="Active",
        nullable=False
    )