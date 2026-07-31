from flask_restful import Resource
from flask import request
from db import db
from models import ClienteModel
from schemas import ClienteSchema
from pydantic import ValidationError

class ClienteResource(Resource):

   def post(self):
      # {
      #    nombre:"Arnold",
      #    telefono: 920224310,
      #    direccion: "Los Alamos 200B"
      # }
      try:
         data = request.get_json()
         # Aqui vendran mis validaciones
         data_validada = ClienteSchema(**data)
         # Insentar la informacion
         nuevo_cliente = ClienteModel(nombre=data_validada["nombre"],
                                    telefono=data_validada["telefono"],
                                    direccion=data_validada["direccion"])
         db.session.add(nuevo_cliente)
         db.session.commit()
         return {
            "msg": "Cliente insertado exitosamente"
         }
      # Para que funcione ValidationError debemos de importarlo
      # de pydathic
      except ValidationError as e:
         return {
            "msg": "Datos invalidos",
            "error": e.errors()
         }
      except Exception:
         db.session.rollback()
         return {
            "msg": "Ah ocurrido un error dentro del servidor"
         }, 500

   def get(self):
      # Para un get tenemos los siguientes pasos
      # 01 Consultamos la informacion
      clientes = ClienteModel.query.all()
      # Se obtienen en este formato [ <ClienteModel> ...]
      # 02 Formatemos la informacion
      resultado = []
      for cliente in clientes:
         resultado.append(cliente.to_json())
      # 03 Respondemos con la informacion formateada
      return resultado