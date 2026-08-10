from flask import request
from db import db
from flask_restful import Resource
from pydantic import ValidationError
from schemas import RegisterSchema, LoginSchema
from models import UserModel
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token

class RegisterResource(Resource):
   def post(self):
      try:
         data = request.get_json()
         validated_data = RegisterSchema(**data)

         existing_user = UserModel.query.filter_by(email=validated_data.email).first()
         if existing_user:
            return {
               "msg": "Email ya registrado"
            }, 400

         # Encriptacion de la contraseña
         bytes_password = validated_data.password.encode("utf-8")
         hashed_password = bcrypt.hashpw(bytes_password, bcrypt.gensalt())
         final_password = hashed_password.decode("utf-8")

         user = UserModel(
            name=validated_data.name,
            last_name=validated_data.last_name,
            email=validated_data.email,
            password=final_password,
            role_id=validated_data.role_id
         )

         db.session.add(user)
         db.session.commit()

         return {
            "msg": "Usuario creado extiosamente"
         }, 200
      except ValidationError as e:
         return {
            "msg": e.errors()
         }, 400
      except Exception:
         db.session.rollback()
         return {
            "msg": "Hubo un error en el servidor"
         }, 500

class LoginResource(Resource):
   def post(self):
      try:
         data = request.get_json()
         validated_data = LoginSchema(**data)

         user = UserModel.query.filter_by(email=validated_data.email).first()

         if not user:
            return {
               "msg": "Email o password invalidos"
            }, 401

         # Validacion de la contraseña
         bytes_password = validated_data.password.encode("utf-8")
         bytes_hashed_password = user.password.encode("utf-8")
         password_verified = bcrypt.checkpw(bytes_password, bytes_hashed_password)

         if password_verified == False:
            return {
               "msg": "Email o password invalidos"
            }, 401

         access_token = create_access_token(identity=str(user.id), additional_claims={
                                                                     "name": user.name,
                                                                     "last_name": user.last_name,
                                                                     "email": user.email
         })

         refresh_token = create_refresh_token(identity=str(user.id))

         return {
            "msg": "Inicio de sesion exitoso",
            "access_token": access_token,
            "refresh_token": refresh_token
         }
      except Exception:
         return {
            "msg" : "Hubo un error en el servidor"
         }, 500