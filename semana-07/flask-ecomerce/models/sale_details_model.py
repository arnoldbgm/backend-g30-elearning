from db import db
from sqlalchemy import Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class SaleDetailModel(db.Model):
   __tablename__ = 'sale_details'

   id:Mapped[int] = mapped_column(Integer, primary_key=True)
   quantity:Mapped[int] = mapped_column(Integer, nullable=False)
   price: Mapped[float] = mapped_column(DECIMAL(10,4), nullable=False)
   total: Mapped[float] = mapped_column(DECIMAL(10,4), nullable=False)
   product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
   sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), nullable=False)