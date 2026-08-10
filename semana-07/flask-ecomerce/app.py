# Punto de entrada de la aplicación.
# Acá se configura Flask, la base de datos, las migraciones
# y se registran las rutas.
import os
from dotenv import load_dotenv
from flask import Flask
from db import db
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///dev.db")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")  # Change this!

jwt = JWTManager(app)

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

from router import register_routes

register_routes(api)

if __name__ == "__main__":
    app.run(debug=os.getenv("DEBUG", "True").lower() == "true")
