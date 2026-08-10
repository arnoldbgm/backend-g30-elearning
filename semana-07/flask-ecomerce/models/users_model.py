from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean, DateTime, func, ForeignKey
from db import db
from datetime import datetime 

# ☢️ IMPORTANTE
# Este es un ejemplo de como puedes crear un modelo, se aconseja eliminar este modelo
class UserModel(db.Model):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str] = mapped_column(String, nullable=False)
    last_name:Mapped[str] = mapped_column(String, nullable=False)
    email:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password:Mapped[str] = mapped_column(Text, nullable=False)
    is_active:Mapped[bool] = mapped_column(Boolean, default=True)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    role_id:Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False)
