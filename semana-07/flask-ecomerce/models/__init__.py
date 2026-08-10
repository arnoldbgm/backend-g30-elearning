# Acá se importan todos los modelos para que SQLAlchemy los descubra.
# Cada vez que crees un modelo nuevo, importalo acá.
from .users_model import UserModel
from .roles_model import RoleModel
from .categories_model import CategoriesModel
from .products_model import ProductsModel
from .customers_model import CustomerModel
from .sales_model import SalesModel
from .sale_details_model import SaleDetailModel