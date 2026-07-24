from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class UserAuth(Base):
    __tablename__ = "user_auth"
    __table_args__ = {"schema": "propertytax"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(200), unique=True,nullable=True)
    password: Mapped[str] = mapped_column(String(255),nullable=True)
    surveyor_name: Mapped[str] = mapped_column(String(200),nullable=True)
    user_id: Mapped[str | None] = mapped_column(
        String(30),
        unique=True,
        nullable=True
    )
    surveyor_id: Mapped[str] = mapped_column(
        String(30),
        unique=True,
       nullable=True
    )

    email: Mapped[str] = mapped_column(String(200), nullable=True)
    mobile: Mapped[str] = mapped_column(String(15), nullable=True)
    zone: Mapped[str] = mapped_column(String(100), nullable=True)
    ward: Mapped[str] = mapped_column(String(50), nullable=True)
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_logged_in: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
       nullable=True
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="Active",
       nullable=True
    )
