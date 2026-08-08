# Guía — Día 1 (Semana 7): Empezamos el E-Commerce 🛒

<img width="1434" height="788" alt="image" src="https://github.com/user-attachments/assets/a843bece-0ffc-41ee-a8c9-229242ec2c5f" />


Hoy arrancamos el proyecto más grande del curso: una **API REST de e-commerce**. En las próximas 4 sesiones vamos a construir una tienda online de verdad, con usuarios, autenticación, productos con imágenes en la nube, y ventas con facturación electrónica.

¿El objetivo de hoy? Que tu proyecto quede parado, conectado a PostgreSQL, con sus primeras 2 tablas y su primer CRUD funcionando.

**Lo que vas a lograr hoy:**
- Un proyecto Flask-RESTful con estructura profesional (flat, estilo boilerplate)
- 2 tablas en PostgreSQL: `roles` y `categorias`
- El CRUD completo de Categorías (y Roles) probado en Postman

---

## El plan completo (para que sepas a dónde vamos)

| Sesión | Qué vamos a construir |
|--------|----------------------|
| **Hoy** | Setup + tablas `roles` y `categorias` + CRUD Categorías |
| 07 Día 2 | Usuarios + Login con JWT + Roles protegidos |
| 08 Día 1 | Productos con imágenes en Cloudinary |
| 08 Día 2 | Clientes, Ventas con IGV y facturación en Nubefact |

**Analogía:** hoy vamos a construir los cimientos y las primeras paredes de la tienda. Sin cimientos sólidos, no hay tienda que valga.

---

## 1. Setup del proyecto (15 min)

### 1A — Copiar el boilerplate

En el curso tenemos una plantilla lista, `flask-boilerplate`, con la estructura base ya armada. En vez de crear todo desde cero, la copiamos y la renombramos.

Copiá la carpeta `flask-boilerplate` y renombrala como `flask-ecomerce`.

### 1B — Entorno virtual

Abran una terminal dentro de `flask-ecomerce`:

```bash
python -m venv venv
venv\Scripts\activate
```

Recuerden: el entorno virtual es como ponerse una casaca que dice "todo lo que instale ahora es solo para este proyecto". Así no se mezclan versiones entre proyectos.

### 1C — Dependencias

Crear el archivo `requirements.txt`:

```
Flask==3.1.3
Flask-Migrate==4.1.0
Flask-RESTful==0.3.10
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.48
pydantic==2.12.5
python-dotenv==1.2.2
psycopg2-binary==2.9.12
```

```bash
pip install -r requirements.txt
```

**¿Qué instalamos?**

| Paquete | ¿Para qué? |
|---------|------------|
| `Flask` | El microframework web |
| `Flask-RESTful` | Organizar endpoints en clases `Resource` |
| `Flask-SQLAlchemy` | ORM para la base de datos |
| `Flask-Migrate` | Migraciones de la BD sin perder datos |
| `pydantic` | Validación de datos con schemas |
| `python-dotenv` | Cargar variables del archivo `.env` |
| `psycopg2-binary` | Driver para conectarnos a PostgreSQL |

**OJO:** cada sesión vamos a AGREGAR paquetes a este archivo. Hoy es lo mínimo.

---

## 2. Configuración: `.env` y la base de datos (10 min)

### 2A — El archivo `.env`

Crear el archivo `.env` en la raíz del proyecto:

```
DATABASE_URL=postgresql://postgres:root@localhost:5432/flask-ecommerce
DEBUG=True
```

**Analogía:** `.env` es la bóveda de secretos de tu proyecto. Ahí viven las contraseñas y URLs de conexión que NO quieres que nadie vea.

También crear `.env.copy` (la plantilla pública, sin secretos reales):

```
DATABASE_URL=postgresql://postgres:TU_PASSWORD@localhost:5432/flask-ecommerce
DEBUG=True
```

**Regla de oro:** `.env` nunca se sube al repositorio (ya está en `.gitignore`). `.env.copy` es lo que compartís para que otros sepan qué variables necesitan.

### 2B — Crear la base de datos

En pgAdmin:
1. Click derecho en **Databases** → **Create** → **Database...**
2. Nombre: `flask-ecommerce`
3. Owner: `postgres`

**CUIDADO:** el nombre lleva guion (`flask-ecommerce`), no usen espacios ni mayúsculas.

---

## 3. La estructura del proyecto (10 min)

¿Por qué empezamos viendo la estructura? Porque en este curso no escribimos código al azar: **la estructura te dice dónde va cada cosa**.

```
flask-ecomerce/
├── app.py                  ← Configuración + punto de entrada
├── db.py                   ← Instancia de SQLAlchemy
├── requirements.txt
├── .env / .env.copy
├── migrations/             ← Migraciones
├── models/                 ← Modelos SQLAlchemy
├── schemas/                ← Schemas de Pydantic
├── resources/              ← Lógica de cada endpoint
└── router/
    └── __init__.py         ← Registro de rutas
```

**Analogía:** es como un restaurante con estaciones. Cada estación tiene su función: la cocina (models), el despacho (schemas), y la atención al cliente (resources). El `router` es el menú: la lista de qué se sirve en cada mesa.

**La convención que vamos a repetir SIEMPRE:**

| Concepto | Cómo se llama |
|----------|---------------|
| Modelo | `RoleModel`, `CategoryModel` |
| Schema de entrada | `RoleCreate`, `CategoryCreate` |
| Schema de salida | `RoleResponse`, `CategoryResponse` |
| Resource | `roleResource.py`, `categoryResource.py` |

Si aprendes esto, vas a poder agregar entidades nuevas sin pensar dos veces.

---

## 4. db.py y app.py (15 min)

### db.py

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

Así de simple. Este `db` lo vamos a importar en TODOS los modelos y resources.

### app.py

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

**Desglose línea por línea:**

| Línea | ¿Qué hace? |
|-------|-----------|
| `load_dotenv()` | Lee el archivo `.env` y pone las variables disponibles |
| `os.getenv("DATABASE_URL", "sqlite:///dev.db")` | Trae la URL de la BD desde `.env`. Si no existe, usa SQLite (el plan B) |
| `db.init_app(app)` | Conecta SQLAlchemy con Flask |
| `migrate = Migrate(app, db)` | Activa las migraciones |
| `api = Api(app)` | Activa Flask-RESTful |
| `register_routes(api)` | Carga las rutas que definamos en `router/` |

**El punto clave de esta sesión:** la URL de la base de datos NO está escrita en el código. Vive en `.env`. ¿Por qué es tan importante? Porque así, el mismo código corre en tu laptop y en un servidor de producción: solo cambias el `.env`. Eso es lo que hacen las empresas de verdad.

---

## 5. Los modelos Role y Category (25 min)

Usamos la sintaxis de SQLAlchemy 2.0 que vimos en la semana 6 (`Mapped[]` + `mapped_column`). La novedad: la clase se llama con el sufijo `Model` (ej: `RoleModel`) para que no se confunda con el schema de Pydantic (`RoleCreate`).

### models/role.py

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from db import db


class RoleModel(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(200), nullable=False)

    __tablename__ = "roles"
```

### models/category.py

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from db import db


class CategoryModel(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(200), nullable=False)

    __tablename__ = "categorias"
```

**Desglose:**

| Línea | ¿Qué define? |
|-------|-------------|
| `id: Mapped[int] = mapped_column(Integer, primary_key=True)` | Llave primaria entera |
| `nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)` | Texto, ÚNICO y obligatorio |
| `descripcion: Mapped[str] = mapped_column(String(200), nullable=False)` | Texto, obligatorio |
| `__tablename__ = "roles"` | El nombre de la tabla en PostgreSQL (en plural) |

**¿Por qué `unique=True`?** Porque en el mundo real no pueden existir dos roles "admin" ni dos categorías "Tecnología". La base de datos te protege de eso. Después, en el resource, validamos el duplicado ANTES de llegar a la BD, para responder con un mensaje claro (código 409) en vez de un error feo.

### models/__init__.py

```python
from .role import RoleModel
from .category import CategoryModel
```

**¿Para qué?** Para que SQLAlchemy y Flask-Migrate "descubran" los modelos. **Regla:** cada modelo nuevo que crees, lo importas acá. Si no lo importas, la migración no lo va a ver.

---

## 6. Los schemas de Pydantic (20 min)

¿Recuerdan cuando validaban campo por campo con `if "nombre" not in data`? Con Pydantic eso se acaba. Cada schema define qué esperamos y qué devolvemos.

### schemas/role.py

```python
from pydantic import BaseModel, ConfigDict


class RoleCreate(BaseModel):
    nombre: str
    descripcion: str


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str
```

### schemas/category.py

```python
from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    nombre: str
    descripcion: str


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str
```

**Dos clases por schema, ¿por qué?**

| Clase | ¿Qué valida? | ¿Cuándo se usa? |
|-------|--------------|-----------------|
| `RoleCreate` | Datos que llegan del cliente | POST y PUT |
| `RoleResponse` | Datos que devolvemos | GET (y respuestas de POST/PUT) |

**`ConfigDict(from_attributes=True)`** es la pieza mágica: le dice a Pydantic que puede leer directamente los atributos de un modelo SQLAlchemy. Sin esto, `model_validate(categoria)` fallaría. (Es un bug clásico de pydantic v2, por eso lo configuramos explícitamente.)

### schemas/__init__.py

```python
from .role import RoleCreate, RoleResponse
from .category import CategoryCreate, CategoryResponse
```

---

## 7. Migración inicial (20 min)

Con los modelos creados, le pedimos a Flask-Migrate que los convierta en tablas reales.

```bash
# 1. Crear la carpeta migrations/
flask db init

# 2. Generar la migración
flask db migrate -m "migracion inicial"

# 3. Aplicar a la base de datos
flask db upgrade
```

**¿Qué hace cada comando?**

| Comando | ¿Qué hace? |
|---------|-----------|
| `flask db init` | Crea la carpeta `migrations/` (una sola vez) |
| `flask db migrate` | Compara los modelos con la BD y genera un script de migración |
| `flask db upgrade` | Ejecuta ese script: crea las tablas en PostgreSQL |

**Analogía:** el `migrate` es el arquitecto que dibuja el plano de la casa. El `upgrade` es el albañil que la construye siguiendo el plano.

### Verificar

En la Query Tool de pgAdmin, sobre la BD `flask-ecommerce`:

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';
```

Debe aparecer: `alembic_version`, `roles`, `categorias`.

---

## 8. CRUD de Categorías (45 min) — el corazón de la sesión

### 8A — La decisión de diseño

En este proyecto usamos **un solo Resource por entidad**. Los 4 métodos (`get`, `post`, `put`, `delete`) viven en la misma clase. Y una decisión importante: el `id` para actualizar/borrar viaja en el **body del JSON**, no en la URL.

¿Por qué? Porque así el endpoint es el mismo para todo: `POST/PUT/DELETE /api/categorias`. Simple y consistente.

### 8B — El código

Crear `resources/categoryResource.py`:

```python
from flask_restful import Resource
from flask import request
from pydantic import ValidationError
from db import db
from models.category import CategoryModel
from schemas.category import CategoryCreate, CategoryResponse


class CategoryResource(Resource):
    def get(self):
        categorias = CategoryModel.query.all()
        return [CategoryResponse.model_validate(c).model_dump(mode="json") for c in categorias], 200

    def post(self):
        try:
            data = CategoryCreate(**request.get_json())
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        if CategoryModel.query.filter_by(nombre=data.nombre).first():
            return {"msg": "La categoría ya existe"}, 409

        categoria = CategoryModel(nombre=data.nombre, descripcion=data.descripcion)
        db.session.add(categoria)
        db.session.commit()

        return CategoryResponse.model_validate(categoria).model_dump(mode="json"), 201

    def put(self):
        data = request.get_json()
        categoria = db.session.get(CategoryModel, data.get("id"))
        if not categoria:
            return {"msg": "Categoría no encontrada"}, 404

        try:
            validated = CategoryCreate(**data)
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        categoria.nombre = validated.nombre
        categoria.descripcion = validated.descripcion
        db.session.commit()

        return CategoryResponse.model_validate(categoria).model_dump(mode="json"), 200

    def delete(self):
        data = request.get_json()
        categoria = db.session.get(CategoryModel, data.get("id"))
        if not categoria:
            return {"msg": "Categoría no encontrada"}, 404

        db.session.delete(categoria)
        db.session.commit()

        return {"msg": "Categoría eliminada"}, 200
```

### 8C — Desglose método por método

**`get()` — listar todas:**

| Línea | ¿Qué hace? |
|-------|-----------|
| `CategoryModel.query.all()` | Trae todas las categorías de la BD |
| `CategoryResponse.model_validate(c)` | Convierte cada modelo SQLAlchemy en un response de Pydantic |
| `.model_dump(mode="json")` | Lo convierte a diccionario serializable como JSON |
| `, 200` | Código HTTP: todo OK |

**`post()` — crear:**

1. `CategoryCreate(**request.get_json())` valida el JSON recibido. Si falla → `ValidationError` → **400** con los errores.
2. Verificamos que no exista una categoría con ese nombre → si existe → **409** ("conflicto").
3. Creamos el modelo, lo agregamos a la sesión (`add`) y guardamos (`commit`).
4. Respondemos el objeto creado con **201** (created).

**`put()` — actualizar:**

1. Leemos el `id` del body y buscamos la categoría con `db.session.get(CategoryModel, id)`.
2. Si no existe → **404**.
3. Validamos el resto de campos con `CategoryCreate` → **400** si falla.
4. Actualizamos campo por campo, `commit`, y devolvemos con **200**.

**`delete()` — borrar:**

1. Buscamos por `id` del body → **404** si no existe.
2. `db.session.delete(categoria)` + `commit`.
3. Devolvemos mensaje de confirmación.

**Los códigos HTTP que usamos (memorizalos):**

| Código | Significado |
|--------|-------------|
| `200` | OK |
| `201` | Creado |
| `400` | Datos inválidos (no pasó la validación) |
| `404` | No encontrado |
| `409` | Conflicto (ya existe) |

### 8D — Registrar la ruta

Crear `resources/__init__.py`:

```python
from .categoryResource import CategoryResource
from .roleResource import RoleResource
```

Crear `router/__init__.py`:

```python
from flask_restful import Api
from resources import CategoryResource, RoleResource


def register_routes(api: Api):
    api.add_resource(CategoryResource, "/api/categorias")
    api.add_resource(RoleResource, "/api/roles")
```

**¿Por qué `resources/__init__.py` y `router/__init__.py`?** Porque el router importa los resources desde el paquete `resources`. Los `__init__.py` son los que permiten importar así: `from resources import CategoryResource`.

---

## 9. Pruebas en Postman (30 min)

**IMPORTANTE:** todo endpoint se prueba en Postman apenas se crea. Postman es nuestra herramienta principal.

Ejecutar `python app.py` y confirmar que el servidor arranca.

### Crear una categoría (POST)

- Método: **POST**
- URL: `http://127.0.0.1:5000/api/categorias`
- Body → raw → JSON:

```json
{
    "nombre": "Tecnología",
    "descripcion": "Productos de tecnología"
}
```

- Send → Debe devolver la categoría con `id: 1` y código **201**

### Listar (GET)

- Método: **GET**
- URL: `http://127.0.0.1:5000/api/categorias`
- Send → Debe devolver la lista con la categoría creada

### Actualizar (PUT)

- Método: **PUT**
- URL: `http://127.0.0.1:5000/api/categorias`
- Body:

```json
{
    "id": 1,
    "nombre": "Tecnología y gadgets",
    "descripcion": "Celulares, laptops y accesorios"
}
```

- Send → Debe devolver la categoría actualizada

### Eliminar (DELETE)

- Método: **DELETE**
- URL: `http://127.0.0.1:5000/api/categorias`
- Body: `{"id": 1}`
- Send → Debe devolver `{"msg": "Categoría eliminada"}`

### Probar los errores (¡también hay que probar los errores!)

| Prueba | Resultado esperado |
|--------|--------------------|
| POST sin `nombre` | **400** con el detalle de `errores` |
| POST con nombre repetido | **409** "La categoría ya existe" |
| PUT con `id: 999` | **404** "Categoría no encontrada" |
| POST con `nombre: 123` | **400** (Pydantic valida el tipo) |

---

## 10. CRUD de Roles (20 min)

¿Viste el patrón de Categorías? Ahora lo repetimos para Roles. Es EXACTAMENTE el mismo código, cambiando los nombres de los modelos y schemas.

Crear `resources/roleResource.py`:

```python
from flask_restful import Resource
from flask import request
from pydantic import ValidationError
from db import db
from models.role import RoleModel
from schemas.role import RoleCreate, RoleResponse


class RoleResource(Resource):
    def get(self):
        roles = RoleModel.query.all()
        return [RoleResponse.model_validate(r).model_dump(mode="json") for r in roles], 200

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

    def delete(self):
        data = request.get_json()
        role = db.session.get(RoleModel, data.get("id"))
        if not role:
            return {"msg": "Rol no encontrado"}, 404

        db.session.delete(role)
        db.session.commit()

        return {"msg": "Rol eliminado"}, 200
```

**¿Qué cambia respecto a Categorías?** Solo esto:
- `RoleModel` en vez de `CategoryModel`
- `RoleCreate` / `RoleResponse` en vez de `CategoryCreate` / `CategoryResponse`
- Mensajes de "Rol" en vez de "Categoría"

Ya estaba registrado en el `router/__init__.py`, así que solo probamos en Postman:

- **POST** `/api/roles` con `{"nombre": "admin", "descripcion": "Acceso total"}` → **201**
- **GET** `/api/roles` → lista con el rol creado
- **PUT** `/api/roles` con `{"id": 1, ...}` → actualizado
- **DELETE** `/api/roles` con `{"id": 1}` → eliminado

> **¿Cuál es el mensaje del día?** El CRUD es un PATRÓN. Si sabes hacer Categorías, sabes hacer Roles, Productos, Clientes y lo que sea. En el Día 2 le vamos a agregar seguridad a Roles con JWT.

---

## Resumen de conceptos

| Tema | Conceptos clave |
|------|-----------------|
| Setup | venv, `requirements.txt`, `.env`, `.env.copy`, BD en pgAdmin |
| Estructura | Flat, capas `models/`/`schemas/`/`resources/`, `router/` |
| app.py | `load_dotenv()`, `os.getenv()`, config sin secretos hardcodeados |
| Modelos | `Mapped[]`, `mapped_column`, `unique=True`, `__tablename__` |
| Schemas | `XxxCreate` (entrada) vs `XxxResponse` (salida), `from_attributes=True` |
| Migraciones | `flask db init` → `migrate` → `upgrade` |
| Resource | `get/post/put/delete`, validación Pydantic, 400/404/409 |
| Router | `register_routes(api)`, prefijo `/api/` |
| Postman | Probar cada endpoint apenas se crea, incluyendo los errores |
