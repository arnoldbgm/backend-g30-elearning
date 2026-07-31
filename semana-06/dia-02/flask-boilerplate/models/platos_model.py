# Debemos de indicar que esta clase
# sera un modelo
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float   # Aqui consigues los tipos de datos
from db import db


# db.Model => Indica que esta clase actuara
# como una tabla
class PlatoModel(db.Model):
   __tablename__ = "platos"

   # mapped_column(TIPO DE LA COLUMNA, CONFIGURACIONES)
   id:Mapped[int] = mapped_column(Integer, primary_key=True)
   nombre:Mapped[str] = mapped_column(String(100), nullable=False)
   categoria:Mapped[str] = mapped_column(String(50), nullable=False)
   precio:Mapped[float] = mapped_column(Float, nullable=False)