# Dentro del archivo urls.py se van a encontrar
# todas las rutas referentes a nuesta aplicacion
# Parar crear las rutas debemos de importar lo siguiente:

from django.urls import path
from .views import CategoriasView,  CategoriasUpdateDeleteView

# Para definir el listado de rutas debemos de crear
# la variable urlpatterns

urlpatterns = [
   path("categorias/", CategoriasView.as_view()),
   path("categoria/<int:pk>/", CategoriasUpdateDeleteView.as_view())
]