# Guía — Día 1 (Semana 11): Autenticación con JWT y permisos por rol 🔐

Ayer el catálogo estaba abierto al mundo: cualquiera podía borrar platos o cambiarte precios. Hoy lo cerramos en dos pasos:

**Lo que vas a lograr hoy (en este orden):**
1. El **login** con **JWT** — tu API aprende a preguntar "¿quién sos?"
2. El **registro** (`RegisterView`) — la vista que crea usuarios
3. **Permisos por rol** (el tema del día) — la API decide "¿qué te dejo hacer?"
4. Cerrar el catálogo: el admin escribe, el resto lee

## ¿Por qué JWT? (y por qué te simplifica la vida)

El **JWT** (JSON Web Token) es un token que viaja en la cabecera de cada petición y le dice a tu API quién sos. Lo elegimos porque:

- **Te da el login y el refresh casi gratis**: Simple JWT trae `TokenObtainPairView` y `TokenRefreshView`. No escribís la lógica de login a mano.
- **Es el estándar** de la industria (microservicios, apps mobile, sesiones sin estado).

**Lo único que vas a escribir a mano es la vista de registro** — crear un usuario es lógica tuya, y Simple JWT no la trae. Todo lo demás del login ya viene resuelto.

> **Regla del maestro:** autenticación (¿quién sos?) y autorización (¿qué hacés?) son dos preguntas DISTINTAS. Hoy construís ambas, en ese orden, y el foco está en la segunda: los permisos.

---

## 1. App `usuarios` y modelo `Usuario` (25 min)

```bash
python manage.py startapp usuarios
```

En `settings.py`:

```python
AUTH_USER_MODEL = "usuarios.Usuario"
```

En `usuarios/models.py`:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from utils.helpers import ROLES


class Usuario(AbstractUser):
    rol = models.CharField(max_length=15, choices=ROLES, default="cliente")
    email = models.EmailField(unique=True)

    class Meta:
        db_table = "users"
```

Heredás de `AbstractUser` todo: username, password (hasheada), `is_staff`, permisos... Vos le sumás:
- **`rol`**: la base de la autorización (mañana `reservas` también lo usa).
- **`email` único**: no se repite.

**El import necesita que `utils/helpers.py` exista YA** (si no, `makemigrations` falla). `utils/` NO es una app: es el módulo transversal del proyecto.

Crear `utils/helpers.py`:

```python
ROLES = [
    ("admin", "Admin"),
    ("mesero", "Mesero"),
    ("cliente", "Cliente"),
]
```

> **Todavía NO migres.** Esperá el reset de la BD de abajo. Si migrás antes, falla con `SystemCheckError`.

### Reset de la BD

`AUTH_USER_MODEL` cambió la tabla del usuario, y el catálogo ya tenía FKs al usuario viejo. Como el modelo ya existe (los system checks no fallan), recreamos la BD:

```powershell
del db.sqlite3
Remove-Item -Recurse -Force restaurantes\migrations
Remove-Item -Recurse -Force platos\migrations
python manage.py makemigrations
python manage.py migrate
```

Re-sembrás el catálogo desde el admin.

## 2. Dependencias y configuración de JWT (15 min)

```
djangorestframework==3.18.0
django-cors-headers==4.9.0
djangorestframework-simplejwt==5.5.1
```

```bash
pip install -r requirements.txt
```

En `settings.py`:

```python
from datetime import timedelta

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}
```

## 3. Login automático + registro (30 min)

Creamos `usuarios/views.py` — **solo el `RegisterView` se escribe a mano**:

```python
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .models import Usuario


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, min_length=8, validators=[validate_password]
    )

    class Meta:
        model = Usuario
        fields = ["username", "email", "password"]

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        user = serializer.save()
        return Response(
            {"username": user.username, "email": user.email},
            status=201,
        )
```

**Los dos detalles que casi todos sufren:**

1. `password` es `write_only=True`: el hash NUNCA sale en el JSON.
2. `create_user` (no `create`) hashea el password. `create()` lo dejaría en texto plano. **Nunca guardes passwords sin hash.**

`usuarios/urls.py` — el **login** y el **refresh** ya vienen de Simple JWT:

```python
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView

urlpatterns = [
    path("auth/registro/", RegisterView.as_view(), name="registro"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path(
        "auth/login/refresh/",
        TokenRefreshView.as_view(),
        name="refresh",
    ),
]
```

En `restoapp/urls.py`:

```python
path("api/", include("usuarios.urls")),
```

> **Lo que JWT te ahorró:** el login ya no se escribe a mano (adiós `authenticate` + `Token.objects.get_or_create`). `TokenObtainPairView` hace login y refresh en 2 líneas de URL. Tu único código es el registro.

### Prueba en Postman

| Método | URL | Body | Resultado |
|--------|-----|------|-----------|
| POST | `/api/auth/registro/` | `{"username": "ana", "email": "ana@mail.com", "password": "supersecreto123"}` | **201** |
| POST | `/api/auth/registro/` | email repetido | **400** |
| POST | `/api/auth/registro/` | password corta | **400** |
| POST | `/api/auth/login/` | `{"username": "ana", "password": "supersecreto123"}` | **`access` + `refresh`** |
| POST | `/api/auth/login/refresh/` | `{"refresh": "<tu refresh>"}` | **access nuevo** |

> **access** (30 min) va en `Authorization: Bearer <access>`. **refresh** (1 día) solo sirve para pedir un access nuevo. Guardá ambos.

## 4. Permisos: la vista-por-rol ⭐ (30 min) — EL TEMA DEL DÍA

Ya tenés login y registro. Ahora la parte divertida: **decidir quién hace qué.**

Creamos `usuarios/permissions.py`:

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS


class EsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol == "admin"
        )


class EsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol == "admin"
        )
```

| Permiso | Leer (GET) | Escribir (POST/PUT/DELETE) |
|---------|-----------|----------------------------|
| `AllowAny` | cualquiera | cualquiera |
| `IsAuthenticated` | con login | con login |
| `EsAdminOrReadOnly` | con login | **solo admin** |
| `EsAdmin` | solo admin | solo admin |

> DRF no conoce tu `rol`: ese afinado lo escribís vos, una vez, y lo reutilizás en todas las vistas. `SAFE_METHODS` son GET, HEAD y OPTIONS: las lecturas.

**Analogía:** el portero con lista — los clientes pasan a ver el menú; para tocar el menú, solo el dueño.

## 5. Cerrar el catálogo (15 min)

En las 8 vistas del catálogo (4 de `restaurantes`, 4 de `platos`), agregá la misma línea:

```python
from usuarios.permissions import EsAdminOrReadOnly

...
    permission_classes = [EsAdminOrReadOnly]
```

## 6. Checklist Postman por rol (15 min)

Creá distintos usuarios y asignales `rol` desde el admin de Django (el registro no deja elegir rol a propósito). Verificá CADA celda:

| Acción | Sin token | Cliente | Admin |
|--------|-----------|---------|-------|
| GET catálogo | **401** | **200** | 200 |
| POST `/api/platos/` | **401** | **403** | **201** |
| DELETE `/api/platos/1/` | **401** | **403** | **204** |

> El **403 en POST para el cliente ES la prueba** de que la API distingue roles: primero demostrás quién sos (JWT), después se evalúa tu rol (permisos).

## El mensaje del día

> Ayer tu API era una vidriera sin puerta. Hoy construiste el login (JWT) y el registro que dan identidad, y sobre todo aprendiste a decir NO con autoridad: una vista-por-rol que decide quién lee y quién escribe. Mañana ese mismo rol manda en las reservas.

## Resumen de conceptos

| Tema | Conceptos clave |
|------|-----------------|
| Autenticación | `JWTAuthentication`, `Authorization: Bearer <access>` |
| Login automático | `TokenObtainPairView`, `TokenRefreshView` (access + refresh) |
| Usuario propio | `AUTH_USER_MODEL`, `AbstractUser`, `create_user`, `write_only` |
| Permisos | `BasePermission`, `has_permission`, `SAFE_METHODS`, vista-por-rol |
| Roles | `choices=ROLES` compartido en `utils` |
