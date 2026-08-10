from db import db
from sqlalchemy import Integer, String, DateTime,func ,ForeignKey ,DECIMAL, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
# Para crear un enum
# Debes de hacer la siguiente importacion
from enum import Enum
class SaleStatus(str, Enum):
   PENDING = "PENDING"
   CONFIRMED = "CONFIRMED"
   CANCELLED = "CANCELLED"


class SalesModel(db.Model):
   __tablename__ = 'sales'

   id:Mapped[int] = mapped_column(Integer, primary_key=True)
   code:Mapped[str] = mapped_column(String(7), nullable=False)
   total:Mapped[float] = mapped_column(DECIMAL(10,4), nullable=False)
   status: Mapped[str] = mapped_column(SQLEnum(SaleStatus), default=SaleStatus.PENDING, nullable=False)
   created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
   customer_id:Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)