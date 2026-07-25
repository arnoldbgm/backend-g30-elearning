from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from db import db

# Para crear una tabla siempre comienzas
# con una clase

# db.Model => Que indica que la clase es una
# tabla

class PlatosModel(db.Model):
   # Mapped => Especificar el tipo de la columna
   # mapped_column => Crear la columna
   # Cuando creas una columna
   # mapped_column( TIPO, configuraciones)
   # nullAble => Pueda ser Nulo
   id_plato: Mapped[int] = mapped_column(Integer, primary_key=True)
   nombre: Mapped[str] = mapped_column(String(100), nullable=False)
   categoria: Mapped[str] = mapped_column(String(50), nullable=False)
   precio: Mapped[float] = mapped_column(Float, nullable=False)


   # Es para nombrar a nuestra tabla
   __tablename__ = "platos"