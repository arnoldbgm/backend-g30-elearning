from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, DateTime, Float, ForeignKey
from datetime import datetime
from db import db

class PedidosModel(db.Model):
   id_pedido: Mapped[int] = mapped_column(Integer, primary_key=True)
   cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
   # Con tipos de fechas, debes de usar el datetime
   fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
   total: Mapped[float] = mapped_column(Float, nullable=False)
   id_cliente: Mapped[int] = mapped_column(Integer, ForeignKey("clientes.id_cliente"))
   id_plato: Mapped[int] = mapped_column(Integer, ForeignKey("platos.id_plato"))

   __tablename__ = "pedidos"
