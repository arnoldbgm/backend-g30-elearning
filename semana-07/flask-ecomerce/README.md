# Flask Boilerplate

API REST con Flask + SQLAlchemy 2.0 + Pydantic + Flask-RESTful.

---

## ¿Qué incluye?

| Capa | Tecnología | Responsabilidad |
|------|-----------|-----------------|
| Modelos | SQLAlchemy 2.0 (Mapped, mapped_column) | Definición de tablas y tipos |
| Schemas | Pydantic v2 | Validación de entrada/salida sin escribir `if` |
| Recursos | Flask-RESTful | Lógica CRUD por endpoint |
| Rutas | Router propio | Mapeo URL → Resource sin acoplar rutas |
| Base de datos | Flask-SQLAlchemy + Migrate | Migraciones automáticas, DB-swap sin cambiar código |
| Configuración | python-dotenv + `.env` | Entornos separados sin tocar código |

**Ventajas:** capas desacopladas, imports sin circulares, migraciones desde el día 1, cambiar de SQLite a PostgreSQL cambiando una línea, validación automática con Pydantic, y un flujo repetible para agregar entidades.

---

## 1. Quick Start

```bash
git clone https://github.com/tu-usuario/flask-boilerplate.git
cd flask-boilerplate

python -m venv venv

# Windows:
venv\Scripts\activate
# Linux / Mac:
source venv/bin/activate

pip install -r requirements.txt
flask db init
flask db migrate -m "crear tabla users"
flask db upgrade
python app.py
```

Abrí http://localhost:5000/api/users en el navegador.

---

## 2. Referencia rápida

| Comando | Qué hace |
|---------|----------|
| `flask db init` | Crea `migrations/` (una vez) |
| `flask db migrate -m "msg"` | Genera migración desde los modelos |
| `flask db upgrade` | Aplica migraciones pendientes |
| `flask db downgrade` | Deshace la última |
| `flask db current` | Muestra migración actual |
| `flask db history` | Historial completo |
| `python app.py` | Inicia el servidor |

---

## 3. Estructura

```
flask-boilerplate/
├── models/          ← Tablas de la DB (SQLAlchemy)
├── schemas/         ← Validación entrada/salida (Pydantic)
├── resources/       ← Lógica de cada endpoint (Flask-RESTful)
├── router/          ← Mapeo URL → Resource
├── utils/           ← Código reutilizable entre resources
├── db.py            ← Instancia de SQLAlchemy
├── app.py           ← Punto de entrada
├── .env             ← Config local (no se sube)
└── requirements.txt
```

Cada capa tiene una responsabilidad única. Los imports siguen esta cadena:

```
app.py → router/ → resources/ → models/ (ahí se descubre el modelo)
```

---

## 4. Cómo agregar una entidad nueva

Agregar `Producto` como ejemplo:

### 4.1 Modelo → `models/producto.py`

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

Exportar en `models/__init__.py`:

```python
from .user import UserModel
from .producto import ProductoModel
```

### 4.2 Schema → `schemas/producto.py`

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

Exportar en `schemas/__init__.py`:

```python
from .user import UserCreate, UserResponse
from .producto import ProductoCreate, ProductoResponse
```

### 4.3 Resource → `resources/productoResource.py`

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

Exportar en `resources/__init__.py`:

```python
from .userResource import UserResource
from .productoResource import ProductoResource
```

### 4.4 Ruta → `router/__init__.py`

```python
from flask_restful import Api
from resources import UserResource, ProductoResource


def register_routes(api: Api):
    api.add_resource(UserResource, "/api/users")
    api.add_resource(ProductoResource, "/api/productos")
```

### 4.5 Migrar

```bash
flask db migrate -m "crear tabla productos"
flask db upgrade
python app.py
```

### 4.6 Probar

Andá a http://localhost:5000/api/productos.

> **Si `flask db migrate` no genera la tabla**: el modelo no se está importando en la cadena de imports. Asegurate de que `resources/productoResource.py` haga `from models.producto import ProductoModel`.

---

## 5. Componentes

### 5.1 `app.py` — punto de entrada

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

Orden: `load_dotenv()` → `Flask()` → `config DB` → `db.init_app()` → `Migrate()` → `Api()` → import router → `register_routes(api)`.

El import de router va al final porque necesita que `db`, `app` y `api` ya existan antes de que los modelos se carguen.

### 5.2 `db.py` — conexión a DB

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

Separado en su propio archivo para evitar imports circulares: tanto `models/` como `resources/` lo necesitan.

### 5.3 Modelos (`models/`) — tablas en Python

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
```

SQLAlchemy descubre los modelos cuando se importa el archivo de la clase. Si ningún archivo lo importa, `flask db migrate` no lo incluye.

### 5.4 Schemas (`schemas/`) — validación con Pydantic

```python
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
```

Dos clases separadas: `UserCreate` valida entrada (sin `id`), `UserResponse` serializa salida (con `id`). Pydantic rechaza campos faltantes y parsea `request.get_json()` automáticamente.

### 5.5 Resources (`resources/`) — lógica del endpoint

```python
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

Cada método HTTP es un método de la clase. `model_validate()` convierte SQLAlchemy → Pydantic, `model_dump()` convierte a dict.

### 5.6 Router (`router/`) — mapeo URL → Resource

```python
from flask_restful import Api
from resources import UserResource


def register_routes(api: Api):
    api.add_resource(UserResource, "/api/users")
```

Es una función (no ejecución directa) para evitar import circular con `app.py`.

### 5.7 Utils (`utils/`) — código compartido

```python
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

Se importa donde se necesite: `from utils.helpers import paginate`.

### 5.8 `.env` — configuración por entorno

```
DATABASE_URL=sqlite:///dev.db
DEBUG=True
```

No se sube al repo (está en `.gitignore`). `.env.copy` es la plantilla.

---

## 6. Cambiar de base de datos

### PostgreSQL

```bash
# Instalar (ej. Ubuntu)
sudo apt install postgresql postgresql-contrib
createdb -U postgres mi_db
```

```env
DATABASE_URL=postgresql://postgres:tu_contraseña@localhost:5432/mi_db
```

`psycopg2-binary` ya está en `requirements.txt`.

### MySQL

```bash
pip install pymysql
```

```env
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/mi_db
```

SQLAlchemy abstrae el motor. Cambiás la URL, correés `flask db upgrade`, y el mismo código funciona.

---

## 7. Troubleshooting

| Problema | Causa | Solución |
|----------|-------|----------|
| `flask: command not found` | No se activó el venv o no se instalaron deps | `source venv/bin/activate && pip install -r requirements.txt` |
| `flask db migrate` no genera la tabla | El modelo no se importa en la cadena | Verificá que el resource importe el modelo |
| `ImportError: cannot import name` | Import circular | Asegurate que `db` esté en `db.py`, no en `app.py` |
| Puerto 5000 en uso | Otra app corriendo | Cambiá el puerto o matá el proceso |
| `psycopg2` no se instala | Falta librería del sistema | `sudo apt install libpq-dev` (Linux) o usá `pip install psycopg2-binary` |

---
