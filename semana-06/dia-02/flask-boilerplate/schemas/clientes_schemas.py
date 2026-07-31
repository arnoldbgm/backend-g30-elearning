# Aqui vamos a crear nuestas validaciones usando Pydathic
# Siempre que quedramos crear una validacion debemos de importar
from pydantic import BaseModel

# Al heredar el BaseModel indico que esta clase sera para validar
class ClienteSchema(BaseModel):
   # Aqui vendran los campos a validar
   # campo: tipo
   nombre:str
   telefono:str
   direccion:str