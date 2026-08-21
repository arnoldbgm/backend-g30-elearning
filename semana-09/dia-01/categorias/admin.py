from django.contrib import admin
from .models import CategoriasModel
# Solo aqui tu vas a poder registrar los modelos que deseas que se vean dentro del panel del admin

# Para registrar el modelo tu debes de colocar lo siguiente
@admin.register(CategoriasModel)
class CategoriasAdmin(admin.ModelAdmin):
   list_display = ["id", "nombre", "activo", "fecha_creacion"]
   search_fields = ["nombre"]