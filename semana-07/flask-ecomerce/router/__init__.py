from flask_restful import Api
from resources import UserResource

def register_routes(api: Api):
    api.add_resource(UserResource, "/api/users")
