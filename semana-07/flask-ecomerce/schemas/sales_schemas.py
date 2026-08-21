from pydantic import BaseModel, EmailStr, Field

# {
#   "total": 2360.00,
#   "customer": {
#     "name": "Juan",
#     "last_name": "Perez",
#     "email": "juan.perez@example.com",
#     "document_number": "45678912",
#     "address": "Av. Los Alamos 123, Lima"
#   },
#   "sale_details": [
#     { "product_id": 1, "quantity": 2, "price": 590.00, "subtotal": 1180.00 },
#     { "product_id": 2, "quantity": 1, "price": 1180.00, "subtotal": 1180.00 }
#   ]
# }

class CustomerSchema(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    document_number:str
    address:str

class SaleDetailSchema(BaseModel):
    product_id: int
    quantity:int = Field(gt=0)
    price:float = Field(gt=0) # Precio unitario
    subtotal:float = Field(gt=0) # Total de PU x Cant

class SaleSchema(BaseModel):
    total: float = Field(gt=0) # Total de PU x Cant
    customer: CustomerSchema
    sale_details: list[SaleDetailSchema]