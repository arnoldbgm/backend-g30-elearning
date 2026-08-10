from flask import request
from flask_restful import Resource
from db import db
from pydantic import ValidationError
from schemas import CategorySchema
from models import CategoriesModel
from flask_jwt_extended import jwt_required

class CategoryResource(Resource):
   def post(self):
      try:
         data = request.get_json()
         validated_data = CategorySchema(name=data["name"])

         new_category = CategoriesModel(name=validated_data.name)

         db.session.add(new_category)
         db.session.commit()

         return {
            "msg": "Categoria creada exitosamente"
         }, 200
      except ValidationError as e:
         return {
            "error": e.errors()
         }, 400
      except Exception:
         db.session.rollback()
         return {
            "msg": "Hubo un error en el servidor"
         }, 500

   @jwt_required()
   def get(self):
      try:
         categories = CategoriesModel.query.filter_by(is_active=True)

         result = []

         for category in categories:
            result.append(category.to_json())

         return result

      except Exception:
         return {
            "msg": "Hubo un error en el servidor"
         }, 500

class OneCategoryResource(Resource):
   def get(self, id):
      try:
         one_category = CategoriesModel.query.get(id)

         if not one_category:
            return {
               "msg": "Categoria no encontrada"
            }, 404

         return  one_category.to_json()
      except Exception:
         return {
            "msg": "Hubo un error en el servidor"
         }, 500

   def delete(self, id):
      try:
         one_category = CategoriesModel.query.get(id)

         if not one_category:
            return {
               "msg": "Categoria no encontrada"
            }, 404

         one_category.is_active = False

         db.session.commit()

         return {
            "msg": "Categoria eliminada exitosamente"
         }, 200
      except Exception:
         db.session.rollback()
         return {
            "msg": "Hubo un error en el servidor"
         }, 500

   def put(self,id):
      try:
         data = request.get_json()
         validated_data = CategorySchema(name=data["name"])

         one_category = CategoriesModel.query.get(id)

         if not one_category:
            return {
               "msg": "Categoria no encontrada"
            }, 404

         one_category.name = validated_data.name

         db.session.commit()

         return {
            "msg": "Actualizacion exitosa",
            "data":{
               "id": one_category.id,
               "name": one_category.name,
               "is_active": one_category.is_active
            }
         }
      except ValidationError as e:
         return{
            "msg": e.errors()
         },400
      except Exception:
         return {
            "msg": "Hubo un error en el servidor"
         }, 500