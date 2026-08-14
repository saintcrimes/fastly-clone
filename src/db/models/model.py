from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    second_name: Mapped[str] = mapped_column(nullable=False)
    company_name: Mapped[str] = mapped_column(nullable=False)
    job_title: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())    
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())    
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), nullable=False)
    role: Mapped["role"] = relationship(back_populates="users")

class role(Base):

    __tablename__ = "role"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    users: Mapped[list["users"]] = relationship(back_populates="role")
    