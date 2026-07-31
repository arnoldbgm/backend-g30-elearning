from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from db import db


# ☢️ IMPORTANTE
# Este es un ejemplo de como puedes crear un modelo, se aconseja eliminar este modelo
class UserModel(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    __tablename__ = "users"
