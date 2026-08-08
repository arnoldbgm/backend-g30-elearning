# Guía — Día 2 (Semana 7): Seguridad con JWT 🔐

Ayer construimos los cimientos: 2 tablas y el CRUD de Categorías y Roles. Hoy le ponemos **seguridad**. ¿Qué significa eso? Que no cualquiera puede crear roles, borrar categorías, ni acceder a lo que no debe.

**Lo que vas a lograr hoy:**
- Usuarios registrados con contraseña cifrada (bcrypt)
- Login que devuelve un **token JWT**
- El CRUD de Roles protegido: sin token → 401, con token → 200
- Respuestas de error limpias y profesionales

**Analogía:** el token JWT es como un brazalete de VIP en una fiesta. El servidor te lo da al hacer login (cuando te identificás con tu correo y contraseña). Cada vez que pedís algo, mostrás el brazalete. Sin brazalete → no entras.

---

## 1. Dependencias nuevas y claves secretas (15 min)

### 1A — Agregar dependencias

A `requirements.txt` le sumamos:

```
Flask-JWT-Extended==4.7.4
bcrypt==5.0.0
email-validator==2.3.0
```

```bash
pip install -r requirements.txt
```

| Paquete | ¿Para qué? |
|---------|------------|
| `Flask-JWT-Extended` | Crear y validar tokens JWT |
| `bcrypt` | Cifrar contraseñas |
| `email-validator` | Validar que un correo tenga formato correcto |

### 1B — Generar la clave secreta

Todo lo que se firma necesita una **clave**.

**Clave JWT** (firma los tokens):

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 1C — Actualizar `.env` y `.env.copy`

`.env`:

```
DATABASE_URL=postgresql://postgres:root@localhost:5432/flask-ecommerce
DEBUG=True
JWT_SECRET_KEY=982fbdeb44fdb8170d7d1de931ec72b7164d48cf2788d69724c758a471483194
```

`.env.copy`:

```
DATABASE_URL=postgresql://postgres:TU_PASSWORD@localhost:5432/flask-ecommerce
DEBUG=True
JWT_SECRET_KEY=genera_uno_con_secrets.token_hex(32)
```

¿Ves la diferencia? En `.env` van tus claves REALES; en `.env.copy`, la INSTRUCCIÓN de cómo generarlas. Nunca compartas tu `.env`.

---

## 2. utils/helpers.py — los helpers de seguridad (20 min)

¿Te acordás del archivo `utils/helpers.py` del boilerplate? Pues ahí va TODO el código que se reutiliza. Hoy le ponemos la seguridad.

Crear (o reemplazar) `utils/helpers.py`:

```python
import os
from bcrypt import hashpw, gensalt, checkpw


def hash_password(password):
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


def verify_password(password, hashed):
    return checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
```

### ¿Qué hace cada pieza?

| Pieza | ¿Qué hace? | ¿Cuándo se usa? |
|-------|-----------|------------------|
| `hash_password` | Convierte una contraseña en un hash bcrypt | Al REGISTRAR un usuario |
| `verify_password` | Compara la contraseña escrita contra el hash guardado | Al hacer LOGIN |

### ¿Por qué no guardamos contraseñas en texto plano?

Imaginá que un ladrón roba la base de datos de una tienda. Si las contraseñas están en texto plano, tiene acceso a todas las cuentas de todos los clientes. Con bcrypt, lo que roba es un montón de basura ilegible (`$2b$12$...`). Cada contraseña, además, tiene un **salt** (sal aleatoria), así que aunque dos usuarios usen la misma clave, los hashes son diferentes.

**Regla #1 de seguridad en backend:** la contraseña del usuario NUNCA se guarda ni se responde. Solo su hash.

---

## 3. Modelo users (15 min)

### models/user.py

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from db import db


class UserModel(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    rol_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)

    rol = db.relationship("RoleModel", backref="usuarios")

    __tablename__ = "users"
```

**Desglose:**

| Línea | ¿Qué significa? |
|-------|-----------------|
| `email ... unique=True` | Dos usuarios no pueden tener el mismo correo |
| `password ... String(200)` | El hash de bcrypt ocupa 60 caracteres; 200 deja margen |
| `ForeignKey("roles.id")` | "users.rol_id apunta a roles.id" — la relación 1:N |
| `rol = db.relationship("RoleModel", backref="usuarios")` | `user.rol` te da el objeto Rol; `role.usuarios` te da la lista de usuarios de ese rol |

**La relación en acción:** un rol tiene muchos usuarios, y cada usuario tiene un rol. Ya estamos conectando tablas con FK, como en la semana 6 pero en nuestro proyecto grande.

### Importar y migrar

`models/__init__.py`:

```python
from .role import RoleModel
from .category import CategoryModel
from .user import UserModel
```

```bash
flask db migrate -m "agregar tabla users"
flask db upgrade
```

**Recordá:** `flask db init` se hace una sola vez (ya lo hicimos ayer). Ahora solo `migrate` + `upgrade`.

---

## 4. Schemas de usuario y autenticación (15 min)

### schemas/user.py

```python
from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol_id: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    rol_id: int
```

**Mirá bien:** `UserResponse` NO tiene `password`. Aunque Pydantic lo permitiera, es una decisión de seguridad: **la contraseña jamás sale en una respuesta**. El `EmailStr` de Pydantic valida el formato del correo automáticamente (por eso instalamos `email-validator`).

### schemas/auth.py

```python
from pydantic import BaseModel, EmailStr


class RegisterSchema(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol_id: int


class LoginSchema(BaseModel):
    email: EmailStr
    password: str
```

**¿Por qué otro schema si ya existe `UserCreate`?** Porque son flujos distintos: registrarse (RegisterSchema) e iniciar sesión (LoginSchema). Separarlos permite que evolucionen por separado sin romperse entre sí. En proyectos reales esta pequeña redundancia es normal y deseable.

### schemas/__init__.py

```python
from .auth import RegisterSchema, LoginSchema
from .role import RoleCreate, RoleResponse
from .category import CategoryCreate, CategoryResponse
from .user import UserCreate, UserResponse
```

---

## 5. JWT en app.py (25 min)

### 5A — ¿Qué es un JWT?

**JSON Web Token**: un pase de entrada firmado digitalmente. Cuando haces login, el servidor te lo entrega. Tiene 3 partes separadas por puntos:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjox... .FirmaFirma
```

1. **Header** — dice qué algoritmo se usó para firmar
2. **Payload** — los datos (quién sos, cuándo expira)
3. **Firma** — la garantía de que nadie lo modificó

**La magia:** el servidor NO necesita buscar en la BD quién sos cada vez. Verifica la firma con su clave secreta y listo. Si alguien intenta cambiar el payload, la firma no coincide y el token se rechaza.

### 5B — Modificar app.py

```python
# Punto de entrada de la aplicación.
# Acá se configura Flask, la base de datos, las migraciones,
# el JWT y se registran las rutas.
import os
from dotenv import load_dotenv
from flask import Flask
from db import db
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt import PyJWTError

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///dev.db")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "secret")

db.init_app(app)
migrate = Migrate(app, db)


# Flask-RESTful intercepta TODAS las excepciones de sus rutas.
# Esta subclase re-lanza los errores de JWT para que los maneje
# Flask con los callbacks de abajo y la respuesta sea un 401 limpio.
class EcommerceApi(Api):
    def handle_error(self, e):
        if isinstance(e, (JWTExtendedException, PyJWTError)):
            raise e
        return super().handle_error(e)


api = EcommerceApi(app)
jwt = JWTManager(app)


@jwt.unauthorized_loader
def falta_token(mensaje):
    return {"msg": "Token faltante o inválido"}, 401


@jwt.invalid_token_loader
def token_invalido(mensaje):
    return {"msg": "Token inválido o expirado"}, 401


@jwt.expired_token_loader
def token_expirado(header, payload):
    return {"msg": "Token expirado"}, 401

from router import register_routes

register_routes(api)

if __name__ == "__main__":
    app.run(debug=os.getenv("DEBUG", "True").lower() == "true")
```

### 5C — El bug que nos obligó a hacer todo esto

Este es UNO de los errores más valiosos de todo el curso. Mirá lo que pasa:

1. Agregas `@jwt_required()` a un endpoint
2. Lo pides SIN token en Postman
3. Resultado: **500** con un traceback gigante en la terminal 😱

**¿Qué pasó?** Resulta que **Flask-RESTful intercepta TODAS las excepciones** que ocurren dentro de sus `Resource` y las convierte en un 500 genérico. Los errores de JWT (token faltante, inválido, expirado) caen en esa trampa. ¿La solución?

| Pieza | Qué hace |
|-------|----------|
| `class EcommerceApi(Api)` | Subclase de `Api`. Su `handle_error` re-lanza los errores de JWT (no los convierte en 500); todo lo demás se maneja normal |
| `api = EcommerceApi(app)` | Usamos nuestra subclase en vez de `Api(app)` |
| `@jwt.unauthorized_loader` | Cuando no hay token → "Token faltante o inválido" (401) |
| `@jwt.invalid_token_loader` | Cuando el token es basura → "Token inválido o expirado" (401) |
| `@jwt.expired_token_loader` | Cuando el token venció → "Token expirado" (401) |

**Resultado:** en vez de un 500 feo con traceback, el cliente recibe un 401 limpio y entendible. Eso es lo que pasa en APIs de producción: **el cliente jamás debe ver un traceback**.

---

## 6. Register y Login (30 min)

### resources/authResource.py

```python
from flask_restful import Resource
from flask import request
from pydantic import ValidationError
from db import db
from flask_jwt_extended import create_access_token
from models.user import UserModel
from models.role import RoleModel
from schemas.auth import RegisterSchema, LoginSchema
from schemas.user import UserResponse
from utils.helpers import hash_password, verify_password


class RegisterResource(Resource):
    def post(self):
        try:
            data = RegisterSchema(**request.get_json())
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        if UserModel.query.filter_by(email=data.email).first():
            return {"msg": "El correo ya está registrado"}, 409

        if not db.session.get(RoleModel, data.rol_id):
            return {"msg": "El rol no existe"}, 404

        user = UserModel(
            nombre=data.nombre,
            email=data.email,
            password=hash_password(data.password),
            rol_id=data.rol_id,
        )
        db.session.add(user)
        db.session.commit()

        return UserResponse.model_validate(user).model_dump(mode="json"), 201


class LoginResource(Resource):
    def post(self):
        try:
            data = LoginSchema(**request.get_json())
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        user = UserModel.query.filter_by(email=data.email).first()
        if not user or not verify_password(data.password, user.password):
            return {"msg": "Credenciales inválidas"}, 401

        token = create_access_token(identity=str(user.id))
        return {
            "access_token": token,
            "usuario": UserResponse.model_validate(user).model_dump(mode="json"),
        }, 200
```

### Desglose de Register paso a paso

1. **Valida** el JSON con `RegisterSchema` → si falta un campo o el correo está mal, Pydantic responde con `errores` detallados → **400**
2. **¿El correo ya existe?** → **409** "El correo ya está registrado"
3. **¿Existe el rol?** → **404** "El rol no existe". No dejas crear un usuario con un rol que no existe en la BD
4. **Crea el usuario** con `hash_password(data.password)` — acá está la magia: el hash entra a la BD, la contraseña jamás
5. **Responde** `UserResponse` (sin contraseña) → **201**

### Desglose de Login paso a paso

1. **Valida** con `LoginSchema` → **400** si falla
2. **Busca el usuario** por email. Fijate la condición:
   ```python
   if not user or not verify_password(data.password, user.password):
   ```
   O el usuario no existe, O la contraseña no coincide → mismo mensaje **401** "Credenciales inválidas". ¿Por qué igual? Para que un atacante no pueda saber qué correos están registrados.
3. **Genera el token** con `create_access_token(identity=str(user.id))`. El `identity` es el dato que el servidor leerá después de cada petición para saber quién es.
4. **Responde** con `access_token` + los datos del usuario → **200**

### Registrar las rutas

`resources/__init__.py`:

```python
from .authResource import RegisterResource, LoginResource
from .roleResource import RoleResource
from .categoryResource import CategoryResource
```

`router/__init__.py`:

```python
from flask_restful import Api
from resources import RegisterResource, LoginResource, RoleResource, CategoryResource


def register_routes(api: Api):
    api.add_resource(RegisterResource, "/api/auth/register")
    api.add_resource(LoginResource, "/api/auth/login")
    api.add_resource(RoleResource, "/api/roles")
    api.add_resource(CategoryResource, "/api/categorias")
```

---

## 7. Proteger Roles con @jwt_required() (25 min)

Llegó el momento. El CRUD de Roles es **solo para autenticados**. ¿Cuánto código nuevo se necesita? Un decorador por método.

### resources/roleResource.py

```python
from flask_restful import Resource
from flask import request
from pydantic import ValidationError
from db import db
from flask_jwt_extended import jwt_required
from models.role import RoleModel
from schemas.role import RoleCreate, RoleResponse


class RoleResource(Resource):
    @jwt_required()
    def get(self):
        roles = RoleModel.query.all()
        return [RoleResponse.model_validate(r).model_dump(mode="json") for r in roles], 200

    @jwt_required()
    def post(self):
        try:
            data = RoleCreate(**request.get_json())
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        if RoleModel.query.filter_by(nombre=data.nombre).first():
            return {"msg": "El rol ya existe"}, 409

        role = RoleModel(nombre=data.nombre, descripcion=data.descripcion)
        db.session.add(role)
        db.session.commit()

        return RoleResponse.model_validate(role).model_dump(mode="json"), 201

    @jwt_required()
    def put(self):
        data = request.get_json()
        role = db.session.get(RoleModel, data.get("id"))
        if not role:
            return {"msg": "Rol no encontrado"}, 404

        try:
            validated = RoleCreate(**data)
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        role.nombre = validated.nombre
        role.descripcion = validated.descripcion
        db.session.commit()

        return RoleResponse.model_validate(role).model_dump(mode="json"), 200

    @jwt_required()
    def delete(self):
        data = request.get_json()
        role = db.session.get(RoleModel, data.get("id"))
        if not role:
            return {"msg": "Rol no encontrado"}, 404

        db.session.delete(role)
        db.session.commit()

        return {"msg": "Rol eliminado"}, 200
```

**Lo único que cambió** respecto al Día 1: `@jwt_required()` arriba de cada método. Así de fácil es proteger un endpoint en producción.

> **Nota:** las Categorías siguen públicas. ¿Por qué? Porque un catálogo es información que todos deberían ver. Los Roles son configuración interna: solo el equipo la toca. Aprende a decidir QUÉ proteger y QUÉ no.

---

## 8. Pruebas en Postman (35 min)

### 8A — Registrar un usuario

- **POST** `http://127.0.0.1:5000/api/auth/register`
- Body → raw → JSON:

```json
{
    "nombre": "Carlos",
    "email": "carlos@correo.com",
    "password": "clave123",
    "rol_id": 1
}
```

**Requisito:** el rol con `id: 1` debe existir. Si no, créalo con POST `/api/roles` (todavía está público).

Resultado: **201** con los datos del usuario, sin contraseña.

### 8B — Login

- **POST** `http://127.0.0.1:5000/api/auth/login`
- Body:

```json
{
    "email": "carlos@correo.com",
    "password": "clave123"
}
```

Resultado: **200** con `access_token` y los datos del usuario. **Copiá el token.**

### 8C — Roles SIN token (debe fallar)

- **GET** `http://127.0.0.1:5000/api/roles`
- Sin token → **401** `{"msg": "Token faltante o inválido"}`

### 8D — Roles CON token (debe funcionar)

- **GET** `http://127.0.0.1:5000/api/roles`
- Pestaña **Authorization** → **Type: Bearer Token** → pegás el token
- → **200** con la lista de roles

### 8E — Probar los errores de JWT

| Prueba | Resultado |
|--------|-----------|
| Token = `basura` | **401** "Token inválido o expirado" |
| Sin header Authorization | **401** "Token faltante o inválido" |
| POST/PUT/DELETE de roles sin token | **401** |

### 8F — Mirar la BD

```sql
SELECT id, nombre, email, password, rol_id FROM users;
```

`password` debe ser un hash de 60 caracteres (`$2b$...`). Si ves tu contraseña en claro, estás haciendo algo mal.

---

## Resumen de conceptos

| Tema | Conceptos clave |
|------|-----------------|
| Claves secretas | `secrets.token_hex(32)`, `.env` protegido |
| Helpers | `hash_password`, `verify_password` — código reutilizable |
| Contraseñas | bcrypt con salt, jamás en claro, jamás en respuestas |
| Modelo users | `ForeignKey` a roles, `relationship` + `backref`, email `unique` |
| JWT | `create_access_token`, `identity`, 3 partes (header, payload, firma) |
| Bug de Flask-RESTful | Convierte errores JWT en 500 → `EcommerceApi` lo re-lanza |
| Callbacks | `unauthorized/invalid_token/expired_token_loader` → 401 limpios |
| Proteger | `@jwt_required()` por método |
| Decisión de diseño | Categorías públicas, Roles protegidos |
