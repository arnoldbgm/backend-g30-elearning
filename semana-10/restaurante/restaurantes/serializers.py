# SERIALIZERS
# Los serializers son traductores, que se encargan
# de convertir los datos en JSON, tambien estos
# se encargar de validar la informacion.
from rest_framework import serializers
from .models import RestauranteModel, SucursalModel

# Camino aconsejado para crear un serializer
# es usar el ModelSerializer
# ¿Porque debemos de usar el ModelSerializer?
# Porque este nos creara un serializador
# basado en nuestro modelo

class RestauranteSerializer(serializers.ModelSerializer):
   # Para definir el comportamiendo del serializer
   # debemos de trabajar con la clase Meta
   class Meta:
      # model => Es el modelo que vamos a serializar
      # ¿Que es serializar? Vamos a convertir en un JSON
      # Es el modelo que vamos a validar
      model = RestauranteModel
      # fields => Son los campos que vamos a solicitar
      # son los campos que vamos a devoler
      fields = ["id", "nombre", "created_at"]

class SucursalSerializer(serializers.ModelSerializer):
   # Permite escribir con IDs y devuelve el objeto completo en respuestas
   restaurante = serializers.PrimaryKeyRelatedField(
      queryset=RestauranteModel.objects.all()
   )
   
   class Meta:
      model = SucursalModel
      fields = "__all__"
   
   def to_representation(self, instance):
      # En la respuesta devolvemos el objeto completo del restaurante
      data = super().to_representation(instance)
      data['restaurante'] = RestauranteSerializer(instance.restaurante).data
      return data