from django.db import models

# Dentro del models. vamos a definir nuestras tablas
class RestauranteModel(models.Model):
   # Para especificar el tipo de la columna
   # models.TIPO
   # null => Para obligar que nos envien los campos (no se permiten nulos)
   # blank => No se van a permitir espacio en blanco o vacios
   nombre = models.CharField(max_length=100, null=False, blank=False)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   # Esta es la forma en como nombramos una tabla
   class Meta:
      db_table = "restaurantes"

   # Como se va mostrar los datos en el Admin de Django
   # El metodo str, es un metodo magico dentro de python
   # Este metodo define como se va a mostrar una clase
   def __str__(self):
      return self.nombre

class SucursalModel(models.Model):
   nombre = models.CharField(max_length=100, null=False, blank=False)
   direccion = models.CharField(max_length=200, null=False, blank=False)
   telefono = models.CharField(max_length=9, null=True)
   foto_url = models.TextField(null=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   # Para hacer una llave foranea en Django, solo debes de llamar a la clase
   # models.ForeignKey
   # Django por defencto agrega los sufijos _id cuando son llave foraneas
   # related_name = Es el nombre que va a tener la relacion
   restaurante = models.ForeignKey(RestauranteModel, on_delete=models.PROTECT, related_name="sucursales")
   
   class Meta:
      db_table = "sucursales"
      # unique_together => No puede existir dos veces la misma combinacion
      unique_together = [["restaurante", "nombre"]]

   def __str__(self):
      # Maido - Arequipa
      return f"{self.restaurante.nombre} - {self.nombre}"

class MesaModel(models.Model):
   UBICACIONES = [
      ("salon", "Salon"),
      ("terraza", "Terraza"),
      ("barra", "Barra")
   ]
   numero = models.IntegerField(null=False)
   capacidad = models.IntegerField(null=False)
   ubicacion = models.CharField(choices=UBICACIONES, default="salon")
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   sucursal = models.ForeignKey(SucursalModel, on_delete=models.PROTECT, related_name="mesas")

   class Meta:
      db_table = "mesas"
      # Dentro de una sucursal no se puedan repetir las mesas
      unique_together = [["sucursal", "numero"]]

   def __str__(self):
      # Mesa 1 (Arequipa)
      return f"Mesa {self.numero} ({self.sucursal.nombre})"