# Schemas de Pydantic para el modelo User.
# UserCreate: valida los datos que llegan del cliente (POST).
# UserResponse: serializa los datos que devolvemos al cliente (GET).
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
