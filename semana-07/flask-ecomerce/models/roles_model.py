from db import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class RoleModel(db.Model):
   __tablename__ = 'roles'

   id:Mapped[int] = mapped_column(Integer, primary_key=True)
   name:Mapped[str] = mapped_column(String, unique=True, nullable=False)