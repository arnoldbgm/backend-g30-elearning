# Debemos de indicar que esta clase
# sera un modelo
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float   # Aqui consigues los tipos de datos
from db import db


# db.Model => Indica que esta clase actuara
# como una tabla
class ClienteModel(db.Model):
   __tablename__ = "clientes"

   # mapped_column(TIPO DE LA COLUMNA, CONFIGURACIONES)
   id:Mapped[int] = mapped_column(Integer, primary_key=True)
   nombre:Mapped[str] = mapped_column(String(100), nullable=False)
   telefono:Mapped[str] = mapped_column(String(9), nullable=False)
   direccion:Mapped[str] = mapped_column(String(200), nullable=False)

   # Esta funcion se encarga de definir el formato de respuesta
   def to_json(self):
      return {
         "id": self.id,
         "nombre": self.nombre,
         "telefono": self.telefono,
         "direccion": self.direccion
      }