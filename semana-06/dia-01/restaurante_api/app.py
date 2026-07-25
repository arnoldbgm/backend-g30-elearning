from flask import Flask
from db import db # Vamos a importar SQLAlchemy
from flask_migrate import Migrate #Vamos a usar las Migraciones
from flask_restful import Api
from resources.clientesResource import ClientesResource

app = Flask(__name__)

# 🔩 Configuraciones
# Aqui siempre van a venir las configuraciones
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:root@localhost:5432/restaurante"
db.init_app(app) # Que se ejecute SQLAlchemy
migrate = Migrate(app,db)
api = Api(app)

# Aqui debo de importar mis tablas, para que sean leidas
from models.clientes import ClientesModel
from models.pedidos import PedidosModel
from models.platos import PlatosModel

# Aqui vamos a definir nuestros endpoints
api.add_resource(ClientesResource, "/api/clientes")

if __name__ == "__main__":
   app.run(debug=True)