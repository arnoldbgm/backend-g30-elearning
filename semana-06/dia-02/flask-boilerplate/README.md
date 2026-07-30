# 🧠 Flask Boilerplate — entendé cada pieza (y después usala)

<p align="center">
  <img src="https://flask.palletsprojects.com/en/stable/_static/flask-logo.png" alt="Logo de Flask" height="80">
</p>

Este boilerplate no es "código que copiás y ya". Es una base pensada para que **entiendas cómo y por qué funciona cada pieza** antes de escribir tu primera línea de negocio. Si entendés esto, después crear una API con Flask es siempre el mismo baile — cambián los modelos, cambián los endpoints, pero la coreografía es la misma.

---
## 0. ¿Qué es un boilerplate y por qué usarlo?

Cuando arrancás un proyecto nuevo, siempre hacés lo mismo: creás carpetas, instalás librerías, configurás la conexión a la base de datos, preparás migraciones. Eso es tiempo que no estás gastando en **tu lógica de negocio**.

Un boilerplate es ese esqueleto que ya tiene todo listo. No tenés que pensar en "¿dónde pongo esto?" porque ya hay una carpeta para cada cosa. Solo creás tu modelo, tu resource, lo registrás, y a producir.

Pero ojo: **no es magia**. Cada pieza está ahí por una razón, y esta guía te explica exactamente cuál es.

---
## 1. Primer viaje — corré el proyecto y hace tu primer request

Antes de entender cómo funciona, veámoslo andar.

```bash
# Parate en la carpeta
cd flask-boilerplate

# Creá el entorno virtual
python -m venv venv

# Activale
# Windows:
venv\Scripts\activate
# Linux / Mac:
source venv/bin/activate

# Instalá las dependencias
pip install -r requirements.txt

# Inicializá migraciones (solo la primera vez)
flask db init

# Creá la tabla users
flask db migrate -m "crear tabla users"
flask db upgrade

# Corré el servidor
python app.py
```

Si todo sale bien, ves:

```
 * Running on http://127.0.0.1:5000
```

Abrí otra terminal y probá:

```bash
# GET — pedir todos los usuarios
curl http://127.0.0.1:5000/api/users
# → [] (vacío, no hay usuarios todavía)

# POST — crear un usuario
curl -X POST http://127.0.0.1:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "jperez", "email": "jperez@mail.com"}'
# → {"id": 1, "username": "jperez", "email": "jperez@mail.com"} (código 201)
```

**Ya tenés una API funcionando.** Ahora entendamos cómo llegamos hasta acá.

---
## 2. Estructura del proyecto — el mapa del tesoro

```
flask-boilerplate/
├── models/               ← ¿Cómo se ven los datos en la DB?
│   ├── __init__.py
│   └── user.py
├── schemas/              ← ¿Cómo se validan los datos que entran y salen?
│   ├── __init__.py
│   └── user.py
├── resources/            ← ¿Qué hace cada endpoint?
│   ├── __init__.py
│   └── userResource.py
├── router/               ← ¿Dónde se conectan los endpoints con las URLs?
│   └── __init__.py
├── utils/                ← ¿Dónde va el código que se repite?
│   ├── __init__.py
│   └── helpers.py
├── db.py                 ← La conexión a la base de datos
├── app.py                ← El punto de entrada de la aplicación
├── .env                  ← Configuración que cambia según el entorno
├── requirements.txt
└── README.md
```

Cada carpeta tiene **una sola responsabilidad**. Si todo estuviera en un archivo de 2000 líneas, sería imposible de mantener. Separar por capas te permite encontrar lo que buscás rápido, cambiar una parte sin romper las otras, y reutilizar código en varios lados.

---
## 3. `app.py` — el cerebro de la aplicación

```python
import os
from dotenv import load_dotenv
from flask import Flask
from db import db
from flask_migrate import Migrate
from flask_restful import Api

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///dev.db")
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

from router import register_routes
register_routes(api)

if __name__ == "__main__":
    app.run(debug=os.getenv("DEBUG", "True").lower() == "true")
```

Este archivo se ejecuta de arriba a abajo en este orden:

1. **`load_dotenv()`** — lee `.env` y mete las variables en el entorno. Después `os.getenv()` puede leerlas.
2. **`Flask(__name__)`** — crea la aplicación. El objeto `app` es tu servidor.
3. **`app.config[...]`** — configura la base de datos. La URL sale de `.env`. Si no hay `.env`, usa SQLite como fallback.
4. **`db.init_app(app)`** — conecta SQLAlchemy a Flask. Sin esto, los modelos no saben a qué app pertenecen.
5. **`Migrate(app, db)`** — prepara las migraciones. Te permite crear y modificar tablas sin perder datos.
6. **`Api(app)`** — inicializa Flask-RESTful. Es el motor que va a enrutar los requests a los Resources.
7. **`from router import register_routes`** — acá cargamos el router, que importa todo lo demás (resources, modelos, schemas). La posición de este import no es casual: necesitamos que `db`, `app` y `api` ya existan antes de que los modelos y resources se importen.
8. **`register_routes(api)`** — ejecuta la función que registra los endpoints. Le pasamos `api` para que pueda hacer `api.add_resource(...)` adentro.

**¿Por qué el import de `router` está después de crear `api`?** Porque `router/__init__.py` importa `from resources import UserResource`, y `resources/userResource.py` importa `from models.user import UserModel`. Cuando `UserModel` se define, necesita que `db` ya exista (hereda de `db.Model`). Como `db` se crea en la línea 7 y se inicializa en la 16, para cuando el modelo se importa (vía la cadena desde la línea 20), todo está listo.

---
## 4. `db.py` — la conexión a la base de datos

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

Cuatro líneas. Pero esta línea es la que usan **todos los modelos** para heredar (`db.Model`) y **todos los resources** para guardar (`db.session.add()`, `db.session.commit()`).

**¿Por qué está separado en su propio archivo?** Porque tanto `models/user.py` como `resources/userResource.py` necesitan importar `db`. Si estuviera en `app.py`, cualquiera de los dos tendría que hacer `from app import db`, lo que crearía un **import circular** cuando `app.py` intente importar el modelo. Al tener `db.py` separado, rompemos ese ciclo.

---
## 5. Modelos — cómo se ven los datos en la DB

### 5.1. El archivo del modelo

```python
# models/user.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
```

Un **modelo** es la representación en Python de una tabla de la base de datos. Cada atributo de clase (`id`, `username`, `email`) es una columna.

| Pieza | Qué hace |
|-------|----------|
| `db.Model` | Le dice a SQLAlchemy "esta clase es una tabla". Le da superpoderes: consultas (`UserModel.query.all()`), guardado, borrado. |
| `Mapped[int]` | Type hint moderno de SQLAlchemy 2.0. Le decís "esta columna es de tipo entero" y el IDE te autocompleta. |
| `mapped_column(Integer, primary_key=True)` | La configuración real de la columna: tipo de dato, restricciones. |
| `__tablename__` | El nombre que va a tener la tabla adentro de la base de datos. Si no lo ponés, SQLAlchemy usa el nombre de la clase. |

### 5.2. El `__init__.py` del paquete

```python
# models/__init__.py
from .user import UserModel
```

Este archivo exporta los modelos para que se puedan importar como `from models import UserModel`. Pero **no es necesario para que el modelo funcione**. Su propósito real es otro.

### 5.3. ⚠️ El auto-descubrimiento de modelos — lo que no se ve

Acá está el concepto que más cuesta entender:

> **SQLAlchemy descubre los modelos en el momento en que el archivo del modelo se importa y la clase se define.**

Cuando `resources/userResource.py` hace:

```python
from models.user import UserModel
```

Pasan dos cosas:
1. Python ejecuta `models/user.py` de arriba a abajo
2. Al ejecutar `class UserModel(db.Model):`, SQLAlchemy registra esa clase en su **metadata** (el catálogo interno de tablas)

Después, cuando ejecutás `flask db migrate`, SQLAlchemy compara su metadata contra la base de datos real y dice "ah, faltan estas tablas" y genera las instrucciones para crearlas.

**¿Qué significa esto en la práctica?** Que un modelo existe para SQLAlchemy **desde el momento en que alguien lo importa**. Si ningún archivo de tu app importa `models/user.py`, SQLAlchemy nunca se va a enterar de que existe, y `flask db migrate` no lo va a incluir.

Por eso en `resources/userResource.py` tenemos `from models.user import UserModel`. Ese import no solo sirve para usar `UserModel.query.all()`, sino que **también le dice a SQLAlchemy "este modelo existe, tenelo en cuenta"**.

La cadena completa de descubrimiento es:

```
app.py
  └─ from router import register_routes
       └─ import router/__init__.py
            └─ from resources import UserResource
                 └─ import resources/__init__.py → resources/userResource.py
                      └─ from models.user import UserModel  ← ACÁ se descubre
```

Cuando querás agregar un modelo nuevo, solo tenés que asegurarte de que se importe en algún punto de esta cadena. El lugar natural es `resources/userResource.py` (el resource que lo usa), pero también podés importarlo directamente en `app.py` como hacían las versiones anteriores.

---
## 6. Schemas — la validación que no escribís a mano

```python
# schemas/user.py
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
```

Un **schema** de Pydantic tiene dos trabajos:

**Validar entrada** (`UserCreate`): cuando el cliente hace POST, esperamos que mande `username` y `email`. Si falta uno, Pydantic lanza un error. Si manda un campo de más, Pydantic lo ignora (a menos que lo configuremos para que lo rechace). No necesitás escribir un solo `if` de validación.

**Serializar salida** (`UserResponse`): cuando devolvemos datos al cliente, Pydantic se asegura de que la respuesta siempre tenga exactamente los campos que esperamos. Convertís un objeto `UserModel` (de SQLAlchemy) a un diccionario con `UserResponse.model_validate(user).model_dump()`.

**¿Por qué dos clases separadas?** Porque el `id` lo genera la base de datos, no el cliente. Si usaras el mismo schema para entrada y salida, el cliente podría mandar un `id` que no le corresponde o, peor, sobreescribir un registro existente. Separarlos evita eso.

El `__init__.py` del paquete `schemas` exporta los schemas igual que `models` exporta los modelos:

```python
# schemas/__init__.py
from .user import UserCreate, UserResponse
```

---
## 7. Resources — la lógica del endpoint

```python
# resources/userResource.py
from flask_restful import Resource
from flask import request
from pydantic import ValidationError
from db import db
from models.user import UserModel
from schemas.user import UserCreate, UserResponse


class UserResource(Resource):
    def get(self):
        users = UserModel.query.all()
        return [UserResponse.model_validate(u).model_dump() for u in users], 200

    def post(self):
        try:
            data = UserCreate(**request.get_json())
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        if UserModel.query.filter_by(username=data.username).first():
            return {"msg": "El nombre de usuario ya existe"}, 409

        if UserModel.query.filter_by(email=data.email).first():
            return {"msg": "El correo ya existe"}, 409

        user = UserModel(username=data.username, email=data.email)
        db.session.add(user)
        db.session.commit()

        return UserResponse.model_validate(user).model_dump(), 201
```

Un **Resource** es una clase que agrupa toda la lógica de un endpoint. Cada método HTTP (GET, POST, PUT, DELETE) se convierte en un método de la clase.

**GET /api/users**:
1. `UserModel.query.all()` → trae todos los usuarios de la base de datos
2. `UserResponse.model_validate(u).model_dump()` → convierte cada usuario de SQLAlchemy a JSON
3. Devuelve la lista con código 200

**POST /api/users**:
1. `UserCreate(**request.get_json())` → toma el JSON del body y lo valida con Pydantic
2. Si falla la validación → devuelve 400 con los errores
3. Verifica que el username no exista → si existe, devuelve 409 Conflict
4. Verifica que el email no exista → si existe, devuelve 409 Conflict
5. Crea el `UserModel`, lo agrega a la sesión, hace commit
6. Devuelve el usuario creado con código 201

**¿Qué es `model_validate` y `model_dump`?**
- `UserResponse.model_validate(user)` → toma un objeto `UserModel` y lo convierte al schema de respuesta. Pydantic extrae los campos automáticamente (encuentra el `id`, `username`, `email` del objeto SQLAlchemy).
- `.model_dump()` → convierte ese schema validado a un diccionario que Flask puede devolver como JSON.

### El `__init__.py` del paquete `resources`

```python
# resources/__init__.py
from .userResource import UserResource
```

Al igual que con los modelos, este archivo exporta los resources. Pero también juega un papel en el auto-descubrimiento.

### ⚠️ Cómo se registra un resource automáticamente

Cuando `router/__init__.py` hace:

```python
from flask_restful import Api
from resources import UserResource

def register_routes(api: Api):
    api.add_resource(UserResource, "/api/users")
```

Pasa esto:

1. `from resources import UserResource` ejecuta `resources/__init__.py`, que ejecuta `from .userResource import UserResource`, que ejecuta **todo** `resources/userResource.py`.
2. Al ejecutar `resources/userResource.py`, se importan los modelos (`UserModel`), los schemas (`UserCreate`, `UserResponse`), y se define la clase `UserResource`.
3. `api.add_resource(UserResource, "/api/users")` registra la clase en Flask-RESTful. A partir de ese momento, cualquier request a `/api/users` va a ser manejado por `UserResource`.

El resource **no se registra solo** — hay que llamar a `api.add_resource()` explícitamente. Pero una vez que lo hacés, no necesitás tocar ningún otro archivo. Flask-RESTful se encarga del enrutamiento automáticamente.

---
## 8. Router — el mapa del restaurante

```python
# router/__init__.py
from flask_restful import Api
from resources import UserResource

def register_routes(api: Api):
    api.add_resource(UserResource, "/api/users")
```

Este archivo es el **mapa** que conecta URLs con Resources. `api.add_resource(UserResource, "/api/users")` le dice a Flask-RESTful: "cuando alguien entre a `/api/users`, ejecutá `UserResource`".

Cada vez que agregás un resource nuevo, volvés acá y agregás una línea:

```python
api.add_resource(UserResource, "/api/users")
api.add_resource(ProductoResource, "/api/productos")
api.add_resource(PedidoResource, "/api/pedidos")
```

**¿Por qué `register_routes` es una función y no se ejecuta directamente?** Porque en `app.py` necesitamos pasarle `api` como parámetro. `api` se crea en `app.py` (es `Api(app)`) y se pasa a `register_routes`. Si `router/__init__.py` importara `api` directamente desde `app.py`, tendríamos un import circular.

---
## 9. Utils — código que se repite

```python
# utils/helpers.py
def paginate(query, page=1, per_page=10):
    items = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "total": items.total,
        "page": items.page,
        "per_page": items.per_page,
        "pages": items.pages,
        "data": [
            {"id": item.id, **{c.name: getattr(item, c.name) for c in item.__table__.columns if c.name != "id"}}
            for item in items.items
        ],
    }
```

Acá van funciones que usás en varios resources. Si empezás a copiar y pegar el mismo código en varios lados, movelo acá.

El ejemplo `paginate()` sirve para cuando tenés muchos registros y querés devolverlos en páginas (por ejemplo, de a 10 por vez, con un link a la página siguiente). No se importa en ningún lado automáticamente — lo importás en el resource que lo necesite:

```python
from utils.helpers import paginate
```

---
## 10. `.env` — configuración que cambia según el entorno

```env
DATABASE_URL=sqlite:///dev.db
DEBUG=True
```

Las variables de entorno separan la **configuración** del **código**. En tu compu usás SQLite (no requiere instalación). Cuando el proyecto sube a un servidor, cambiás `DATABASE_URL` a PostgreSQL. El código es el mismo, lo único que cambia es este archivo.

**¿Por qué no hardcodear la URL en `app.py`?** Porque la URL de producción es distinta a la de desarrollo, y probablemente el que deploya no es el que escribe el código. Si está en `.env`, cada uno pone la suya sin tocar una línea de Python.

El archivo `.env` **no se sube al repositorio** (está en `.gitignore`). Por eso existe `.env.copy` — es una plantilla para que cualquiera que clone el proyecto sepa qué variables necesita crear.

---
## 11. Cómo agregar una entidad nueva — el walkthrough completo

Vamos a agregar `Producto` como ejemplo. Son 6 pasos.

### Paso 1: Crear el modelo → `models/producto.py`

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from db import db


class ProductoModel(db.Model):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
```

Después lo exportás en `models/__init__.py`:

```python
from .user import UserModel
from .producto import ProductoModel
```

**¿Qué pasa si no lo exportás en `__init__.py`?** Nada, el modelo igual se descubre cuando algún resource lo importe directamente con `from models.producto import ProductoModel`. El `__init__.py` es solo para centralizar imports.

### Paso 2: Crear el schema Pydantic → `schemas/producto.py`

```python
from pydantic import BaseModel


class ProductoCreate(BaseModel):
    nombre: str
    precio: float


class ProductoResponse(BaseModel):
    id: int
    nombre: str
    precio: float
```

Exportalo en `schemas/__init__.py`:

```python
from .user import UserCreate, UserResponse
from .producto import ProductoCreate, ProductoResponse
```

### Paso 3: Crear el resource → `resources/productoResource.py`

```python
from flask_restful import Resource
from flask import request
from pydantic import ValidationError
from db import db
from models.producto import ProductoModel
from schemas.producto import ProductoCreate, ProductoResponse


class ProductoResource(Resource):
    def get(self):
        productos = ProductoModel.query.all()
        return [ProductoResponse.model_validate(p).model_dump() for p in productos], 200

    def post(self):
        try:
            data = ProductoCreate(**request.get_json())
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        producto = ProductoModel(**data.model_dump())
        db.session.add(producto)
        db.session.commit()

        return ProductoResponse.model_validate(producto).model_dump(), 201
```

Exportalo en `resources/__init__.py`:

```python
from .userResource import UserResource
from .productoResource import ProductoResource
```

### Paso 4: Registrar la ruta → `router/__init__.py`

```python
from flask_restful import Api
from resources import UserResource, ProductoResource


def register_routes(api: Api):
    api.add_resource(UserResource, "/api/users")
    api.add_resource(ProductoResource, "/api/productos")
```

### Paso 5: Migrar y correr

```bash
flask db migrate -m "crear tabla productos"
flask db upgrade
python app.py
```

**¿Qué hace `flask db migrate`?** SQLAlchemy compara su metadata (los modelos que están importados) contra la base de datos real. Si encuentra diferencias (la tabla `productos` no existe), genera un archivo de migración con las instrucciones SQL para crearla.

**¿Qué hace `flask db upgrade`?** Ejecuta esas instrucciones contra la base de datos. Crea la tabla.

**¿Qué pasa si olvidaste importar `ProductoModel` en algún lado?** `flask db migrate` no va a encontrar la tabla `productos` en la metadata y no la va a generar. El modelo existe en tu código, pero SQLAlchemy no sabe de él. Ese es el error más común al agregar una entidad nueva — asegurate de que el modelo esté siendo importado en la cadena de imports de tu app.

### Paso 6: Probar

```bash
# GET — lista vacía
curl http://127.0.0.1:5000/api/productos

# POST — crear producto
curl -X POST http://127.0.0.1:5000/api/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Hamburguesa", "precio": 12.50}'
```

---
## 12. PostgreSQL / MySQL — cambiá de base sin cambiar código

El boilerplate viene con SQLite por defecto porque no requiere instalación. Pero en producción (y en proyectos del bootcamp) vas a usar PostgreSQL.

### PostgreSQL

Primero necesitás tener PostgreSQL instalado y corriendo en tu máquina.

1. **Instalación:**
   - **Windows**: descargá el instalador desde [postgresql.org/download](https://www.postgresql.org/download/) y ejecutalo. Durante la instalación te pide una contraseña para el usuario `postgres` — **no la olvides**.
   - **Linux (Ubuntu/Debian)**: `sudo apt install postgresql postgresql-contrib`
   - **Mac**: `brew install postgresql@17`

2. **Crear la base de datos:**
   ```bash
   # Desde terminal
   createdb -U postgres mi_db
   ```
   O desde pgAdmin: click derecho en Databases → Create → Database → nombre: `mi_db`.

3. **Cambiar la URL en `.env`:**
   ```env
   DATABASE_URL=postgresql://postgres:tu_contraseña@localhost:5432/mi_db
   ```
   Donde:
   - `postgresql://` → el protocolo
   - `postgres:tu_contraseña` → usuario : contraseña (la que pusiste al instalar)
   - `@localhost:5432` → dirección y puerto de PostgreSQL
   - `/mi_db` → el nombre de la base de datos que creaste

4. **Asegurate de tener el driver instalado.** El `requirements.txt` ya incluye `psycopg2-binary`, así que si hiciste `pip install -r requirements.txt`, ya lo tenés.

5. **Corré las migraciones de nuevo** (si ya tenés datos en SQLite, empezá de cero):
   ```bash
   flask db upgrade
   ```

### MySQL

1. Instalá MySQL desde [dev.mysql.com/downloads](https://dev.mysql.com/downloads/)
2. Instalá el driver: `pip install pymysql`
3. Agregalo a `requirements.txt`
4. Cambiá la URL en `.env`:
   ```env
   DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/mi_db
   ```

**¿Por qué el código no cambia?** Porque SQLAlchemy es una **capa de abstracción**. El ORM traduce tus modelos de Python a SQL, sin importar si el motor es SQLite, PostgreSQL, MySQL o SQL Server. Cambiás la URL, corrés `flask db upgrade`, y el mismo código funciona en todas. Ese es el poder de SQLAlchemy.

---
## 13. Recorrido completo: ¿qué pasa cuando hacés GET /api/users?

```
Cliente                        Servidor
  │                               │
  │  GET /api/users                │
  │──────────────────────────────>│
  │                               │
  │                      Flask recibe el request
  │                      Flask-RESTful busca la ruta /api/users
  │                      Encuentra UserResource
  │                      Llama a UserResource.get()
  │                      UserModel.query.all() → consulta SQL a la DB
  │                      Pydantic convierte cada UserModel a UserResponse
  │                      model_dump() convierte UserResponse a dict
  │                      Flask convierte el dict a JSON
  │                               │
  │  200 OK  [{...}, {...}]       │
  │<──────────────────────────────│
```

## Recorrido completo: ¿qué pasa cuando hacés POST /api/users?

```
Cliente                        Servidor
  │                               │
  │  POST /api/users               │
  │  {"username": "jperez",        │
  │   "email": "jperez@mail.com"}  │
  │──────────────────────────────>│
  │                               │
  │                      Flask-RESTful llama a UserResource.post()
  │                      request.get_json() → extrae el JSON del body
  │                      UserCreate(**request.get_json()) → Pydantic valida
  │                      Si falta un campo → ValidationError → 400
  │                      Si el username ya existe → 409 Conflict
  │                      Si el email ya existe → 409 Conflict
  │                      Crea UserModel(username=..., email=...)
  │                      db.session.add(user) → lo marca para guardar
  │                      db.session.commit() → ejecuta INSERT en la DB
  │                      UserResponse.model_validate(user) → convierte a schema
  │                      model_dump() → convierte a dict
  │                               │
  │  201 CREATED  {id:1, ...}     │
  │<──────────────────────────────│
```

---
## 14. Referencia rápida

| Comando | Qué hace |
|---------|----------|
| `flask db init` | Crea la carpeta `migrations/` con la configuración inicial (solo una vez) |
| `flask db migrate -m "mensaje"` | Compara los modelos contra la DB y genera una migración con los cambios |
| `flask db upgrade` | Aplica las migraciones pendientes a la base de datos |
| `flask db downgrade` | Deshace la última migración |
| `flask db current` | Muestra en qué migración estás parado |
| `flask db history` | Muestra el historial completo de migraciones |
| `python app.py` | Corre el servidor |

```
Para agregar una entidad nueva, el flujo es siempre el mismo:

  1. Crear el modelo      → models/producto.py
  2. Exportarlo           → models/__init__.py
  3. Crear el schema      → schemas/producto.py
  4. Exportarlo           → schemas/__init__.py
  5. Crear el resource    → resources/productoResource.py
  6. Exportarlo           → resources/__init__.py
  7. Registrar la ruta    → router/__init__.py (api.add_resource)
  8. Migrar               → flask db migrate + flask db upgrade
  9. Correr               → python app.py
```
