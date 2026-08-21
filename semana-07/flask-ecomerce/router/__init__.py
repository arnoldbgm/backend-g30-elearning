from flask_restful import Api
from resources import (UserResource, 
                       CategoryResource, 
                       OneCategoryResource,
                       RegisterResource,
                       LoginResource,
                       ProductResource,
                       SaleResource)

def register_routes(api: Api):
    api.add_resource(UserResource, "/api/users")
    # Categorias
    api.add_resource(CategoryResource, "/api/v1/categories")
    api.add_resource(OneCategoryResource, "/api/v1/categories/<int:id>")
    # Usuarios
    api.add_resource(RegisterResource, "/api/v1/user/register")
    api.add_resource(LoginResource, "/api/v1/user/login")
    # Productos
    api.add_resource(ProductResource, "/api/v1/products")
    # Ventas
    api.add_resource(SaleResource, "/api/v1/sales")