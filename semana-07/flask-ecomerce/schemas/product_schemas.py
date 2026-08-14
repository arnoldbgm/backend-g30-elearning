from pydantic import BaseModel, Field

class ProductSchema(BaseModel):
   name: str
   description: str
   brand: str
   size: str
   price: float = Field(gt=0)
   stock: int = Field(gt=0)
   category_id: int