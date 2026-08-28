from django.contrib import admin
from .models import CategoriaModel, PlatoModel
# Register your models here.

@admin.register(CategoriaModel)
class CategoriaAdmin(admin.ModelAdmin):
   list_display = ["id", "sucursal", "nombre"]

@admin.register(PlatoModel)
class PlatoAdmin(admin.ModelAdmin):
   list_display = ["id", "categoria", "nombre", "precio", "disponible"]