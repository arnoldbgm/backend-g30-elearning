from pydantic import BaseModel, EmailStr, Field

class RegisterSchema(BaseModel):
   name: str
   last_name: str
   email: EmailStr
   password: str = Field(min_length=6)
   role_id: int

class LoginSchema(BaseModel):
   email: EmailStr
   password: str = Field(min_length=6)