from flask_restful import Api
from resources import UserResource, PlatoResource, ClienteResource

def register_routes(api: Api):
    # Aqui vas a declarar tus rutas
    api.add_resource(UserResource, "/api/users")
    api.add_resource(PlatoResource, "/api/v1/plato")
    api.add_resource(ClienteResource, "/api/v1/cliente")
