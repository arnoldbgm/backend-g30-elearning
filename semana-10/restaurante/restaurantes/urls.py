# Para crear los endpoints, haremos lo siguiente:
from django.urls import path
from .views import RestauranteCreateListView, RestauranteDetailView, SucursalCreateListView

# Para empezar a crear endpoints, tienes que llamar urlpatterns
urlpatterns = [
   path("restaurante/", RestauranteCreateListView.as_view()),
   path("restaurante/<int:pk>/", RestauranteDetailView.as_view()),
   path("sucursales/", SucursalCreateListView.as_view())
]