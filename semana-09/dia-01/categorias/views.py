# El archivo views.py contiene todas las vistas
# Las vistas son los resources o tambien llamados 
# los controladres (Es la logica de mi negocio)

from rest_framework.views import APIView
from .serializers import CategoriasSerializer, CategoriasAllSerializer
from .models import CategoriasModel
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class CategoriasView(APIView):
   # Vamos a crear una metodo del tipo post
   # El parametro request => Contiene la informacion
   #                         que se envia desde el cliente
   def post(self, request):
      #{
      #  nombre: "Deportes",
      #  descripcion: "Deportes en general"
      #}
      # 01 Recibir la informacion del cliente
      data = request.data
      # 02 Validar la informacion
      serializer = CategoriasSerializer(data=data)
      # 03 Mostrar error si algun campo no cumple con la validacion
      serializer.is_valid(raise_exception=True)
      # 04 Almacenamiento en la bd
      serializer.save()
      # ¿Porque colocamos serializer.save y no llamamos al Modelo?
      # Es porque el serializer ya contiene la informacion del modelo
      # Osea ya contiene la informacion de donde se va almacernar la info
      # 05 Retornar una respuesta
      return Response({
         "msg": "Categoria creada exitosamente",
         "data": serializer.data
      })

   def get(self, request):
      # 01 Ejecutar una consulta a la tabla
      categorias = CategoriasModel.objects.all()
      # 02 Serializar la consulta
      serializer = CategoriasAllSerializer(categorias, many=True)
      # 03 Responder al cliente
      return Response(serializer.data)

# /api/v1/categorias/1 => api/v1/categorias/<int:pk>
class CategoriasUpdateDeleteView(APIView):
   def delete(self, request, pk):
      # Para consultar un registro de nuestra tablas
      categoria = get_object_or_404(CategoriasModel, pk=pk)
      categoria.delete()
      return Response({"msg": "Categoria eliminada exitosamente"})

   def put(self,request,pk):
      categoria = get_object_or_404(CategoriasModel,pk=pk)
      data=request.data # Capturo la informacion que me envian
      serializer = CategoriasSerializer(categoria, data=data)      
      serializer.is_valid(raise_exception=True)
      serializer.save()
      return Response(serializer.data)