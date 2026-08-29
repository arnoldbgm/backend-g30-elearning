from django.db import models

class CategoriaModel(models.Model):
   nombre = models.CharField(max_length=100, null=False)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   # Referencia a una aplicacion exterior
   # NOMBRE_APLICACION.NOMBRE_MODELO
   sucursal = models.ForeignKey('restaurantes.SucursalModel', on_delete=models.PROTECT, related_name='categorias')

   class Meta:
      db_table = "categorias"
      unique_together = [["sucursal", "nombre"]]
      # Configuracion amigable del nombre dentro del Admin
      verbose_name = "Categoria"

   def __str__(self):
      return self.nombre


class PlatoModel(models.Model):
   nombre = models.CharField(max_length=100, null=False)
   precio = models.DecimalField(max_digits=8, decimal_places=2, null=False)
   descripcion = models.TextField(null=True,blank=True)
   foto_url = models.TextField(null=True)
   disponible = models.BooleanField(default=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   categoria = models.ForeignKey(CategoriaModel, on_delete=models.PROTECT, related_name='platos')

   class Meta:
      db_table = "platos"
      verbose_name = "Plato"

   def __str__(self):
      # Lomo saltado - S/ 15.00
      return f"{self.nombre} - S/{self.precio}"