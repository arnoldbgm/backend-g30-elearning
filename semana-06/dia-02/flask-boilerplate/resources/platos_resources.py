# Vamos a crear la logica de nuestro controlador (resource)
# Aqui vamos a definir el comportamiento
from flask_restful import Resource # Siempre va ir para todos los resource
from flask import request  # Siempre va ir para todos los resources
from models import PlatoModel
from db import db # Siempre va ir para todos los resources

class PlatoResource(Resource):

   # Vamos a definir el comportamiento de cada endpoint
   def post(self):
      # Siguiendo las buenas practicas para crear un controlador
      # Siempre usamos un try except
      try:
         # 01 Obtner la informacion
         # Siempre se va recibir un json por parte del cliente
         # {
         # nombre: "Lomo saltado",
         # categoria : "Criollo",
         # precio: 15.00
         #}
         data = request.get_json()
         # 02 Validar la informacion
         if not data:
            return {
               "msg": "Datos incompletos"
            }
         if "nombre" not in data:
            return {
               "msg": "Debes de enviar el nombre"
            }
         # 03 Insertar la informacion
         # 03.1 Debes de darle el formato del modelo
         nuevo_plato = PlatoModel(
            nombre=data["nombre"],
            categoria=data["categoria"],
            precio=data["precio"]
         )
         # 03.2 Debes de crear este INSERT INTO que aun no se ejectu
         db.session.add(nuevo_plato)
         # 03.3 Para confirmar el registro o la inserceccion
         db.session.commit()
         # 04 Return una respuesta
         return {
            "msg": "Producto creado exitosamente"
         }
      except Exception:
         # El rollback es para deshacer cualquier cambio
         # que se haya producido en la base de datos
         # siempre estos sean productos de un error
         db.session.rollback()
         return {
            "msg": "Ah ocurrido un error dentro del servidor"
         }, 500