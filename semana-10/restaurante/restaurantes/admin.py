from django.contrib import admin
from .models import SucursalModel, RestauranteModel, MesaModel

# Para registrar un modelo usamos el decorador @admin.register
@admin.register(RestauranteModel)
class RestauranteAdmin(admin.ModelAdmin):
   # Vamos a definir el comportamiento
   list_display = ["id", "nombre", "created_at"]

@admin.register(SucursalModel)
class SucursalAdmin(admin.ModelAdmin):
   list_display = ["id", "restaurante", "nombre", "direccion", "telefono"]

@admin.register(MesaModel)
class MesaAdmin(admin.ModelAdmin):
   list_display = ["id", "sucursal", "numero", "capacidad", "ubicacion"]