from flask import request
from flask_restful import Resource
from pydantic import ValidationError
from db import db
from utils import CloudinaryHelper
from schemas import ProductSchema
from models import ProductsModel

cloudinary_helper = CloudinaryHelper()

class ProductResource(Resource):
   def post(self):
      try:
         data = request.form
         validated_data = ProductSchema(**data)
         image = request.files.get("image")

         if not image:
            return {
               "msg": "La imagen es obligatoria"
            }, 400

         if image.filename == "":
            return {
               "msg": "La imagen es obligatoria"
            }, 400

         secure_url, public_id = cloudinary_helper.upload_image(image, "products")

         if not secure_url:
            return {
               "msg": "Error al subir la imagen"
            }, 400

         new_product = ProductsModel(
            name=validated_data.name,
            code="P-00",
            description=validated_data.description,
            image=public_id,
            brand=validated_data.brand,
            size=validated_data.size,
            price=validated_data.price,
            stock=validated_data.stock,
            category_id=validated_data.category_id
         )

         db.session.add(new_product)
         db.session.commit()

         return{
            "msg": "Producto subido extiosamente",
            "data": {
               "id": new_product.id,
               "name": new_product.name,
               "image": secure_url,
               "brand": new_product.brand,
               "size": new_product.size,
               "stock": new_product.stock,
               "is_active": new_product.is_active,
               "category_id": new_product.category_id
            }
         }
      except ValidationError as e:
         return {
            "msg": e.errors()
         }, 400
      except Exception as e:
         return {
            "msg": str(e)
         }, 500

   def get(self):
      try:
         products = ProductsModel.query.filter_by(is_active=True)

         response = []

         for product in products:
            product_dict = {
               "id": product.id,
               "code": product.code,
               "name": product.name,
               "description": product.description,
               "image": cloudinary_helper.get_full_url(product.image),
               "brand": product.brand,
               "size": product.size,
               "stock": product.stock,
               "is_active": product.is_active,
            }
            response.append(product_dict)

         return {
            "msg": "Productos cargados exitosamente",
            "data": response
         }
      except Exception as e:
         return {
            "msg": str(e)
         }, 500