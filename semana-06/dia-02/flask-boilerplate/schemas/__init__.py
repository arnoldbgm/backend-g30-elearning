# Acá se importan todos los schemas de Pydantic.
# Cada vez que crees un schema nuevo, importalo acá.
from .user import UserCreate, UserResponse
from .clientes_schemas import ClienteSchema