# Acá se importan todos los resources para que el router los use.
# Cada vez que crees un resource nuevo, importalo acá.
from .userResource import UserResource
from .categories_resources import CategoryResource, OneCategoryResource
from .users_resources import RegisterResource, LoginResource
from .products_resources import ProductResource
from .sales_resources import SaleResource