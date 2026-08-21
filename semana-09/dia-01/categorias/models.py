from django.db import models

# Create your models here.
class CategoriasModel(models.Model):
   nombre = models.CharField(max_length=80, unique=True)
   # blank=True => Indica que el campo no es obligatorio
   # (OPCIONAL)
   descripcion = models.TextField(blank=True)
   activo = models.BooleanField(default=True)
   fecha_creacion = models.DateTimeField(auto_now_add=True)

   class Meta:
      db_table = "categorias"