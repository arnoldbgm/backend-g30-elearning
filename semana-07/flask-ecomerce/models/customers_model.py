from db import db
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column


class CustomerModel(db.Model):
   __tablename__ = 'customers'

   id:Mapped[int] = mapped_column(Integer, primary_key=True)
   name:Mapped[str] = mapped_column(String, nullable=False)
   last_name:Mapped[str] = mapped_column(String, nullable=False)
   email:Mapped[str] = mapped_column(String, unique=True, nullable=False)
   document_number:Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
   address:Mapped[str] = mapped_column(String, nullable=False)