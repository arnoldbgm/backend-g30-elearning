# Guía — Día 1 (Semana 8): Productos con Cloudinary 📦☁️

Hoy le damos vida al catálogo de la tienda. Ya tenemos roles, categorías, usuarios y seguridad. ¿Qué falta para que sea una tienda de verdad? **PRODUCTOS.** Y los productos, en el mundo real, tienen fotos.

**Lo que vas a lograr hoy:**
- Tabla `productos` con código autogenerado (P-00001, P-00002...)
- Subir fotos a Cloudinary (la nube) y guardar solo la URL en la BD
- CRUD completo probado en Postman con **form-data**
- Borrado que no rompe el historial (borrado lógico)

**Analogía:** tu base de datos es como el fichero de una farmacia. Ahí guardas FICHAS con datos (nombre, precio, stock). ¿Y las cajas de medicina? No caben en un fichero. Las guardas en el depósito (Cloudinary) y en la ficha anotas en qué estante está (la URL). Nadie llena un fichero con cajas de medicina... ni con fotos de productos.

---

## 1. Cloudinary: qué es y cómo se configura (15 min)

### 1A — ¿Qué es Cloudinary?

**Cloudinary** es un servicio en la nube que guarda imágenes, las optimiza y te devuelve una URL pública.

¿Por qué NO guardamos la imagen dentro de PostgreSQL?

| Forma | Problema |
|-------|----------|
| Guardar el archivo en la BD | Las BD se vuelven lentas y gigantes con imágenes. Recuperar un producto implica mover megabytes |
| Guardar la imagen en una carpeta del proyecto | Se pierde si reinstalás, no escala y complica el deploy |
| **Guardar la URL en la BD** | La imagen vive en Cloudinary, la BD solo guarda un texto corto. Rápido, escalable, profesional |

### 1B — Dependencia

A `requirements.txt`:

```
cloudinary==1.45.0
```

```bash
pip install -r requirements.txt
```

### 1C — Credenciales en `.env`

Creá tu cuenta gratis en **cloudinary.com**. El dashboard te muestra 3 datos.

`.env`:

```
DATABASE_URL=postgresql://postgres:root@localhost:5432/flask-ecommerce
DEBUG=True
JWT_SECRET_KEY=982fbdeb44fdb8170d7d1de931ec72b7164d48cf2788d69724c758a471483194
CLOUDINARY_CLOUD_NAME=du0sspuql
CLOUDINARY_API_KEY=726516987941426
CLOUDINARY_API_SECRET=VCZzgEtDhOuuAFxv30lZATBBYZs
```

`.env.copy`:

```
CLOUDINARY_CLOUD_NAME=TU_CLOUD_NAME
CLOUDINARY_API_KEY=TU_API_KEY
CLOUDINARY_API_SECRET=TU_API_SECRET
```

Mismo patrón de siempre: tus secretos en `.env`, la plantilla en `.env.copy`.

---

## 2. CloudinaryHelper en utils/helpers.py (15 min)

Agregamos los imports de cloudinary y la clase al final del archivo:

```python
import os
from bcrypt import hashpw, gensalt, checkpw
import cloudinary
import cloudinary.uploader


def hash_password(password):
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


def verify_password(password, hashed):
    return checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


class CloudinaryHelper:
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    @staticmethod
    def validate_image(filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in CloudinaryHelper.ALLOWED_EXTENSIONS

    @staticmethod
    def upload(file_storage):
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        )
        result = cloudinary.uploader.upload(file_storage)
        return result["secure_url"]
```

### Desglose pieza por pieza

| Pieza | ¿Qué hace? |
|-------|-----------|
| `ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}` | Un **set** con las extensiones aceptadas. Validar antes de subir |
| `validate_image(filename)` | Separa el nombre de la extensión con `rsplit(".", 1)` y verifica que esté en el set. Devuelve `True`/`False` |
| `upload(file_storage)` | `cloudinary.config(...)` carga las credenciales desde `.env`, `uploader.upload(file)` sube el archivo y `result["secure_url"]` es la URL pública final |

**¿Por qué `@staticmethod`?** Porque la función no usa `self` — no necesita recordar nada entre llamadas. La llamas directo: `CloudinaryHelper.upload(archivo)`.

**Aclaración honesta sobre seguridad:** validar solo la extensión (`file.jpg`) es la versión didáctica. En producción también se valida el CONTENIDO del archivo (los "magic bytes"), porque cualquiera puede renombrar un `.exe` a `.jpg`. Acá vamos paso a paso.

---

## 3. Modelo productos (20 min)

### models/product.py

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Boolean, ForeignKey
from db import db


class ProductModel(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    imagen_url: Mapped[str] = mapped_column(String(500), nullable=True)
    categoria_id: Mapped[int] = mapped_column(Integer, ForeignKey("categorias.id"), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    categoria = db.relationship("CategoryModel", backref="productos")

    __tablename__ = "productos"
```

**Desglose:**

| Columna | ¿Qué es? |
|---------|----------|
| `codigo` | Único, autogenerado: `P-00001` |
| `precio` | `Float` — número decimal, ej: 3499.99 |
| `stock` | `Integer` — cuántas unidades hay |
| `imagen_url` | `nullable=True` porque en el modelo el producto puede existir sin URL todavía (aunque el POST la exija) |
| `categoria_id` | FK → `categorias.id`. Un producto pertenece a UNA categoría |
| `activo` | `default=True`. La columna del borrado lógico |

**La relación:** `product.categoria.nombre` te da la categoría del producto. Y gracias a `backref="productos"`, `categoria.productos` te da la lista de productos de esa categoría.

### Importar y migrar

`models/__init__.py`:

```python
from .role import RoleModel
from .category import CategoryModel
from .user import UserModel
from .product import ProductModel
```

```bash
flask db migrate -m "agregar tabla productos"
flask db upgrade
```

---

## 4. Schema de productos (10 min)

### schemas/product.py

```python
from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    nombre: str
    precio: float
    stock: int
    categoria_id: int


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    precio: float
    stock: int
    imagen_url: str | None
    categoria_id: int
    activo: bool
```

**Prestá atención a lo que NO está en `ProductCreate`:**

| Campo | ¿Por qué no lo manda el cliente? |
|-------|----------------------------------|
| `codigo` | Lo genera el servidor con `generar_codigo()`. El cliente no decide su código |
| `imagen_url` | La genera Cloudinary al subir el archivo |

¿Y `imagen_url: str | None`? Es unión de tipos: puede ser un `str` o `None`. Es la forma de pydantic v2 para decir "campo opcional".

### schemas/__init__.py

```python
from .auth import RegisterSchema, LoginSchema
from .role import RoleCreate, RoleResponse
from .category import CategoryCreate, CategoryResponse
from .user import UserCreate, UserResponse
from .product import ProductCreate, ProductResponse
```

---

## 5. Resource de productos (45 min)

**La gran novedad:** hasta ahora todo era JSON (`request.get_json()`). Pero un producto viene con un ARCHIVO. Cuando viaja un archivo, el cuerpo de la petición es `multipart/form-data`. Ahí los datos llegan en `request.form` (textos) y `request.files` (el archivo).

### resources/productResource.py

```python
from flask_restful import Resource
from flask import request
from pydantic import ValidationError
from db import db
from models.product import ProductModel
from models.category import CategoryModel
from schemas.product import ProductCreate, ProductResponse
from utils.helpers import CloudinaryHelper


def generar_codigo():
    cantidad = ProductModel.query.count()
    return "P-" + str(cantidad + 1).zfill(5)


class ProductResource(Resource):
    def get(self):
        productos = ProductModel.query.filter_by(activo=True).all()
        return [ProductResponse.model_validate(p).model_dump(mode="json") for p in productos], 200

    def post(self):
        if "imagen" not in request.files:
            return {"msg": "La imagen es obligatoria"}, 400

        file = request.files["imagen"]
        if not CloudinaryHelper.validate_image(file.filename):
            return {"msg": "Formato de imagen no válido"}, 400

        try:
            data = ProductCreate(**request.form.to_dict())
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        if not db.session.get(CategoryModel, data.categoria_id):
            return {"msg": "La categoría no existe"}, 404

        imagen_url = CloudinaryHelper.upload(file)

        product = ProductModel(
            codigo=generar_codigo(),
            nombre=data.nombre,
            precio=data.precio,
            stock=data.stock,
            imagen_url=imagen_url,
            categoria_id=data.categoria_id,
        )
        db.session.add(product)
        db.session.commit()

        return ProductResponse.model_validate(product).model_dump(mode="json"), 201

    def put(self):
        product_id = request.form.get("id", type=int)
        product = db.session.get(ProductModel, product_id)
        if not product:
            return {"msg": "Producto no encontrado"}, 404

        try:
            data = ProductCreate(**request.form.to_dict())
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        product.nombre = data.nombre
        product.precio = data.precio
        product.stock = data.stock
        product.categoria_id = data.categoria_id

        if "imagen" in request.files and request.files["imagen"].filename:
            file = request.files["imagen"]
            if not CloudinaryHelper.validate_image(file.filename):
                return {"msg": "Formato de imagen no válido"}, 400
            product.imagen_url = CloudinaryHelper.upload(file)

        db.session.commit()

        return ProductResponse.model_validate(product).model_dump(mode="json"), 200

    def delete(self):
        product_id = request.form.get("id", type=int)
        product = db.session.get(ProductModel, product_id)
        if not product:
            return {"msg": "Producto no encontrado"}, 404

        product.activo = False
        db.session.commit()

        return {"msg": "Producto desactivado"}, 200
```

### Desglose del código autogenerado

```python
def generar_codigo():
    cantidad = ProductModel.query.count()
    return "P-" + str(cantidad + 1).zfill(5)
```

Desarmémoslo:
- `query.count()` → cuántos productos hay (ej: 0)
- `cantidad + 1` → el número del nuevo código (1)
- `str(1).zfill(5)` → `"00001"` (rellena con ceros a la izquierda hasta 5 dígitos)
- `"P-" + "00001"` → `"P-00001"`

### Desglose de POST — crear producto

1. **¿Hay imagen?** `if "imagen" not in request.files` → **400** "La imagen es obligatoria". Acá el orden importa: validar la imagen ANTES de perder tiempo validando el resto.
2. **¿Formato válido?** `validate_image` → **400** si es un `.txt` o `.exe`
3. **¿Datos válidos?** `ProductCreate(**request.form.to_dict())` → **400** si falta precio, etc.
4. **¿Existe la categoría?** → **404**
5. **Subir a la nube:** `CloudinaryHelper.upload(file)` → devuelve la URL
6. **Crear** con `codigo=generar_codigo()` + `imagen_url` → **201**

### Desglose de PUT — actualizar

El `id` viene en el formulario: `request.form.get("id", type=int)` — el `type=int` convierte el texto a entero.

La imagen es **opcional**: solo se reemplaza si `request.files["imagen"].filename` tiene nombre (es decir, el cliente eligió un archivo). El código NO se modifica.

### Desglose de DELETE — borrado lógico

```python
product.activo = False
db.session.commit()
```

¿Ves? NO hay `db.session.delete()`. Es un UPDATE de `activo` a `False`.

**¿Por qué?** Porque en la sesión 4 los productos van a aparecer en `venta_detalles`. Si borras un producto físicamente, rompes el historial de ventas (una venta apuntaría a un producto inexistente). Con `activo=False`:
- `GET /api/productos` lo esconde (filtra `activo=True`)
- El historial de ventas se conserva intacto

Ese es el patrón estándar de los e-commerce de verdad.

### Registrar la ruta

`resources/__init__.py`:

```python
from .authResource import RegisterResource, LoginResource
from .roleResource import RoleResource
from .categoryResource import CategoryResource
from .productResource import ProductResource
```

`router/__init__.py`:

```python
from flask_restful import Api
from resources import RegisterResource, LoginResource, RoleResource, CategoryResource, ProductResource


def register_routes(api: Api):
    api.add_resource(RegisterResource, "/api/auth/register")
    api.add_resource(LoginResource, "/api/auth/login")
    api.add_resource(RoleResource, "/api/roles")
    api.add_resource(CategoryResource, "/api/categorias")
    api.add_resource(ProductResource, "/api/productos")
```

---

## 6. Pruebas en Postman (35 min)

### Crear un producto (POST) — con form-data

- **POST** `http://127.0.0.1:5000/api/productos`
- En **Body**, elegí **form-data** (NO raw)
- Agregá estas filas:

| Key | Value | Tipo |
|-----|-------|------|
| nombre | Laptop Gamer | Text |
| precio | 3500 | Text |
| stock | 10 | Text |
| categoria_id | 1 | Text |
| imagen | (tu archivo .jpg o .png) | **File** |

**Requisito:** la categoría `id: 1` debe existir (la creaste en la semana 7). Si no, créala primero con POST `/api/categorias`.

Resultado: **201** con `codigo: "P-00001"` y un `imagen_url` larguísimo. **Copiá esa URL y abrila en el navegador.** ¡Tu imagen está viviendo en la nube!

### Listar (GET)

- **GET** `http://127.0.0.1:5000/api/productos` → lista de productos activos

### Actualizar (PUT)

- **PUT** `http://127.0.0.1:5000/api/productos`
- form-data:

| Key | Value | Tipo |
|-----|-------|------|
| id | 1 | Text |
| nombre | Laptop Gamer 16GB | Text |
| precio | 4000 | Text |
| stock | 8 | Text |
| categoria_id | 1 | Text |

- Sin imagen → la URL no cambia. Después agregá `imagen` tipo File → la URL cambia

### Borrar (DELETE) — el borrado lógico

- **DELETE** `http://127.0.0.1:5000/api/productos`
- form-data: `id = 1`
- Resultado: **200** `{"msg": "Producto desactivado"}`
- GET `/api/productos` → ya no aparece. Pero mirá la BD → sigue ahí, con `activo = false`

### Probar los errores (importante)

| Prueba | Resultado |
|--------|-----------|
| POST sin `imagen` | **400** "La imagen es obligatoria" |
| POST con archivo `.txt` | **400** "Formato de imagen no válido" |
| POST sin `precio` | **400** con `errores` |
| POST con `categoria_id` inexistente | **404** "La categoría no existe" |
| PUT/DELETE con `id` inexistente | **404** "Producto no encontrado" |

### Verificar en pgAdmin

```sql
SELECT id, codigo, nombre, precio, stock, imagen_url, categoria_id, activo FROM productos;
```

---

## Resumen de conceptos

| Tema | Conceptos clave |
|------|-----------------|
| Cloudinary | Nube para imágenes, en la BD solo la URL |
| Credenciales | Cloud name, API key, API secret en `.env` |
| `CloudinaryHelper` | `validate_image`, `upload`, `secure_url`, `@staticmethod` |
| Código | `generar_codigo()`, `count()`, `zfill(5)` |
| Multipart | `request.form` + `request.files`, form-data en Postman |
| Borrado lógico | `activo=False` en vez de `delete()`, filtrar en GET |
| `str \| None` | Unión de tipos: campo opcional en pydantic v2 |
