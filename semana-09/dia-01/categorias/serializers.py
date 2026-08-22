# ¿Que son los serializers?
# Los serializers en DRF son como los schemas en Flask
# EStos cumplen con la siguiente funcion:
#     1 . Validar la informacion que se recibe en el request
#     2 . Transformar la informacion de la respueta

from rest_framework import serializers
from .models import CategoriasModel
# Esta es la forma basica de crear un serializer,
# esta forma es un poco arcaica y te va a demandar baste
# tiempo
# class CategoriasSerializer(serializers.Serializer):
#    nombre = serializers.CharField(max_length=80)
#    descripcion = serializers.CharField(min_length=5)

# Ahora usarmoes el metodo mas moderno y el recomenado
# crear los serializador a partir de los modelos

class CategoriasSerializer(serializers.ModelSerializer):
   class Meta:
      # Vamos a cargar un modelo para validar la info
      model = CategoriasModel
      # Vamos a indicar que campos deseamos validar
      fields = ["nombre", "descripcion"]
      # Para indicar que se tomen todos los campos
      # fields = "__all__" => Cree validaciones para todos los campos
      # Campos obligatorios son los que estan en el fields

class CategoriasAllSerializer(serializers.ModelSerializer):
   class Meta:
      model = CategoriasModel
      fields = "__all__"