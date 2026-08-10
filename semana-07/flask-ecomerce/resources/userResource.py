from flask_restful import Resource
from flask import request
from pydantic import ValidationError
from db import db
from models.users_model import UserModel
from schemas.user import UserCreate, UserResponse


# ☢️ IMPORTANTE
# Este es un ejemplo de como puedes crear un Resource, se aconseja eliminarlo
class UserResource(Resource):
    def get(self):
        users = UserModel.query.all()
        return [UserResponse.model_validate(u).model_dump() for u in users], 200

    def post(self):
        try:
            data = UserCreate(**request.get_json())
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        if UserModel.query.filter_by(username=data.username).first():
            return {"msg": "El nombre de usuario ya existe"}, 409

        if UserModel.query.filter_by(email=data.email).first():
            return {"msg": "El correo ya existe"}, 409

        user = UserModel(username=data.username, email=data.email)
        db.session.add(user)
        db.session.commit()

        return UserResponse.model_validate(user).model_dump(), 201
