# Guía — Día 1 (Semana 10): Empezamos RestoApp 🍽️

Hoy arrancamos el proyecto más grande del curso: una **API REST de reservas para un restaurante multi-sucursal**. En las próximas 4 sesiones vamos a construir RestoApp de punta a punta: el catálogo del restaurante, usuarios con JWT, envío de correos, fotos en la nube con Cloudinary y reservas con disponibilidad real.

**Lo que vas a lograr hoy:**
- Tu proyecto Django `restoapp` parado y corriendo
- 5 tablas del catálogo: `restaurantes`, `sucursales`, `mesas`, `categorias` y `platos`
- El proyecto organizado en **apps por dominio** (hoy: `restaurantes` y `platos`)
- El admin de Django + Jazzmin funcionando, con data cargada

## El plan completo (para que sepas a dónde vamos)

| Sesión | Qué vamos a construir |
|--------|----------------------|
| **Hoy** | Setup + tablas del catálogo + admin |
| 10 Día 2 | CRUD del catálogo con DRF generics |
| 11 Día 1 | Usuarios + JWT + email de bienvenida + Cloudinary |
| 11 Día 2 | Reservas, disponibilidad, reseñas y Swagger |

**Analogía:** hoy construimos los cimientos y el primer piso del restaurante. Sin cimientos no hay reservas que valgan.

---

## 1. Entorno y dependencias (15 min)

Creá la carpeta del proyecto:

```bash
mkdir restoapp
cd restoapp
python -m venv venv
venv\Scripts\activate
```

Crear `requirements.txt` con lo mínimo de hoy:

```
Django~=5.2.0
django-jazzmin==3.0.5
python-dotenv==1.2.2
```

```bash
pip install -r requirements.txt
```

**OJO:** cada sesión vamos a AGREGAR paquetes a este archivo (DRF, JWT, Cloudinary...). Hoy es lo mínimo.

## 2. El archivo `.env` (10 min)

Crear `.env` (tus secretos de verdad):

```
SECRET_KEY=clave-larga-y-dificil-de-adivinar
DEBUG=True
```

Y `.env.copy` (la plantilla pública, sin secretos):

```
SECRET_KEY=tu-clave-secreta
DEBUG=True
```

> El `.env` nunca se sube al repo. Es como la llave de la caja fuerte: la tenés vos, no la pegas en la puerta.

## 3. Crear el proyecto (25 min)

```bash
django-admin startproject restoapp .
python manage.py startapp restaurantes
python manage.py startapp platos
```

Ahora tenés tres carpetas: `restoapp/` (la configuración) y las apps `restaurantes/` y `platos/`. **¿Por qué dos apps y no una sola?** Porque una app = un dominio del negocio. El restaurante y sus mesas no son lo mismo que el menú con platos, y mañana vas a ver que cada app maneja sus archivos solos.

En `restoapp/settings.py`:

1. Arriba, cargar las variables de entorno:

```python
import os
from dotenv import load_dotenv

load_dotenv()
```

2. Registrar las apps del proyecto (DRF entra mañana):

```python
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "restaurantes",
    "platos",
]
```

3. Usar la clave desde el entorno:

```python
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default")
DEBUG = os.getenv("DEBUG") == "True"
```

Probá:

```bash
python manage.py migrate
python manage.py runserver
```

**Cohete en `http://127.0.0.1:8000/`** = proyecto vivo.

---

## 4. El modelo `Restaurante` (20 min)

En `restaurantes/models.py`:

```python
from django.db import models


class Restaurante(models.Model):
    nombre = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "restaurantes"

    def __str__(self):
        return self.nombre
```

Notá dos cosas:
- `auto_now_add=True` → se llena sola **una sola vez** (creación); `auto_now=True` → se actualiza sola en **cada guardado**
- **`class Meta: db_table = "restaurantes"`** → le decís a Django cómo se llama la tabla REAL en la BD. Sin esto, la tabla se llamaría `restaurantes_restaurante` (app + modelo). Con esto, queda igual que tu diagrama. Lo vas a usar en TODOS los modelos.

```bash
python manage.py makemigrations restaurantes
python manage.py migrate
```

## 5. Los modelos con relación: `Sucursal` y `Mesa` (30 min)

Una `Sucursal` le pertenece a un restaurante (ForeignKey). Una `Mesa` le pertenece a una sucursal. Es la cadena 1:N del diagrama. Seguís en `restaurantes/models.py`:

```python
class Sucursal(models.Model):
    restaurante = models.ForeignKey(
        Restaurante, on_delete=models.CASCADE, related_name="sucursales"
    )
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True)
    foto_url = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sucursales"
        unique_together = [["restaurante", "nombre"]]

    def __str__(self):
        return f"{self.restaurante.nombre} - {self.nombre}"
```

```python
class Mesa(models.Model):
    UBICACIONES = [
        ("salon", "Salón"),
        ("terraza", "Terraza"),
        ("barra", "Barra"),
    ]

    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.CASCADE, related_name="mesas"
    )
    numero = models.IntegerField()
    capacidad = models.IntegerField()
    ubicacion = models.CharField(max_length=10, choices=UBICACIONES, default="salon")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mesas"
        unique_together = [["sucursal", "numero"]]

    def __str__(self):
        return f"Mesa {self.numero} ({self.sucursal.nombre})"
```

**¿Y por qué `unique_together`? (la parte que NO se saca)**

En `class Meta` hay dos líneas, y NO son lo mismo:

- `db_table = "mesas"` → solo el nombre de la tabla.
- `unique_together = [["sucursal", "numero"]]` → **la regla de negocio**: no pueden existir dos mesas con el mismo número en la misma sucursal. La mesa 5 puede estar en Centro Y en Norte (por eso es de DOS campos: unicidad **compuesta**).

Esto se mantiene a propósito: aunque tu app y tu API hagan todo bien, la **base de datos es la última barrera**. Nadie, ni siquiera un error de código, va a crear dos mesa 5 en el mismo salón. Y como bonus, mañana el DRF va a leer esta regla sola y devolver **400** cuando alguien mande un duplicado. Sin escribir validación a mano.

Acordate del formato: `[["sucursal", "numero"]]` — corchetes dobles, porque es una lista de pares.

```bash
python manage.py makemigrations restaurantes
python manage.py migrate
```

## 6. `Categoria` y `Plato` (25 min)

Misma cadena: la categoría cuelga de la sucursal, el plato cuelga de la categoría. PERO ahora cambiamos de archivo: estos dos viven en la app `platos`.

En `platos/models.py`:

```python
class Categoria(models.Model):
    sucursal = models.ForeignKey(
        "restaurantes.Sucursal", on_delete=models.CASCADE, related_name="categorias"
    )
    nombre = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categorias"
        unique_together = [["sucursal", "nombre"]]

    def __str__(self):
        return self.nombre
```

Miralo dos veces: la FK a `Sucursal` está escrita como **texto** `"restaurantes.Sucursal"`. Cuando una relación cruza de una app a otra, se escribe "app.Modelo" entre comillas. El Django lo resuelve solo; vos solo marcás el límite.

```python
class Plato(models.Model):
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name="platos"
    )
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    descripcion = models.TextField(blank=True)
    foto_url = models.CharField(max_length=500, blank=True)
    disponible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "platos"

    def __str__(self):
        return f"{self.nombre} - S/ {self.precio}"
```

> **Prestá atención:** el plato NO tiene sucursal. ¿Cómo sabríamos en qué sucursal está? Por la cadena `plato → categoria → sucursal`. Eso es lo que se llama **heredar la relación** — y funciona aunque cada eslabón viva en una app distinta.

```bash
python manage.py makemigrations platos
python manage.py migrate
```

## 7. Admin + Jazzmin + tu primera data (40 min)

1. Crear el superusuario:

```bash
python manage.py createsuperuser
```

2. Cada app registra SUS modelos. En `restaurantes/admin.py`:

```python
from django.contrib import admin
from .models import Restaurante, Sucursal, Mesa


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "created_at")


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurante", "nombre", "direccion", "telefono")
    search_fields = ("nombre", "direccion")
    list_filter = ("restaurante",)


class MesaInline(admin.TabularInline):
    model = Mesa
    extra = 1


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ("id", "sucursal", "numero", "capacidad", "ubicacion")
    list_filter = ("sucursal", "ubicacion")
```

Y en `platos/admin.py`:

```python
from django.contrib import admin
from .models import Categoria, Plato


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "sucursal", "nombre")
    list_filter = ("sucursal",)


class PlatoInline(admin.TabularInline):
    model = Plato
    extra = 1


@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    list_display = ("id", "categoria", "nombre", "precio", "disponible")
    list_filter = ("disponible", "categoria")
    search_fields = ("nombre",)
```

> Django junta los registros de TODAS las apps en un solo panel. Cada app se encarga de lo suyo.

3. Entrar a `http://127.0.0.1:8000/admin/` y cargar a mano:

- Restaurante **"Restaurantes Don Julio"**
- Sucursales **Centro** y **Norte**
- Mesas de Centro: 1 (cap 2, barra), 2 (cap 4, salón), 3 (cap 6, terraza)
- Categorías de Centro: Entradas, Fondos, Postres
- Platos de Fondos: Lomo Saltado (S/ 35.00), Ceviche (S/ 42.00), Ají de Gallina (S/ 28.00)

> Cargar la data a mano no es un trámite aburrido: es tu primera prueba real del admin. Y te da los datos que mañana vas a consumir con la API.

## Mensaje del día

El catálogo ya tiene forma, la BD está sembrada y descubriste el orden Django: **una app por dominio**. Mañana le damos vida: cada entidad se convierte en endpoints que el resto del mundo puede consumir.

## Resumen de conceptos

| Tema | Conceptos clave |
|------|-----------------|
| Setup | `startproject`, `startapp`, `.env`, `.env.copy`, `python-dotenv` |
| Apps | una app por dominio; cada una con sus archivos propios |
| Models | `CharField`, `DecimalField`, `ForeignKey`, `choices`, `__str__` |
| Tiempos | `auto_now_add` vs `auto_now` |
| Unicidad | `unique_together` de campos compuestos (la regla se mantiene) |
| BD | `db_table` = el nombre real de la tabla, como el diagrama |
| FKs entre apps | `"app.Modelo"` como texto |
| Cadenas | `plato → categoria → sucursal` (heredar relación) |
| Migraciones | `makemigrations <app>` → `migrate` |
| Admin | `@admin.register`, `list_display`, `search_fields`, `list_filter`, `inline` |