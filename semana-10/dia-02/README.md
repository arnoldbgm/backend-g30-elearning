# Guía — Día 2 (Semana 10): Le damos vida al catálogo con DRF 🔧

Ayer la BD quedó sembrada. Hoy cada entidad se convierte en **endpoints** que el mundo puede consumir: listar, crear, actualizar y borrar restaurantes, sucursales, categorías y platos.

**Lo que vas a lograr hoy:**
- Instalar Django REST Framework (DRF)
- Un **serializer** por cada entidad del catálogo (en la app que le corresponde)
- El CRUD completo de las 4 entidades usando vistas genéricas de DRF
- Cada app con sus propias vistas y sus propias rutas
- Probar TODO en Postman, incluidos los errores

## El plan (dónde estamos)

| Sesión | Qué construimos |
|--------|-----------------|
| ✅ Hoy | CRUD del catálogo con generics |
| 11 Día 1 | Usuarios + JWT + email + Cloudinary |
| 11 Día 2 | Reservas, disponibilidad, reseñas y Swagger |

**Analogía:** hoy el restaurante abre sus puertas: instalás las puertas (serializers), los mostradores (vistas) y cada plato queda a la vista del público (endpoints). Pero todavía no hay seguridad: mañana ponemos el candado.

---

## 1. Instalar DRF (10 min)

A `requirements.txt`:

```
djangorestframework==3.18.0
```

```bash
pip install -r requirements.txt
```

Registrar en `INSTALLED_APPS` de `settings.py`:

```python
"rest_framework",
```

## 2. Los serializers, un archivo por app (20 min)

El serializer es el **traductor**: convierte un objeto Django en JSON y el JSON en un objeto validado.

En `restaurantes/serializers.py` (archivo nuevo):

```python
from rest_framework import serializers
from .models import Restaurante, Sucursal


class RestauranteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurante
        fields = ["id", "nombre", "created_at", "updated_at"]


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = ["id", "restaurante", "nombre", "direccion", "telefono", "foto_url"]
```

En `platos/serializers.py` (archivo nuevo):

```python
from rest_framework import serializers
from .models import Categoria, Plato


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "sucursal", "nombre"]


class PlatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plato
        fields = ["id", "categoria", "nombre", "precio", "descripcion", "foto_url", "disponible"]
```

> Fijate lo poderoso: le das el `model` y el serializer deduce los tipos, qué es obligatorio y hasta la unicidad. En Flask escribíamos esos schemas campo por campo. Y cada app serializa SOLO lo suyo.

## 3. CRUD de `Restaurante` — la DEMO (35 min)

En `restaurantes/views.py`:

```python
from rest_framework import generics
from .models import Restaurante, Sucursal
from .serializers import RestauranteSerializer, SucursalSerializer


class RestauranteListCreateView(generics.ListCreateAPIView):
    queryset = Restaurante.objects.all()
    serializer_class = RestauranteSerializer


class RestauranteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Restaurante.objects.all()
    serializer_class = RestauranteSerializer
```

Dos clases y listo el CRUD completo en 4 líneas útiles. ¿Cómo?

- `ListCreateAPIView` → lista (GET) y crea (POST)
- `RetrieveUpdateDestroyAPIView` → trae uno (GET), actualiza (PUT/PATCH) y borra (DELETE)

Crear `restaurantes/urls.py`:

```python
from django.urls import path
from .views import (
    RestauranteListCreateView,
    RestauranteDetailView,
)

urlpatterns = [
    path("restaurantes/", RestauranteListCreateView.as_view(), name="restaurantes-list"),
    path("restaurantes/<int:pk>/", RestauranteDetailView.as_view(), name="restaurantes-detail"),
]
```

Montar en `restoapp/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("restaurantes.urls")),
]
```

### Probar YA en Postman

| Método | URL | Body | Resultado |
|--------|-----|------|-----------|
| GET | `/api/restaurantes/` | — | lista con el de ayer |
| POST | `/api/restaurantes/` | `{"nombre": "Pollos La Granja"}` | **201** |
| PATCH | `/api/restaurantes/1/` | `{"nombre": "Restaurantes Don Julio SAC"}` | **200** |
| DELETE | `/api/restaurantes/99/` | — | **404** |

## 4. Réplica: `Sucursal` (20 min)

Es el MISMO patrón, cambiando nombres. Misma app `restaurantes`:

```python
class SucursalListCreateView(generics.ListCreateAPIView):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer


class SucursalDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
```

```python
path("sucursales/", SucursalListCreateView.as_view(), name="sucursales-list"),
path("sucursales/<int:pk>/", SucursalDetailView.as_view(), name="sucursales-detail"),
```

Pruebas:

| Método | URL | Body | Resultado |
|--------|-----|------|-----------|
| POST | `/api/sucursales/` | `{"restaurante": 1, "nombre": "Norte", "direccion": "Av. Universitaria 456"}` | **201** |
| POST | `/api/sucursales/` | misma sucursal repetida | **400** (¡el `unique_together` de ayer trabaja SOLO!) |

## 5. Réplica: `Categoria` — MIRÁ, CAMBIÁS DE APP (15 min)

La categoría no está en `restaurantes`: vive en `platos`. Acá se siente la arquitectura.

En `platos/views.py`:

```python
from rest_framework import generics
from .models import Categoria, Plato
from .serializers import CategoriaSerializer, PlatoSerializer


class CategoriaListCreateView(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class CategoriaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
```

En `platos/urls.py` (archivo nuevo):

```python
from django.urls import path
from .views import CategoriaListCreateView, CategoriaDetailView

urlpatterns = [
    path("categorias/", CategoriaListCreateView.as_view(), name="categorias-list"),
    path("categorias/<int:pk>/", CategoriaDetailView.as_view(), name="categorias-detail"),
]
```

Y en `restoapp/urls.py` sumás la nueva app al mismo prefijo:

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("restaurantes.urls")),
    path("api/", include("platos.urls")),
]
```

POST `/api/categorias/` con `{"sucursal": 1, "nombre": "Bebidas"}` → **201**.

## 6. Réplica: `Plato` (20 min)

Misma app `platos`:

```python
class PlatoListCreateView(generics.ListCreateAPIView):
    queryset = Plato.objects.all()
    serializer_class = PlatoSerializer


class PlatoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plato.objects.all()
    serializer_class = PlatoSerializer
```

```python
path("platos/", PlatoListCreateView.as_view(), name="platos-list"),
path("platos/<int:pk>/", PlatoDetailView.as_view(), name="platos-detail"),
```

Atención a dos detalles que te van a salvar:

1. **El filtro del menú:** `GET /api/platos/?disponible=True` → DRF filtra solo con el query param. Sin escribir una línea de lógica.
2. **El precio es string:** al crear un plato ya el `precio` llega como `"35.00"` (texto), no `35.00`. Es porque JSON no entiende `Decimal`.

## 7. El mensaje del día

> La API del catálogo está **funcional pero abierta**: cualquiera podría borrar un plato o cambiarte los precios. Eso es innegociable en un producto real. Mañana construimos los usuarios con JWT y cerramos la puerta.

## Resumen de conceptos

| Tema | Conceptos clave |
|------|-----------------|
| DRF | `ModelSerializer`, `queryset`, `serializer_class` |
| Generics | `ListCreateAPIView`, `RetrieveUpdateDestroyAPIView` |
| Apps | cada app con sus `serializers.py`, `views.py` y `urls.py` |
| Rutas | `include` por app bajo `/api/` |
| Postman | probar apenas se crea, incluidos los 400 y 404 |
| Query params | `?disponible=True` filtra de gratis |