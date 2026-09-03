# Guía — Día 1 (Semana 11): Identidad y permisos para tu API 🔐

Ayer el catálogo estaba abierto al mundo: cualquiera podía borrar platos o cambiarte precios. Hoy le ponemos **identidad** y **seguridad**:

**Lo que vas a lograr hoy:**
- La app `usuarios` con autenticación por **token**
- Usuarios con roles (`cliente`, `mesero`, `admin`)
- Permisos por rol: el admin escribe, el resto lee
- Email de bienvenida al registrarte y fotos en la nube con Cloudinary

## ¿Por qué NO JWT hoy?

Dos razones:

1. JWT se justifica con escala (microservicios, app mobile, sesiones sin estado). Tu proyecto todavía no la tiene.
2. DRF trae **TokenAuth** de fábrica: el flujo completo en 5 líneas.

**Regla del maestro:** primero demostrás quién sos (TokenAuth). Cuando el problema lo pida de verdad, saltás a JWT. Hoy no.

---

## 1. Nueva app y dependencias (15 min)

```bash
pip install -r requirements.txt
python manage.py startapp usuarios
```

Con `requirements.txt` crecido:

```
djangorestframework==3.18.0
django-cors-headers==4.9.0
cloudinary==1.40.0
drf-spectacular==0.28.0
```

En `settings.py`:

```python
INSTALLED_APPS = [
    "jazzmin",
    "rest_framework",
    "rest_framework.authtoken",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "restaurantes",
    "platos",
    "usuarios",
]

AUTH_USER_MODEL = "usuarios.Usuario"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}
```

> **Todavía NO migres.** Con `AUTH_USER_MODEL` seteado, `makemigrations` corre los system checks de Django y exige que `usuarios.Usuario` exista (y que su `choices` de roles exista). El reset de la BD viene en la sección 2, cuando el modelo y `utils/helpers.py` estén listos; si lo hacés antes, falla con `SystemCheckError`.

## 2. El modelo `Usuario` (20 min)

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

- Heredás de `AbstractUser`: username, password (hasheada), is_staff, permisos... todo.
- Vos le sumás `rol` (la base de la autorización) y `email` **único**.

> `ROLES` vive en `utils/helpers.py` porque mañana `reservas` también lo necesita. Una sola definición, dos apps usándola.

**El import necesita que `utils/helpers.py` exista YA** (si no, `makemigrations` falla con ImportError). Lo creamos ahora, por ahora solo con la constante; las clases llegan en la sección siguiente. `utils/` no es una app: es el módulo transversal del proyecto.

Crear `utils/helpers.py`:

```python
ROLES = [
    ("admin", "Admin"),
    ("mesero", "Mesero"),
    ("cliente", "Cliente"),
]
```

### Reset de la BD (ahora sí)

`AUTH_USER_MODEL` cambió la tabla del usuario, y el catálogo ya tenía FKs al usuario viejo. Como el modelo y los helpers ya existen (los system checks no fallan), recreamos la BD desde cero:

```powershell
del db.sqlite3
Remove-Item -Recurse -Force restaurantes\migrations
Remove-Item -Recurse -Force platos\migrations
python manage.py makemigrations
python manage.py migrate
```

Esto migra TODAS las apps (incluida `usuarios`) y construye la BD nueva bajo el modelo de usuario propio. Después re-sembrás el catálogo desde el admin (Restaurante Don Julio, sucursales, mesas, categorías y platos).

## 3. Email y Cloudinary: sumamos las clases (15 min)

El archivo ya existe (sección 2). Ahora le sumamos las clases de email y fotos (arriba las importaciones, abajo las clases, `ROLES` sigue ahí):

```python
from django.conf import settings
from django.core.mail import EmailMessage
import cloudinary
import cloudinary.uploader


class EmailHelper:
    @staticmethod
    def send_email(subject, body, to_email):
        email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
        email.send()


class CloudinaryHelper:
    @staticmethod
    def upload(file):
        resultado = cloudinary.uploader.upload(file)
        return resultado.get("secure_url")

    @staticmethod
    def delete(public_id):
        cloudinary.uploader.destroy(public_id)
```

Y en `settings.py`:

```python
import cloudinary

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)
```

> `utils/` NO es una app: es código transversal (email, fotos, constantes) que no le pertenece a ningún dominio. El patrón de las semanas 07-08 de Flask, ahora en Django.

## 4. Permisos: la vista-por-rol (20 min)

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

> DRF no conoce tu `rol`: ese afinado lo escribís vos, una vez, y lo reutilizás en todas las vistas. Eso es código reutilizable de verdad.

## 5. Serializers y vistas de auth (35 min)

`usuarios/serializers.py`:

```python
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["username", "email", "rol", "is_staff"]
        read_only_fields = fields
```

`usuarios/views.py`:

```python
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
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


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Credenciales inválidas"}, status=401)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
```

`usuarios/urls.py`:

```python
from django.urls import path
from .views import RegisterView, LoginView, MeView

urlpatterns = [
    path("auth/registro/", RegisterView.as_view(), name="registro"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/me/", MeView.as_view(), name="me"),
]
```

En `restoapp/urls.py`:

```python
path("api/", include("usuarios.urls")),
```

**Los dos detalles que casi todos sufren:**

1. `password` es `write_only=True`: el hash NUNCA sale en el JSON.
2. `create_user` (no `create`) hashea el password. `create()` lo dejaría en texto plano. **Nunca guardes passwords sin hash.**

### Prueba en Postman

| Método | URL | Body / Header | Resultado |
|--------|-----|---------------|-----------|
| POST | `/api/auth/registro/` | `{"username": "ana", "email": "ana@mail.com", "password": "supersecreto123"}` | **201** |
| POST | `/api/auth/registro/` | email repetido | **400** |
| POST | `/api/auth/registro/` | password corta | **400** |
| POST | `/api/auth/login/` | username y password | **token** |
| GET | `/api/auth/me/` | `Authorization: Token <token>` | tus datos |

## 6. Cerrar el catálogo (20 min)

En las 8 vistas del catálogo (4 de `restaurantes`, 4 de `platos`), agregá la misma línea:

```python
from usuarios.permissions import EsAdminOrReadOnly

...
    permission_classes = [EsAdminOrReadOnly]
```

| Acción | Sin token | Cliente | Admin |
|--------|-----------|---------|-------|
| GET catálogo | **401** | **200** | 200 |
| POST `/api/platos/` | **401** | **403** | **201** |
| DELETE `/api/platos/1/` | **401** | **403** | **204** |

> Esa tabla NO es letra muerta: es el checklist de tu prueba en Postman. Verificá cada celda antes de cerrar la sesión.

## El mensaje del día

> Ayer tu API era una vidriera sin puerta. Hoy tiene identidad (tokens), niveles de acceso (roles) y hasta manda mails de bienvenida. Mañana el flujo se completa: una reserva que depende de TODA esta seguridad para funcionar.

## Resumen de conceptos

| Tema | Conceptos clave |
|------|-----------------|
| Autenticación | `TokenAuth`, `Authorization: Token <token>` |
| Usuario propio | `AUTH_USER_MODEL`, `AbstractUser`, `create_user` |
| Seguridad | password con hash, `write_only`, email único |
| Permisos | `BasePermission`, `SAFE_METHODS`, vista-por-rol |
| Transversal | `utils/helpers.py`, `EmailMessage`, Cloudinary |
| Roles | `choices=ROLES` compartido en `utils` |