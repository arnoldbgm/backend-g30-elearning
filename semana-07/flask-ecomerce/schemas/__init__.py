# Acá se importan todos los schemas de Pydantic.
# Cada vez que crees un schema nuevo, importalo acá.
from .user import UserCreate, UserResponse
from .categories_schemas import CategorySchema
from .users_schemas import RegisterSchema, LoginSchema