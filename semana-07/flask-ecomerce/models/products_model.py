from db import db
from sqlalchemy import Integer, String, Boolean, Text, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class ProductsModel(db.Model):
   __tablename__ = 'products'

   id:Mapped[int] = mapped_column(Integer, primary_key=True)
   name:Mapped[str] = mapped_column(String, nullable=False)
   code:Mapped[str] = mapped_column(String(7), nullable=False) # P-00001
   description:Mapped[str] = mapped_column(Text, nullable=False)
   image:Mapped[str] = mapped_column(Text, nullable=False)
   brand:Mapped[str] = mapped_column(String, nullable=False)
   size:Mapped[str] = mapped_column(String(20), nullable=False)
   price:Mapped[float] = mapped_column(DECIMAL(10,4), nullable=False)
   stock:Mapped[int] = mapped_column(Integer, nullable=False)
   is_active:Mapped[bool] = mapped_column(Boolean, default=True)
   category_id:Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False)
