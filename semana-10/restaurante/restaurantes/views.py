# Dentro del views nosotros definimos la logica
# es decir definimos el comportamiento de nuestros
# endpoints

# Los generics ¿Que son los generics?
# Son clases con comportamientos ya definidos
# Los generics que existen:
# ListAPIView => Listar todos los registros
# CreateAPIView => Crear un registro
# RetrieveAPIView => Obtener un SOLO registro
# UpdateAPIView => Actualizar un registro
# DestroyAPIView => Eliminar un registro

# ¿Para crear un view usando generics?
# class NombredeTuGusto(generics.NombreGenerico):
#    queryset => Es la consulta que se va a realizar
#    serializer_class => Es el serializador que se va a usar

from rest_framework import generics
from .models import RestauranteModel, SucursalModel
from .serializers import RestauranteSerializer, SucursalSerializer

class RestauranteCreateListView(generics.ListCreateAPIView):
   queryset = RestauranteModel.objects.all()
   serializer_class = RestauranteSerializer

class RestauranteDetailView(generics.RetrieveUpdateDestroyAPIView):
   queryset = RestauranteModel.objects.all()
   serializer_class = RestauranteSerializer

class SucursalCreateListView(generics.ListCreateAPIView):
   queryset = SucursalModel.objects.all()
   serializer_class = SucursalSerializer