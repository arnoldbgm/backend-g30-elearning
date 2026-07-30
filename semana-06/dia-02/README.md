# 🧠 Día 2 (Semana 6): Arquitectura boilerplate + Pydantic

<p align="center">
  <img src="https://flask.palletsprojects.com/en/stable/_static/flask-logo.png" alt="Logo de Flask" height="60">
  &nbsp;&nbsp;&nbsp;
  <img src="https://www.sqlalchemy.org/img/sqla_logo.png" alt="Logo de SQLAlchemy" height="60">
  &nbsp;&nbsp;&nbsp;
  <img alt="Pydantic" height="50" src="https://raw.githubusercontent.com/pydantic/pydantic/main/docs/images/pydantic-logo.svg">
</p>

El día de hoy no escribimos una API desde cero. Hoy **heredamos** un proyecto ya armado (el boilerplate) y aprendemos a trabajarlo como se hace en la industria: sobre una base que ya existe, la limpiamos, la entendemos, y la extendemos con nuestras propias entidades.

El boilerplate ya tiene todo lo que vimos ayer:
- `models/` → SQLAlchemy 2.0 con `Mapped[]`
- `schemas/` → Pydantic para validación
- `resources/` → Flask-RESTful con Resources
- `router/` → registro centralizado de rutas

Hoy no repetimos la teoría de cada pieza. Hoy **las usamos**. Y agregamos un ingrediente nuevo: **Pydantic** para validar datos en serio, sin escribir `if` a mano para cada campo.

---

## 0. Setup — clonar y limpiar el boilerplate (15 min)

### 0A — Demo: Copiar boilerplate y limpiar

Copien la carpeta `flask-boilerplate` a su espacio de trabajo:

```bash
cd restaurante_api
```

Activen el entorno virtual e instalen dependencias:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```


---

### 0B — Reto: Explicar la arquitectura

**Profe dice:** "Antes de seguir, asegurémonos de que todos entienden cómo está organizado el proyecto."

Respondan:
1. ¿Qué carpeta contiene los modelos de base de datos?
2. ¿Qué carpeta contiene los schemas de Pydantic?
3. ¿Dónde se registran las rutas (URL → Resource)?
4. ¿Por qué `db.py` está separado de `app.py`?

<details>
<summary><b>Solución (reto)</b></summary>

1. `models/` — ahí van las clases que heredan de `db.Model`
2. `schemas/` — ahí van las clases que heredan de `BaseModel` de Pydantic
3. En `router/__init__.py`, dentro de la función `register_routes()`
4. Para evitar **imports circulares**: tanto `models/` como `resources/` necesitan importar `db`. Si `db` estuviera en `app.py`, `app.py` tendría que importar `models/` y `models/` tendría que importar `app.py` — un círculo vicioso. Al tener `db.py` separado, rompemos ese ciclo.

</details>

---

## 1. Reto: Modelo Plato (15 min)

### Planteamiento

El restaurante necesita un catálogo de platos para su menú. Cada plato debe guardar:

- **Nombre** del plato (ej: "Lomo Saltado", "Ceviche")
- **Categoría** a la que pertenece (ej: "Entradas", "Platos Fuertes", "Bebidas", "Postres")
- **Precio** en soles (ej: 25.00, 30.50)

Preguntas para pensar ANTES de codear:
1. ¿La categoría es texto libre o debería ser una lista fija?
2. ¿El precio es entero o decimal? ¿Qué tipo de dato de SQLAlchemy usamos?
3. ¿Dónde se crea el archivo del modelo?
4. ¿Qué pasa si el nombre del plato tiene más de 100 caracteres?

Para darles contexto, estas son las **tres tablas** que vamos a construir a lo largo del día. Hoy empiezan con `platos`, pero el destino final es este:

<img width="787" height="297" alt="image" src="https://github.com/user-attachments/assets/82cb0d1e-f767-4af6-8539-ecdcc6129407" />


**Profe dice:** "Este diagrama es su hoja de ruta para todo el día. Hoy empiezan con `platos`, después agregan `clientes`, y al final conectan todo con `pedidos`. Tengan esto a mano — cada vez que se pregunten '¿qué sigue?' la respuesta está acá."

👉 Después de discutirlo, creen el archivo.

---

### 1A — Los alumnos crean el modelo

Crear `models/plato.py`:

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Integer
from db import db


class PlatoModel(db.Model):
    __tablename__ = "platos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
```

Ahora exportarlo en `models/__init__.py`:

```python
from .plato import PlatoModel
```

**Probar que funciona:**
```bash
flask db migrate -m "crear tabla platos"
flask db upgrade
```

**Verificar en pgAdmin:**
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

Ahora deberían ver: `alembic_version`, `platos`.

---

<details>
<summary><b>Solución completa (reto)</b></summary>

**models/plato.py:**
```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Integer
from db import db


class PlatoModel(db.Model):
    __tablename__ = "platos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
```

**models/__init__.py:**
```python
from .plato import PlatoModel
```

</details>

---

## 2. Demo + Reto: POST endpoint (Plato → Cliente) (50 min)

### 2A — Demo: Resource con POST para Plato (validación manual)

### Planteamiento

Ya tenemos la tabla `platos` en la base de datos. Ahora necesitamos una forma de agregar platos desde el frontend (o Postman). Para eso creamos un endpoint **POST**.

El endpoint necesita:
1. Recibir nombre, categoría y precio en formato JSON
2. Validar que los datos sean correctos ANTES de guardar:
   - ¿Los 3 campos llegaron?
   - ¿El nombre no está vacío?
   - ¿El precio es un número positivo?
3. Guardar el plato en la base de datos
4. Responder con el plato creado (incluyendo el `id` que generó la BD)
5. Si algo falla, responder con el error apropiado

Preguntas:
- ¿Qué código HTTP devolvemos cuando todo sale bien? ¿Y cuando falla?
- ¿Qué pasa si el cliente manda `precio: "veinte"` en vez de `precio: 20`?
- ¿Qué pasa si el cliente no manda `nombre`?

---

Crear `resources/platoResource.py`:

```python
from flask_restful import Resource
from flask import request
from db import db
from models.plato import PlatoModel


class PlatoResource(Resource):

    def post(self):
        try:
            data = request.get_json()

            if not data:
                return {"msg": "Debes enviar datos en formato JSON"}, 400

            if "nombre" not in data or not data["nombre"].strip():
                return {"msg": "El campo nombre es obligatorio"}, 400

            if "precio" not in data:
                return {"msg": "El campo precio es obligatorio"}, 400

            if not isinstance(data["precio"], (int, float)):
                return {"msg": "El precio debe ser un número"}, 400

            if data["precio"] <= 0:
                return {"msg": "El precio debe ser mayor a 0"}, 400

            nuevo = PlatoModel(
                nombre=data["nombre"],
                categoria=data.get("categoria", "General"),
                precio=data["precio"]
            )

            db.session.add(nuevo)
            db.session.commit()
            return {
                "id": nuevo.id,
                "nombre": nuevo.nombre,
                "categoria": nuevo.categoria,
                "precio": nuevo.precio
            }, 201
        except Exception:
            db.session.rollback()
            return {"msg": "Error del servidor al crear el plato"}, 500
```

**Desglose de las validaciones (una por una):**

| Validación | ¿Qué problema resuelve? |
|------------|------------------------|
| `if not data` | El cliente no mandó JSON, o mandó `{}` vacío |
| `"nombre" not in data or not data["nombre"].strip()` | Falta nombre, o está vacío, o son solo espacios |
| `"precio" not in data` | No mandó precio |
| `isinstance(data["precio"], (int, float))` | Mandó `"veinte"` en vez de `20` — texto en campo numérico |
| `data["precio"] <= 0` | Mandó `-5` o `0` — precio inválido |

**¿Por qué `data.get("categoria", "General")`?** Porque la categoría no debería ser obligatoria — si no mandan, asumimos "General".

Ahora exportarlo en `resources/__init__.py`:

```python
from .platoResource import PlatoResource
```

Registrar la ruta en `router/__init__.py`:

```python
from flask_restful import Api
from resources import PlatoResource


def register_routes(api: Api):
    api.add_resource(PlatoResource, "/api/platos")
```

---

### Probar en Postman

Ejecuten el servidor:
```bash
python app.py
```

**Crear un plato (POST exitoso):**
- Método: POST
- URL: `http://127.0.0.1:5000/api/platos`
- Body → raw → JSON:
```json
{
    "nombre": "Lomo Saltado",
    "categoria": "Platos Fuertes",
    "precio": 25.00
}
```
- Send → Deberían ver:
```json
{
    "id": 1,
    "nombre": "Lomo Saltado",
    "categoria": "Platos Fuertes",
    "precio": 25.0
}
```
- Código: **201 Created**

**Probar validaciones:**

POST sin nombre:
```json
{
    "precio": 25.00
}
```
→ `{"msg": "El campo nombre es obligatorio"}` — 400

POST con precio inválido:
```json
{
    "nombre": "Ceviche",
    "precio": "carisimo"
}
```
→ `{"msg": "El precio debe ser un número"}` — 400

POST sin datos (Body vacío):
→ `{"msg": "Debes enviar datos en formato JSON"}` — 400

---

### 2B — Reto: Modelo + POST Cliente

### Planteamiento

El restaurante necesita registrar a sus clientes. Cada cliente debe guardar:

- **Nombre** completo (obligatorio)
- **Teléfono** de contacto (opcional)
- **Dirección** de entrega (opcional)

El endpoint POST debe:
1. Recibir nombre, teléfono y dirección en JSON
2. Validar que el nombre sea obligatorio
3. Si no mandan teléfono o dirección, guardar string vacío
4. Responder con el cliente creado

Preguntas:
- ¿Ya vieron este patrón antes? ¿En qué se diferencia de Plato?
- ¿Qué campos son obligatorios y cuáles no?
- ¿Qué validaciones necesita el POST?

**Profe dice:** "Este es el mismo baile que acabamos de hacer con Plato. La diferencia es que esta vez lo hacen USTEDES. Si se trabancan, revisen el código de Plato. Si siguen trabados, pregunten."

<details>
<summary><b>Solución (reto)</b></summary>

**models/cliente.py:**
```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from db import db


class ClienteModel(db.Model):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    direccion: Mapped[str] = mapped_column(String(200), nullable=False)
```

**models/__init__.py:**
```python
from .plato import PlatoModel
from .cliente import ClienteModel
```

Migrar:
```bash
flask db migrate -m "crear tabla clientes"
flask db upgrade
```

**resources/clienteResource.py:**
```python
from flask_restful import Resource
from flask import request
from db import db
from models.cliente import ClienteModel


class ClienteResource(Resource):

    def post(self):
        try:
            data = request.get_json()

            if not data:
                return {"msg": "Debes enviar datos en formato JSON"}, 400

            if "nombre" not in data or not data["nombre"].strip():
                return {"msg": "El campo nombre es obligatorio"}, 400

            nuevo = ClienteModel(
                nombre=data["nombre"],
                telefono=data.get("telefono", ""),
                direccion=data.get("direccion", "")
            )

            db.session.add(nuevo)
            db.session.commit()
            return {
                "id": nuevo.id,
                "nombre": nuevo.nombre,
                "telefono": nuevo.telefono,
                "direccion": nuevo.direccion
            }, 201
        except Exception:
            db.session.rollback()
            return {"msg": "Error del servidor al crear el cliente"}, 500
```

**resources/__init__.py:**
```python
from .platoResource import PlatoResource
from .clienteResource import ClienteResource
```

**router/__init__.py:**
```python
from flask_restful import Api
from resources import PlatoResource, ClienteResource


def register_routes(api: Api):
    api.add_resource(PlatoResource, "/api/platos")
    api.add_resource(ClienteResource, "/api/clientes")
```

**Prueba en Postman:**
- POST `http://127.0.0.1:5000/api/clientes`
```json
{
    "nombre": "Juan Perez",
    "telefono": "999888777",
    "direccion": "Av. Lima 123"
}
```
→ Debería responder con el cliente creado y código 201

- POST sin nombre:
```json
{
    "telefono": "999888777"
}
```
→ `{"msg": "El campo nombre es obligatorio"}` — 400

</details>

---

## 3. ⚡ Pydantic de referencia + Demo + Reto (Plato → Cliente) (55 min)

### Planteamiento

Miren el código que escribieron para validar los datos de POST. ¿Cuántas líneas de `if` tienen?

Cuenten: en el POST de Plato hay **5 validaciones manuales**. Y solo son 3 campos. ¿Qué pasa cuando tienen 10 campos? ¿20 campos? ¿30?

```python
if not data:
    return {"msg": "Debes enviar datos"}, 400
if "nombre" not in data or not data["nombre"].strip():
    return {"msg": "Falta nombre"}, 400
if "precio" not in data:
    return {"msg": "Falta precio"}, 400
if not isinstance(data["precio"], (int, float)):
    return {"msg": "Precio debe ser número"}, 400
if data["precio"] <= 0:
    return {"msg": "Precio debe ser positivo"}, 400
```

Esto es:
- **Repetitivo** — cada campo nuevo = otro `if`
- **Propenso a errores** — si te olvidás de una validación, datos inválidos entran a la BD
- **Difícil de leer** — 30 líneas de `if` al inicio de cada POST

**Analogía:** las validaciones manuales son como revisar cada documento de un cliente UNO POR UNO, a mano, con una lista de chequeo en papel. Pydantic es como tener un escáner automático que lee el documento y te dice al instante si falta algo.

---

### ¿Qué es Pydantic?

Pydantic es una librería que **valida datos automáticamente** usando type hints de Python. Definís un schema (un "molde") con los campos y tipos esperados, y Pydantic se encarga del resto.

```python
from pydantic import BaseModel


class PlatoCreate(BaseModel):
    nombre: str
    precio: float
```

Con esas 4 líneas, Pydantic ya sabe que:
- `nombre` debe ser texto y no vacío
- `precio` debe ser un número (int o float) y no puede faltar

No necesitás escribir un solo `if`.

---

### Ejemplos básicos

**Caso 1: Datos correctos**
```python
data = PlatoCreate(nombre="Lomo Saltado", precio=25.00)
print(data.nombre)   # "Lomo Saltado"
print(data.precio)   # 25.0
```

**Caso 2: Falta un campo obligatorio**
```python
from pydantic import ValidationError

try:
    data = PlatoCreate(precio=25.00)
except ValidationError as e:
    print(e.errors())
    # → [{"type": "missing", "loc": ["nombre"], "msg": "Field required"}]
```

**Caso 3: Tipo de dato incorrecto**
```python
try:
    data = PlatoCreate(nombre="Ceviche", precio="carisimo")
except ValidationError as e:
    print(e.errors())
    # → [{"type": "float_parsing", "loc": ["precio"], "msg": "Input should be a valid number"}]
```

**Caso 4: Campos opcionales**
```python
from pydantic import BaseModel


class ClienteCreate(BaseModel):
    nombre: str
    telefono: str | None = None
    direccion: str | None = None
```

**Caso 5: Convertir schema a diccionario (para guardar en el modelo)**
```python
data = PlatoCreate(nombre="Arroz con Leche", precio=12.00)
diccionario = data.model_dump()
print(diccionario)
# → {"nombre": "Arroz con Leche", "precio": 12.0}
```

---

### Solo schema de entrada, nada más

Pydantic lo usamos **solo para validar lo que llega del cliente**. La respuesta la armamos como un diccionario de Python directamente — no necesitamos un schema para eso.

```python
class PlatoCreate(BaseModel):
    nombre: str
    precio: float
```

Al recibir: `PlatoCreate(**request.get_json())` valida automáticamente.
Al responder: `return {"id": nuevo.id, "nombre": nuevo.nombre, ...}` — un dict simple.

---

### Comparación final

**Sin Pydantic (15 líneas para 3 campos):** 5 `if` con lógica repetitiva.
**Con Pydantic (6 líneas para los mismos 3 campos):**
```python
try:
    data = PlatoCreate(**request.get_json())
except ValidationError as e:
    return {"msg": "Datos inválidos", "errores": e.errors()}, 400
```

Y Pydantic nos da **más** validaciones: tipo de dato, campos faltantes, strings vacíos, valores negativos.

---

### 3A — Demo: Refactorizar POST Plato con Pydantic

Sabemos qué es Pydantic. Ahora lo aplicamos. Refactorizamos el POST de Plato para usar schemas.

Preguntas antes de codear:
1. ¿Dónde se crean los archivos de schemas?
2. ¿Cómo capturamos el error de validación de Pydantic?
3. ¿La respuesta la armamos con schema o con dict?

Crear `schemas/plato.py`:

```python
from pydantic import BaseModel


class PlatoCreate(BaseModel):
    nombre: str
    precio: float
    categoria: str = "General"
```

**Desglose:**

| Campo | Significado |
|-------|-------------|
| `nombre: str` | Texto obligatorio. Pydantic rechaza si no viene o si viene vacío |
| `precio: float` | Número obligatorio. Rechaza si viene texto o si falta |
| `categoria: str = "General"` | Opcional. Si no mandan, usa "General" |

**¿Notan algo?** Ya no necesitamos `data.get("categoria", "General")` en el resource. El schema se encarga de eso.

Exportar en `schemas/__init__.py`:

```python
from .plato import PlatoCreate
```

Ahora modificamos `resources/platoResource.py` para usar Pydantic:

```python
from flask_restful import Resource
from flask import request
from db import db
from models.plato import PlatoModel
from schemas.plato import PlatoCreate


class PlatoResource(Resource):

    def post(self):
        try:
            data = PlatoCreate(**request.get_json())
            nuevo = PlatoModel(
                nombre=data.nombre,
                categoria=data.categoria,
                precio=data.precio
            )
            db.session.add(nuevo)
            db.session.commit()
            return {
                "id": nuevo.id,
                "nombre": nuevo.nombre,
                "categoria": nuevo.categoria,
                "precio": nuevo.precio
            }, 201
        except Exception:
            db.session.rollback()
            return {"msg": "Error del servidor al crear el plato"}, 500
```

**Comparación: cómo cambió el código**

| Aspecto | Antes (manual) | Después (Pydantic) |
|---------|---------------|-------------------|
| Validaciones | 5 `if` | Pydantic + 1 `except Exception` |
| Valor por defecto de categoría | `data.get("categoria", "General")` | `categoria: str = "General"` |
| Construcción de respuesta | Dict escrito a mano | Dict escrito a mano (igual) |

La respuesta SIEMPRE es un dict. Pydantic solo valida entrada.

**Probar en Postman:**

**POST exitoso:**
```json
{"nombre": "Ají de Gallina", "precio": 20.00, "categoria": "Platos Fuertes"}
```
→ 201 Created

**POST sin precio (Pydantic lo rechaza):**
```json
{"nombre": "Ají de Gallina"}
```
→ 400 con errores de Pydantic:
```json
{"msg": "Datos inválidos", "errores": [{"type": "missing", "loc": ["precio"], "msg": "Field required"}]}
```

---

### 3B — Reto: Pydantic en POST Cliente

**Profe dice:** "Agarren el `ClienteResource` que crearon hace rato (con validaciones manuales) y refactorícenlo para usar Pydantic. Solos."

**Recuerden:**
- `nombre` es obligatorio
- `telefono` y `direccion` son opcionales (`str | None = None`)
- Solo necesitan un schema: `ClienteCreate`
- La respuesta va con dict directo

<details>
<summary><b>Solución (reto)</b></summary>

**schemas/cliente.py:**
```python
from pydantic import BaseModel


class ClienteCreate(BaseModel):
    nombre: str
    telefono: str | None = None
    direccion: str | None = None
```

**schemas/__init__.py:**
```python
from .plato import PlatoCreate
from .cliente import ClienteCreate
```

**resources/clienteResource.py:**
```python
from flask_restful import Resource
from flask import request
from db import db
from models.cliente import ClienteModel
from schemas.cliente import ClienteCreate


class ClienteResource(Resource):

    def post(self):
        try:
            data = ClienteCreate(**request.get_json())
            telefono = data.telefono if data.telefono else ""
            direccion = data.direccion if data.direccion else ""
            nuevo = ClienteModel(
                nombre=data.nombre,
                telefono=telefono,
                direccion=direccion
            )
            db.session.add(nuevo)
            db.session.commit()
            return {
                "id": nuevo.id,
                "nombre": nuevo.nombre,
                "telefono": nuevo.telefono,
                "direccion": nuevo.direccion
            }, 201
        except Exception:
            db.session.rollback()
            return {"msg": "Error del servidor al crear el cliente"}, 500
```

**Prueba en Postman:
- POST `http://127.0.0.1:5000/api/clientes`
```json
{"nombre": "Maria Garcia"}
```
→ 201 Created con telefono="" y direccion=""

```json
{}
```
→ 400 con error: "nombre" field required

</details>

---

## 4. Demo + Reto: GET all y GET one (Plato → Cliente) (20 min)

### Planteamiento

Ya sabemos crear datos con POST. Ahora necesitamos poder **listar** los platos y **buscar** uno por su ID.

**GET /api/platos** → devuelve todos los platos
**GET /api/platos/1** → devuelve el plato con id=1

Preguntas:
- ¿Qué pasa si el plato con ese ID no existe?
- ¿Qué código HTTP devolvemos en cada caso?
- ¿Cómo recibimos el ID en el Resource?

---

### 4A — Demo: GET all y GET one en Plato

Agregamos los métodos `get()` a `PlatoResource`:

```python
class PlatoResource(Resource):

    def get(self, id=None):
        if id is None:
            platos = PlatoModel.query.all()

            resultado = []
            for p in platos:
                resultado.append({
                    "id": p.id,
                    "nombre": p.nombre,
                    "categoria": p.categoria,
                    "precio": p.precio
                })

            return resultado

        plato = PlatoModel.query.get(id)

        if not plato:
            return {"msg": "Plato no encontrado"}, 404

        return {
            "id": plato.id,
            "nombre": plato.nombre,
            "categoria": plato.categoria,
            "precio": plato.precio
        }

    def post(self):
        # ... el mismo de antes ...
```

**¿Por qué `id=None` como parámetro?** Porque vamos a usar la misma clase para dos rutas:
- `GET /api/platos` → sin `id`, lista todos
- `GET /api/platos/<int:id>` → con `id`, busca uno

**¿Cómo hacemos que funcione con dos rutas?** Necesitamos dos registros en `router/__init__.py`:

```python
api.add_resource(PlatoResource, "/api/platos", "/api/platos/<int:id>")
```

**Desglose de `get(self, id=None)`:**

| Situación | ¿Qué pasa? |
|-----------|-----------|
| GET /api/platos | Flask-RESTful llama a `get(id=None)` → entra al `if id is None` → lista todos |
| GET /api/platos/1 | Flask-RESTful llama a `get(id=1)` → pasa directo a `PlatoModel.query.get(1)` |
| GET /api/platos/999 | Busca id=999, no existe → devuelve 404 |

**¿Por qué usamos `for` tradicional en vez de list comprehension?**

Porque en este curso queremos que se vea cada paso. Esto es más fácil de leer y depurar:
```python
resultado = []
for p in platos:
    resultado.append({
        "id": p.id,
        "nombre": p.nombre,
        "categoria": p.categoria,
        "precio": p.precio
    })
return resultado
```

---

### Probar en Postman

Asegurarse de tener `router/__init__.py` con las dos rutas:

```python
from flask_restful import Api
from resources import PlatoResource, ClienteResource


def register_routes(api: Api):
    api.add_resource(PlatoResource, "/api/platos", "/api/platos/<int:id>")
    api.add_resource(ClienteResource, "/api/clientes")
```

Reinicien el servidor y prueben:

- GET `http://127.0.0.1:5000/api/platos` → lista de platos (vacía o con los que crearon)
- GET `http://127.0.0.1:5000/api/platos/1` → el plato con id=1
- GET `http://127.0.0.1:5000/api/platos/999` → `{"msg": "Plato no encontrado"}` — 404

---

### 4B — Reto: GET all y GET one en Cliente

**Profe dice:** "Agreguen GET all y GET one al `ClienteResource`. Mismo patrón que Plato."

<details>
<summary><b>Solución (reto)</b></summary>

**resources/clienteResource.py:**
```python
from flask_restful import Resource
from flask import request
from db import db
from models.cliente import ClienteModel
from schemas.cliente import ClienteCreate


class ClienteResource(Resource):

    def get(self, id=None):
        if id is None:
            clientes = ClienteModel.query.all()

            resultado = []
            for c in clientes:
                resultado.append({
                    "id": c.id,
                    "nombre": c.nombre,
                    "telefono": c.telefono,
                    "direccion": c.direccion
                })

            return resultado

        cliente = ClienteModel.query.get(id)

        if not cliente:
            return {"msg": "Cliente no encontrado"}, 404

        return {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "telefono": cliente.telefono,
            "direccion": cliente.direccion
        }

    def post(self):
        try:
            data = ClienteCreate(**request.get_json())
            telefono = data.telefono if data.telefono else ""
            direccion = data.direccion if data.direccion else ""
            nuevo = ClienteModel(
                nombre=data.nombre,
                telefono=telefono,
                direccion=direccion
            )
            db.session.add(nuevo)
            db.session.commit()
            return {
                "id": nuevo.id,
                "nombre": nuevo.nombre,
                "telefono": nuevo.telefono,
                "direccion": nuevo.direccion
            }, 201
        except Exception:
            db.session.rollback()
            return {"msg": "Error del servidor al crear el cliente"}, 500
```

**router/__init__.py:**
```python
from flask_restful import Api
from resources import PlatoResource, ClienteResource


def register_routes(api: Api):
    api.add_resource(PlatoResource, "/api/platos", "/api/platos/<int:id>")
    api.add_resource(ClienteResource, "/api/clientes", "/api/clientes/<int:id>")
```

</details>

---

## 5. Demo + Reto: PUT y DELETE (Plato → Cliente) (20 min)

### Planteamiento

Ya podemos crear, listar y buscar. Ahora necesitamos **actualizar** y **eliminar** platos.

**PUT /api/platos/1** → actualiza el plato con id=1
- Recibe los campos a actualizar en JSON
- Actualiza solo los campos que vienen (no reemplaza todo)
- Si el plato no existe, devuelve 404
- Devuelve el plato actualizado

**DELETE /api/platos/1** → elimina el plato con id=1
- Si el plato no existe, devuelve 404
- Devuelve un mensaje de confirmación

Preguntas:
- En PUT, ¿qué pasa si el cliente manda solo `nombre`? ¿Se borran `precio` y `categoria`?
- En DELETE, ¿qué información debería incluir el mensaje de respuesta?
- ¿Qué código HTTP devolvemos cuando la operación es exitosa?

---

### 5A — Demo: PUT y DELETE en Plato

Agregamos los métodos a `PlatoResource`:

```python
class PlatoResource(Resource):

    # ... get e post ...

    def put(self, id):
        plato = PlatoModel.query.get(id)

        if not plato:
            return {"msg": "Plato no encontrado"}, 404

        try:
            data = PlatoCreate(**request.get_json())
            plato.nombre = data.nombre
            plato.categoria = data.categoria
            plato.precio = data.precio
            db.session.commit()
            return {
                "id": plato.id,
                "nombre": plato.nombre,
                "categoria": plato.categoria,
                "precio": plato.precio
            }
        except Exception:
            db.session.rollback()
            return {"msg": "Error del servidor al actualizar el plato"}, 500

    def delete(self, id):
        plato = PlatoModel.query.get(id)

        if not plato:
            return {"msg": "Plato no encontrado"}, 404

        nombre = plato.nombre
        try:
            db.session.delete(plato)
            db.session.commit()
            return {"msg": f"Plato '{nombre}' eliminado"}
        except Exception:
            db.session.rollback()
            return {"msg": "Error del servidor al eliminar el plato"}, 500
```

**Desglose de PUT:**

| Paso | Código | ¿Qué hace? |
|------|--------|-----------|
| 1 | `PlatoModel.query.get(id)` | Busca el plato en la BD |
| 2 | `if not plato: return 404` | Si no existe, error |
| 3 | `PlatoCreate(**request.get_json())` | Valida los datos nuevos con Pydantic |
| 4 | `plato.nombre = data.nombre` | Actualiza campo por campo |
| 5 | `db.session.commit()` | Guarda los cambios |
| 6 | `return {"id": ..., ...}` | Devuelve el plato actualizado en dict |

**Desglose de DELETE:**

| Paso | Código | ¿Qué hace? |
|------|--------|-----------|
| 1 | `PlatoModel.query.get(id)` | Busca el plato |
| 2 | `if not plato: return 404` | Si no existe, error |
| 3 | `nombre = plato.nombre` | Guarda el nombre ANTES de borrar (para el mensaje) |
| 4 | `db.session.delete(plato)` | Marca el plato para eliminar |
| 5 | `db.session.commit()` | Ejecuta el DELETE en la BD |
| 6 | `return {"msg": f"'{nombre}' eliminado"}` | Confirma la eliminación |

**¿Por qué guardamos `nombre` antes de borrar?** Porque después de `db.session.delete(plato)`, el objeto `plato` sigue existiendo en memoria, pero está "detached". Es buena práctica guardar lo que necesitemos del mensaje antes del delete.

---

### 5B — Probar en Postman

**PUT exitoso:**
- Método: PUT
- URL: `http://127.0.0.1:5000/api/platos/1`
- Body → raw → JSON:
```json
{
    "nombre": "Lomo Saltado Clásico",
    "categoria": "Platos Fuertes",
    "precio": 28.00
}
```
- Send → plato actualizado con código 200

**PUT con datos inválidos:**
```json
{
    "nombre": "",
    "precio": -5
}
```
→ 400 con errores de Pydantic (string vacío, precio negativo)

**DELETE exitoso:**
- Método: DELETE
- URL: `http://127.0.0.1:5000/api/platos/1`
- Send → `{"msg": "Plato 'Lomo Saltado Clásico' eliminado"}` — 200

**DELETE de plato inexistente:**
- URL: `http://127.0.0.1:5000/api/platos/999`
- Send → `{"msg": "Plato no encontrado"}` — 404

---

### 5C — Reto: PUT y DELETE en Cliente

**Profe dice:** "Agreguen PUT y DELETE a Cliente. Mismo patrón. Si se traban, miren el código de Plato."

<details>
<summary><b>Solución (reto)</b></summary>

```python
class ClienteResource(Resource):

    # ... get y post ...

    def put(self, id):
        cliente = ClienteModel.query.get(id)

        if not cliente:
            return {"msg": "Cliente no encontrado"}, 404

        try:
            data = ClienteCreate(**request.get_json())
            cliente.nombre = data.nombre
            cliente.telefono = data.telefono if data.telefono else ""
            cliente.direccion = data.direccion if data.direccion else ""
            db.session.commit()
            return {
                "id": cliente.id,
                "nombre": cliente.nombre,
                "telefono": cliente.telefono,
                "direccion": cliente.direccion
            }
        except Exception:
            db.session.rollback()
            return {"msg": "Error del servidor al actualizar el cliente"}, 500

    def delete(self, id):
        cliente = ClienteModel.query.get(id)

        if not cliente:
            return {"msg": "Cliente no encontrado"}, 404

        nombre = cliente.nombre
        try:
            db.session.delete(cliente)
            db.session.commit()
            return {"msg": f"Cliente '{nombre}' eliminado"}
        except Exception:
            db.session.rollback()
            return {"msg": "Error del servidor al eliminar el cliente"}, 500
```

</details>

---

## 6. Reto final: Pedido (30 min)

### Planteamiento

Llegó el plato fuerte del día. El restaurante necesita registrar **pedidos**. Un pedido conecta a un cliente con un plato, y calcula automáticamente el total.

Un pedido necesita:
- **Cliente** que hizo el pedido (referencia a `clientes`)
- **Plato** que se pidió (referencia a `platos`)
- **Cantidad** de platos (ej: 2 Lomo Saltados)
- **Fecha** del pedido (se asigna automáticamente al crearlo)
- **Total** (se calcula: `plato.precio * cantidad`)

Diagrama de relaciones (el mismo de la sección 1, con tipos y nullabilidad):

<img width="787" height="297" alt="image" src="https://github.com/user-attachments/assets/ca8c7fb1-e3bc-469c-8524-76c45e8f5e09" />


Preguntas para pensar ANTES de codear:
1. **Foreign Keys**: ¿cómo se escribe una FK en SQLAlchemy 2.0?
2. **Validación de existencia**: antes de crear un pedido, ¿qué debemos verificar?
3. **Cálculo automático**: el total lo calcula el servidor, no el cliente. ¿Dónde ponemos esa lógica?
4. **Fecha automática**: ¿cómo hacemos que la fecha se asigne sola al crear el pedido?

**Profe dice:** "Este es el reto más complejo del día porque combina TODO lo que vimos: modelo con FK, schema de Pydantic, resource con validaciones Y lógica de negocio (calcular total, asignar fecha). Tienen 20 minutos. Si no terminan, no pasa nada — la solución completa está abajo. Pero INTÉNTENLO primero."

---

### Lo que deben crear

**1. Modelo** `models/pedido.py`:
- `id`: entero, PK
- `id_cliente`: entero, FK a `clientes.id`
- `id_plato`: entero, FK a `platos.id`
- `cantidad`: entero
- `fecha`: datetime, default `datetime.now`
- `total`: float
- Relaciones: `cliente` (N:1 a ClienteModel), `plato` (N:1 a PlatoModel)

**2. Schema** `schemas/pedido.py`:
- `PedidoCreate`: `id_cliente`, `id_plato`, `cantidad`

**3. Resource** `resources/pedidoResource.py`:
- `post`: validar existencia de cliente y plato, calcular total, asignar fecha
- `get` (all y one): listar pedidos con nombre de cliente y plato
- `delete`: eliminar pedido

**4. Router**: registrar las rutas

---

<details>
<summary><b>Solución completa (reto final)</b></summary>

### 1. Modelo — models/pedido.py

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, DateTime, ForeignKey
from datetime import datetime
from db import db
from models.plato import PlatoModel
from models.cliente import ClienteModel


class PedidoModel(db.Model):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_cliente: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    id_plato: Mapped[int] = mapped_column(ForeignKey("platos.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    total: Mapped[float] = mapped_column(Float, nullable=False)

    cliente = relationship("ClienteModel")
    plato = relationship("PlatoModel")
```

Exportar en `models/__init__.py`:

```python
from .plato import PlatoModel
from .cliente import ClienteModel
from .pedido import PedidoModel
```

Migrar:
```bash
flask db migrate -m "crear tabla pedidos"
flask db upgrade
```

### 2. Schema — schemas/pedido.py

```python
from pydantic import BaseModel


class PedidoCreate(BaseModel):
    id_cliente: int
    id_plato: int
    cantidad: int = 1
```

**¿Solo un schema?** Sí. Pydantic solo valida entrada. La respuesta va como dict directo.

Exportar en `schemas/__init__.py`:

```python
from .plato import PlatoCreate
from .cliente import ClienteCreate
from .pedido import PedidoCreate
```

### 3. Resource — resources/pedidoResource.py

```python
from flask_restful import Resource
from flask import request
from datetime import datetime
from db import db
from models.pedido import PedidoModel
from models.cliente import ClienteModel
from models.plato import PlatoModel
from schemas.pedido import PedidoCreate


class PedidoResource(Resource):

    def get(self, id=None):
        if id is None:
            pedidos = PedidoModel.query.all()

            resultado = []
            for p in pedidos:
                resultado.append({
                    "id": p.id,
                    "id_cliente": p.id_cliente,
                    "id_plato": p.id_plato,
                    "cantidad": p.cantidad,
                    "fecha": str(p.fecha),
                    "total": p.total,
                    "cliente_nombre": p.cliente.nombre if p.cliente else "Desconocido",
                    "plato_nombre": p.plato.nombre if p.plato else "Desconocido"
                })

            return resultado

        pedido = PedidoModel.query.get(id)

        if not pedido:
            return {"msg": "Pedido no encontrado"}, 404

        return {
            "id": pedido.id,
            "id_cliente": pedido.id_cliente,
            "id_plato": pedido.id_plato,
            "cantidad": pedido.cantidad,
            "fecha": str(pedido.fecha),
            "total": pedido.total,
            "cliente_nombre": pedido.cliente.nombre if pedido.cliente else "Desconocido",
            "plato_nombre": pedido.plato.nombre if pedido.plato else "Desconocido"
        }

    def post(self):
        try:
            data = PedidoCreate(**request.get_json())

            cliente = ClienteModel.query.get(data.id_cliente)
            if not cliente:
                return {"msg": "Cliente no encontrado"}, 404

            plato = PlatoModel.query.get(data.id_plato)
            if not plato:
                return {"msg": "Plato no encontrado"}, 404

            total = plato.precio * data.cantidad

            nuevo = PedidoModel(
                id_cliente=data.id_cliente,
                id_plato=data.id_plato,
                cantidad=data.cantidad,
                fecha=datetime.now(),
                total=total
            )

            db.session.add(nuevo)
            db.session.commit()
            return {
                "id": nuevo.id,
                "id_cliente": nuevo.id_cliente,
                "id_plato": nuevo.id_plato,
                "cantidad": nuevo.cantidad,
                "fecha": str(nuevo.fecha),
                "total": nuevo.total,
                "cliente_nombre": cliente.nombre,
                "plato_nombre": plato.nombre
            }, 201
        except Exception:
            db.session.rollback()
            return {"msg": "Error del servidor al crear el pedido"}, 500

    def delete(self, id):
        pedido = PedidoModel.query.get(id)

        if not pedido:
            return {"msg": "Pedido no encontrado"}, 404

        try:
            db.session.delete(pedido)
            db.session.commit()
            return {"msg": "Pedido eliminado"}
        except Exception:
            db.session.rollback()
            return {"msg": "Error del servidor al eliminar el pedido"}, 500
```

**¿Qué tiene de especial el POST de Pedido?**

| Diferencia | ¿Por qué? |
|-----------|-----------|
| Valida que el cliente exista | No se puede crear un pedido para un cliente que no existe en la BD |
| Valida que el plato exista | No se puede pedir un plato que no está en el menú |
| Calcula el total automáticamente | `total = plato.precio * cantidad` — el cliente NO manda el total |
| Asigna fecha automáticamente | `fecha=datetime.now()` — el cliente NO manda la fecha |

**¿Por qué en el GET devolvemos el nombre del cliente y del plato (y no solo los IDs)?** Porque el frontend necesita mostrar "Juan Perez pidió Lomo Saltado", no "El cliente 1 pidió el plato 2". La relación de SQLAlchemy (`p.cliente.nombre`) nos permite acceder a esos datos sin hacer consultas adicionales.

### 4. Router

```python
from flask_restful import Api
from resources import PlatoResource, ClienteResource, PedidoResource


def register_routes(api: Api):
    api.add_resource(PlatoResource, "/api/platos", "/api/platos/<int:id>")
    api.add_resource(ClienteResource, "/api/clientes", "/api/clientes/<int:id>")
    api.add_resource(PedidoResource, "/api/pedidos", "/api/pedidos/<int:id>")
```

### Probar en Postman

Primero asegurarse de tener datos en las tablas `clientes` y `platos`:

**Crear un cliente:**
```
POST http://127.0.0.1:5000/api/clientes
{"nombre": "Juan Perez", "telefono": "999111222"}
```

**Crear un plato:**
```
POST http://127.0.0.1:5000/api/platos
{"nombre": "Lomo Saltado", "categoria": "Platos Fuertes", "precio": 25.00}
```

**Crear un pedido:**
```
POST http://127.0.0.1:5000/api/pedidos
{"id_cliente": 1, "id_plato": 1, "cantidad": 2}
```
→ Deberían ver:
```json
{
    "id": 1,
    "id_cliente": 1,
    "id_plato": 1,
    "cantidad": 2,
    "fecha": "2026-07-30 18:30:00",
    "total": 50.0,
    "cliente_nombre": "Juan Perez",
    "plato_nombre": "Lomo Saltado"
}
```

**Listar pedidos:**
```
GET http://127.0.0.1:5000/api/pedidos
```
→ Lista con nombre del cliente y del plato, no solo IDs.

**Pedido inválido (cliente inexistente):**
```
POST http://127.0.0.1:5000/api/pedidos
{"id_cliente": 999, "id_plato": 1, "cantidad": 1}
```
→ `{"msg": "Cliente no encontrado"}` — 404

**Pedido inválido (plato inexistente):**
```
POST http://127.0.0.1:5000/api/pedidos
{"id_cliente": 1, "id_plato": 999, "cantidad": 1}
```
→ `{"msg": "Plato no encontrado"}` — 404

</details>

---

## 7. Resumen de conceptos

| Tema | Demo | Reto | Conceptos clave |
|------|:----:|:----:|-----------------|
| 0. Setup boilerplate | ✅ | ✅ | Clonar, limpiar User, `flask db init`, migración vacía |
| 1. Modelo Plato | — | ✅ | `Mapped[]`, `mapped_column`, migración |
| 2. POST con validación manual | ✅ | ✅ | `request.get_json()`, `if` de validación, códigos HTTP |
| 3. Pydantic de referencia | ✅ | — | `BaseModel`, type hints, `ValidationError`, `model_dump()` |
| 4. Refactorizar Plato con Pydantic | ✅ | — | Pydantic + `except Exception`, schema de entrada |
| 5. Pydantic en Cliente | — | ✅ | Refactorizar solos |
| 6. GET all + GET one | ✅ | ✅ | `id=None`, `query.get()`, 404 |
| 7. PUT + DELETE | ✅ | ✅ | Actualizar campo por campo, `db.session.delete()` |
| 8. Reto final: Pedido | — | ✅ | FKs, relaciones, validación de existencia, cálculo automático |

---

## Estructura final del proyecto

```
restaurante_api/
├── app.py
├── db.py
├── .env
├── requirements.txt
├── migrations/
├── models/
│   ├── __init__.py
│   ├── plato.py
│   ├── cliente.py
│   └── pedido.py
├── schemas/
│   ├── __init__.py
│   ├── plato.py
│   ├── cliente.py
│   └── pedido.py
├── resources/
│   ├── __init__.py
│   ├── platoResource.py
│   ├── clienteResource.py
│   └── pedidoResource.py
├── router/
│   └── __init__.py
└── utils/
    ├── __init__.py
    └── helpers.py
```
