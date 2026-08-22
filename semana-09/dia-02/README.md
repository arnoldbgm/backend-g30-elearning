# Guía — Día 2 (Semana 9): API REST con Django REST Framework 🚀

Ayer construimos los cimientos: proyecto, modelos, migraciones y hasta un panel admin. Hoy le ponemos la cereza: **una API REST completa** con Django REST Framework (DRF). Y acá viene lo lindo — vos YA sabés construir APIs. Hiciste dos en Flask. Hoy solo aprendés el dialecto Django.

**Lo que vas a lograr hoy:**
- DRF instalado y funcionando
- Serializers (los "schemas Pydantic" de Django)
- Dominar el manager `objects`: filtros, lookups y utilidades del ORM
- CRUD de categorías escribiendo cada paso a mano con clases `APIView`
- CRUD de productos en ~10 líneas con ViewSet + Router
- Evolucionar el modelo sin romper nada (migraciones en acción)
- Descubrir la **browsable API**: tu API probándose sola en el navegador

**Analogía del día:** el serializer es el **traductor de aduana**. Tus objetos Python viven de un lado, el mundo JSON del otro. El serializer revisa documentos (valida), traduce lo que entra y lo que sale, y te rechaza lo que no cumple las reglas.

---

## 1. Qué es DRF (10 min)

**Django REST Framework** es EL estándar para APIs en Django. Mirá el traductor con lo que ya conocés:

| Flask-RESTful (semanas 6-8) | Django REST Framework |
|------------------------------|----------------------|
| `Resource` con get/post/put/delete | Clases `APIView` (mismos métodos) o `ViewSet` |
| Schemas Pydantic | Serializers |
| `request.get_json()` | `request.data` |
| `marshal_with` / dict manual | `Response(serializer.data)` |
| `api.add_resource(...)` | `router.register(...)` |
| `abort(404, ...)` | `get_object_or_404` |

¿Te das cuenta? No estás aprendiendo de cero. Estás cambiando de acento.

---

## 2. Instalar DRF (10 min)

### 2A — Dependencia

A tu `requirements.txt`:

```
djangorestframework==3.18.0
```

```bash
pip install -r requirements.txt
```

### 2B — Registrarlo

En `INSTALLED_APPS` (settings.py):

```python
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',           # NUEVO
    'tienda',
]
```

Y listo. Sin migraciones ni configuración extra — los defaults de DRF son sensatos. Cuando lleguemos a autenticación configuraremos más cosas.

---

## 3. Serializers: el traductor (30 min)

### 3A — El concepto

En Flask teníamos schemas Pydantic que validaban la entrada y formateaban la salida. Un **serializer** hace exactamente eso. La diferencia: `ModelSerializer` genera los campos SOLO desde tu modelo. Casi no escribís tipos a mano.

### 3B — Crear los serializers

Creá el archivo `tienda/serializers.py`:

```python
from rest_framework import serializers
from .models import Categoria, Etiqueta, Producto


class EtiquetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etiqueta
        fields = ['id', 'nombre']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'activo', 'fecha_creacion']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_detalle = CategoriaSerializer(source='categoria', read_only=True)
    etiquetas = EtiquetaSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'codigo', 'nombre', 'precio', 'stock',
            'categoria', 'categoria_detalle', 'etiquetas',
            'activo', 'fecha_creacion',
        ]
        read_only_fields = ['fecha_creacion']
```

### 3C — Desglose pieza por pieza

1. **`fields = [...]`** es una lista blanca EXPLÍCITA. Existe `'__all__'` pero no lo uses: mañana agregás un campo al modelo y aparece solo en la API sin que nadie lo revise.

2. **`categoria`** apunta a la ForeignKey → DRF la convierte automáticamente en campo de escritura por ID. Igual que nuestro `categoria_id` en Flask.

3. **`categoria_detalle`** es un campo EXTRA inventado por nosotros: anida el serializer completo de la categoría, solo lectura (`source='categoria'` dice "lee del atributo categoria"). El resultado:

```json
{
    "id": 1,
    "codigo": "P-00001",
    "categoria": 2,
    "categoria_detalle": { "id": 2, "nombre": "Lácteos", ... }
}
```

Escribís con el ID, leés con el detalle. Patrón profesional estándar.

4. **`etiquetas`**: la relación ManyToMany anidada, también de solo lectura (las etiquetas se gestionan desde el admin por ahora).

---

## 4. Evolución del modelo: imagen_url (15 min)

Llega el "cliente" con un pedido realista: *"quiero guardar la URL de la foto de cada producto"*. ¿Cuánto creés que toma? Tres toques:

**Toque 1** — En `tienda/models.py`, agregá al modelo `Producto`:

```python
    imagen_url = models.URLField(blank=True)
```

**Toque 2** — Migrar:

```bash
python manage.py makemigrations tienda
python manage.py migrate
```

**Toque 3** — Agregar `'imagen_url'` a la lista `fields` del `ProductoSerializer`.

Listo. La BD evolucionó sin romper nada y la API ya lo expone. Ayer aprendiste QUÉ es una migración; hoy la usás como herramienta de todos los días.

---

## 5. La ORM con objects (20 min)

Antes de escribir el CRUD, hagamos una parada técnica en la herramienta que usa por debajo de todo: el manager `objects`. Ya lo viste de reojo en `Categoria.objects.filter(activo=True)` — ahora lo entendemos a fondo, porque lo vas a usar en cada vista que escribas hoy.

### 5A — El manager objects

Todo modelo Django trae de fábrica un manager llamado `objects`: es la puerta de entrada a la base de datos. Es el equivalente directo al `query` de SQLAlchemy.

| Flask-SQLAlchemy (semanas 6-8) | Django ORM |
|---|---|
| `ProductoModel.query.all()` | `Producto.objects.all()` |
| `ProductoModel.query.filter_by(activo=True)` | `Producto.objects.filter(activo=True)` |
| `ProductoModel.query.get(id)` | `Producto.objects.get(pk=id)` |
| `ProductoModel.query.filter(Producto.precio > 10)` | `Producto.objects.filter(precio__gt=10)` |
| `.first()` | `.first()` |
| `.count()` | `.count()` |

### 5B — Operaciones básicas

```python
Producto.objects.all()                # QuerySet con todos
Producto.objects.filter(activo=True)  # Filtra
Producto.objects.exclude(stock=0)     # Excluye
Producto.objects.get(pk=1)            # Un objeto exacto (o excepción)
```

`get()` lanza `DoesNotExist` si no hay resultado, y `MultipleObjectsReturned` si hay más de uno. Por eso en las vistas usamos `get_object_or_404` en vez de `get()` a pelo — ya lo vas a ver abajo.

### 5C — Lookups de campo: el doble guion bajo

Django no usa operadores de comparación (`>`, `<`) como SQLAlchemy. Usa "lookups" con `__`:

| Lookup | Significado | Ejemplo |
|---|---|---|
| `__icontains` | contiene (sin importar mayúsc.) | `nombre__icontains='leche'` |
| `__gte` / `__lte` | mayor/menor o igual | `precio__gte=10` |
| `__gt` / `__lt` | mayor/menor estricto | `stock__lt=5` |
| `__exact` | igual exacto (default) | `codigo__exact='P-001'` |
| `__in` | está en una lista | `categoria_id__in=[1, 2, 3]` |

```python
Producto.objects.filter(nombre__icontains='leche')
Producto.objects.filter(precio__gte=10, stock__gt=0)
Producto.objects.filter(categoria_id__in=[1, 2])
```

Varios filtros separados por coma se combinan con AND implícito. Para OR se usa `Q()` — eso lo vemos más adelante.

### 5D — Utilidades que vas a usar todo el tiempo

```python
Producto.objects.filter(activo=True).order_by('-precio')  # orden descendente
Producto.objects.filter(activo=True).first()               # primero o None
Producto.objects.filter(activo=True).count()                # cantidad
Producto.objects.filter(codigo='P-00001').exists()          # True/False, sin traer el objeto
Producto.objects.values('id', 'nombre', 'precio')            # dicts en vez de objetos
```

`.exists()` es más eficiente que `if queryset:` porque solo le pregunta a la base de datos si hay algo, sin traer los datos.

### 5E — Practicá en el shell

```bash
python manage.py shell
```

```python
>>> from tienda.models import Producto, Categoria
>>> Producto.objects.filter(precio__gte=5).count()
>>> Producto.objects.filter(nombre__icontains='leche').first()
>>> Categoria.objects.filter(activo=True).values('id', 'nombre')
>>> exit()
```

Esto es exactamente lo que vas a usar dentro de cada método de las vistas que armamos ahora.

---

## 6. CRUD categorías con APIView (35 min)

Empezamos con la forma explícita porque muestra todas las piezas por separado. Es el espejo EXACTO del `Resource` de Flask-RESTful: una clase, un método por verbo HTTP.

Reemplazá TODO el contenido de `tienda/views.py`:

```python
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Categoria
from .serializers import CategoriaSerializer


class CategoriaList(APIView):
    def get(self, request):
        categorias = Categoria.objects.filter(activo=True)
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategoriaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoriaDetail(APIView):
    def get(self, request, pk):
        categoria = get_object_or_404(Categoria, pk=pk)
        return Response(CategoriaSerializer(categoria).data)

    def put(self, request, pk):
        categoria = get_object_or_404(Categoria, pk=pk)
        serializer = CategoriaSerializer(categoria, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        categoria = get_object_or_404(Categoria, pk=pk)
        categoria.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

### 6A — Desglose

1. **`class CategoriaList(APIView)`**: cada verbo HTTP es un método de la clase (`get`, `post`, `put`, `delete`). Si llega un método no definido → 405 automático, igual que antes — pero ahora el parecido con `Resource` de Flask-RESTful es total: allá también sobreescribías `get`, `post`, etc. dentro de una clase.

2. **`many=True`** sigue siendo obligatorio para serializar LISTAS. Sin él, serializa UN objeto. Sigue siendo EL error clásico de todo principiante DRF — ya estás avisado, otra vez.

3. **`is_valid(raise_exception=True)`**: si la validación falla, DRF responde **400 con el detalle de errores en JSON** automático. Acordate cuánto JSON de errores armamos a mano en Flask... eso ya no existe.

4. **`get_object_or_404`**: ahora aparece en CADA método de `CategoriaDetail`, porque cada método es independiente (a diferencia de la función `categoria_detail` de antes, que buscaba el objeto una sola vez arriba de un `if`). Es el costo lógico de separar por verbo — más claridad, un poco más de repetición.

5. **`serializer.save()`** conserva su doble vida:
   - Recibió solo `data=` → CREA
   - Recibió instancia + `data=` (`CategoriaSerializer(categoria, data=...)`) → ACTUALIZA
   
   Un método, dos comportamientos. Fijate bien en la diferencia de argumentos.

> **Diferencia filosófica con Flask:** con `APIView`, la clase reemplaza 1 a 1 tu `Resource` de Flask-RESTful — mismos métodos, mismo nombre, misma idea de "un método por verbo". Lo que cambia de fondo sigue siendo el manejo de errores: allá envolvías todo en try/except; acá DRF tiene su propio manejador central de excepciones — vos lanzás señales (`raise_exception=True`, `get_object_or_404`) y él arma la respuesta. Menos código repetido, mismo resultado.

### 6B — Tabla comparativa actualizada

| Flask-RESTful (semanas 6-8) | Django REST Framework |
|---|---|
| `class ProductoResource(Resource):` | `class CategoriaList(APIView):` |
| `def get(self): ...` | `def get(self, request): ...` |
| `def post(self): ...` | `def post(self, request): ...` |
| `api.add_resource(ProductoResource, '/productos')` | `path('categorias/', CategoriaList.as_view())` |

Notá la simetría: es prácticamente el mismo patrón mental. Lo único que cambia es el nombre de la clase base y cómo se conecta a la URL (`.as_view()` en vez de `add_resource`).

---

## 7. Productos con ViewSet + Router (25 min)

Ahora la forma PRO. Todo el CRUD de productos en ~10 líneas. 

### 7A — El ViewSet

Agregar AL FINAL de `tienda/views.py`:

```python
from rest_framework import viewsets

from .models import Producto
from .serializers import ProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.filter(activo=True)
    serializer_class = ProductoSerializer
```

Eso es TODO el código. `ModelViewSet` implementa list, retrieve, create, update, partial_update y destroy. Seis operaciones heredadas.

### 7B — El Router

El router genera las URLs solito. Creá el archivo `tienda/urls.py`:

```python
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoriaList, CategoriaDetail, ProductoViewSet

router = DefaultRouter()
router.register('productos', ProductoViewSet, basename='productos')

urlpatterns = [
    path('categorias/', CategoriaList.as_view(), name='categoria-list'),
    path('categorias/<int:pk>/', CategoriaDetail.as_view(), name='categoria-detail'),
] + router.urls
```

Con clases, la conexión a la URL siempre pasa por `.as_view()` — es lo que convierte la clase en una función que Django puede llamar por request.

Y montamos todo bajo `/api/` en `config/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('tienda.urls')),
]
```

URLs generadas automáticamente por el router:

| Método | URL | Acción |
|--------|-----|--------|
| GET | `/api/productos/` | listar |
| POST | `/api/productos/` | crear |
| GET | `/api/productos/1/` | detalle |
| PUT/PATCH | `/api/productos/1/` | actualizar |
| DELETE | `/api/productos/1/` | eliminar |

**Analogía:** `APIView` es cocinar a mano, plato por plato — ves cada paso (cada método `get`/`post`/`put`/`delete`) y controlás todo. `ModelViewSet` es la procesadora — misma receta estándar, cero esfuerzo. El router es el recepcionista que anota las direcciones por vos.

---

## 8. Pruebas en Postman + Browsable API (25 min)

Levantá el servidor (`python manage.py runserver`) y a probar.

### 8A — Categorías

**POST** `http://127.0.0.1:8000/api/categorias/` (body → raw → JSON):

```json
{
    "nombre": "Lácteos",
    "descripcion": "Leche, quesos y yogures"
}
```

→ **201** con el objeto creado (incluye `id` y `fecha_creacion`).

**GET** `http://127.0.0.1:8000/api/categorias/` → lista completa.

**PUT** `http://127.0.0.1:8000/api/categorias/1/`:

```json
{
    "nombre": "Lácteos y derivados",
    "descripcion": "Leche, quesos y yogures",
    "activo": true
}
```

**DELETE** `http://127.0.0.1:8000/api/categorias/1/` → **204**, sin cuerpo.

### 8B — Productos

**POST** `http://127.0.0.1:8000/api/productos/`:

```json
{
    "codigo": "P-00001",
    "nombre": "Leche Gloria 1L",
    "precio": "4.50",
    "stock": 100,
    "categoria": 2,
    "imagen_url": "https://ejemplo.com/leche.jpg"
}
```

→ **201**. Mirá bien la respuesta: `categoria` trae el ID y `categoria_detalle` trae el objeto anidado completo. Lo que configuramos en el serializer, ahí está.

**GET** `http://127.0.0.1:8000/api/productos/1/` → detalle con etiquetas incluidas.

### 8C — Probar los errores (importante)

| Caso | Esperado |
|------|----------|
| POST categoría con nombre duplicado | **400** con detalle del error en `nombre` |
| POST producto con `"categoria": 999` | **400** "Invalid pk ... object does not exist" |
| GET `/api/productos/999/` | **404** Not found |
| DELETE categoría que tiene productos | **500** — ProtectedError |

Sobre el último caso: ¡es PROTECT trabajando! Te bloquea borrar una categoría con productos. Pero responde 500 (error del servidor) cuando debería ser un 400 elegante. ¿Cómo se maneja eso bien? Próxima semana.

### 8D — Verificar en la base de datos

Como hoy usamos SQLite, abrimos el shell de Django:

```bash
python manage.py shell
```

```python
>>> from tienda.models import Producto
>>> list(Producto.objects.values('id', 'codigo', 'nombre', 'precio', 'stock', 'categoria_id', 'imagen_url', 'activo'))
>>> exit()
```

(Cuando migremos a PostgreSQL, esta misma verificación vuelve a pgAdmin.)

### 8E — La browsable API 🤯

Abrí en el NAVEGADOR:

```
http://127.0.0.1:8000/api/productos/
```

DRF renderiza tu API como página web navegable: botones para crear/editar/borrar, formularios autogenerados, selector de formato. Tu API se documenta y se prueba SOLA. Esto tampoco existía en Flask.

---

## Resumen de conceptos

| Tema | Conceptos clave |
|------|-----------------|
| DRF | Estándar de APIs en Django; Flask-RESTful + Pydantic juntos |
| ORM `objects` | Manager de acceso a BD; equivalente a `.query` de SQLAlchemy |
| Lookups (`__gte`, `__icontains`, etc.) | Reemplazan los operadores de comparación de SQLAlchemy |
| ModelSerializer | Genera campos desde el modelo; `fields` siempre explícitos |
| FK en serializer | Escritura por ID (`categoria`), lectura anidada (`categoria_detalle` con `source`) |
| many=True | Obligatorio para serializar listas |
| raise_exception=True | Validación fallida → 400 automático con errores |
| get_object_or_404 | Busca o lanza 404; reemplaza try/except manual |
| serializer.save() | Crea o actualiza según reciba instancia o no |
| APIView | Clase con un método por verbo HTTP; espejo de `Resource` de Flask-RESTful |
| ModelViewSet | CRUD completo heredado; queryset + serializer_class |
| Router | Genera URLs REST automáticas con `register()` |
| Browsable API | La API navegable desde el navegador |
