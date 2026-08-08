# Guía — Día 2 (Semana 8): La Venta Completa 🧾💥

Llegamos al final del proyecto. Las 4 sesiones nos prepararon para ESTO: registrar una **venta** de principio a fin, como se hace en una empresa real.

Hoy juntamos TODO lo aprendido:
- Los **schemas anidados** de Pydantic (el momento en que dijimos "gracias por tener schemas")
- El **get-or-create** de clientes con `flush()` (patrón real de producción)
- El **cálculo de IGV 18%** (el impuesto peruano)
- La **factura electrónica** emitida por Nubefact

**Analogía:** hasta hoy tenías la tienda montada (productos en el estante, clientes registrados). Hoy le pones la CAJA REGISTRADORA. Cuando alguien compra, la caja calcula, descuenta stock, y le entrega su factura.

---

## 1. Nubefact y la dependencia requests (10 min)

### 1A — ¿Qué es Nubefact?

**Nubefact** es un servicio peruano de **facturación electrónica**. Cuando vendes, tu API le manda los datos de la operación y Nubefact genera el comprobante válido para SUNAT y se lo envía al cliente por correo.

Para hablar con el API de Nubefact desde Python necesitamos `requests`, el cliente HTTP de Python (sí, el mismo que usamos hace semanas).

A `requirements.txt`:

```
requests==2.32.5
```

```bash
pip install -r requirements.txt
```

### 1B — Credenciales

`.env`:

```
DATABASE_URL=postgresql://postgres:root@localhost:5432/flask-ecommerce
DEBUG=True
JWT_SECRET_KEY=982fbdeb44fdb8170d7d1de931ec72b7164d48cf2788d69724c758a471483194
CLOUDINARY_CLOUD_NAME=du0sspuql
CLOUDINARY_API_KEY=726516987941426
CLOUDINARY_API_SECRET=VCZzgEtDhOuuAFxv30lZATBBYZs
NUBEFACT_URL=https://api.nubefact.com/api/v1/99ae592e-9d4e-4961-84be-dac68239b909
NUBEFACT_TOKEN=25f8c55909bb406eb57325bebc82dd2d1c9dd928eac54613b0ac577ca5333a1a
```

`.env.copy`:

```
NUBEFACT_URL=https://api.nubefact.com/api/v1/TU_TOKEN_URL
NUBEFACT_TOKEN=TU_TOKEN_NUBEFACT
```

> Estas son credenciales de prueba del profe. Cada empresa real tiene las suyas.

---

## 2. NubefactHelper — el último helper (20 min)

Agregamos `import requests` y la clase `NubefactHelper` al final de `utils/helpers.py`. Con esto, el archivo queda COMPLETO: los 3 helpers del proyecto.

```python
import os
from bcrypt import hashpw, gensalt, checkpw
import cloudinary
import cloudinary.uploader
import requests


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


class NubefactHelper:
    @staticmethod
    def emitir_factura(venta, cliente, detalles, email_cliente):
        url = os.getenv("NUBEFACT_URL")
        token = os.getenv("NUBEFACT_TOKEN")
        headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

        serie, numero = venta.correlativo.split("-")

        items = []
        for detalle in detalles:
            items.append(
                {
                    "unidad_de_medida": "NIU",
                    "codigo": detalle.producto.codigo,
                    "descripcion": detalle.producto.nombre,
                    "cantidad": detalle.cantidad,
                    "valor_unitario": detalle.precio_unitario,
                    "precio_unitario": round(detalle.precio_unitario * 1.18, 2),
                    "subtotal": round(detalle.precio_unitario * 1.18 * detalle.cantidad, 2),
                    "tipo_de_igv": "10",
                    "igv": round(detalle.subtotal * 0.18, 2),
                    "total": round(detalle.precio_unitario * 1.18 * detalle.cantidad, 2),
                }
            )

        body = {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": "01",
            "serie": serie,
            "numero": numero,
            "fecha_de_emision": venta.fecha.strftime("%d-%m-%Y"),
            "cliente": {
                "tipo_documento": "6",
                "numero_documento": cliente.documento,
                "razon_social": cliente.nombre,
                "direccion": cliente.direccion,
                "email": email_cliente,
            },
            "moneda": "PEN",
            "enviar_automaticamente": True,
            "items": items,
            "totales": {
                "total_gravado": venta.subtotal,
                "total_igv": venta.igv,
                "total": venta.total,
            },
        }

        response = requests.post(url, json=body, headers=headers)
        return response.json()
```

### Desglose pieza por pieza

| Pieza | ¿Qué hace? |
|-------|-----------|
| `venta.correlativo.split("-")` | `"V-000001"` → serie `"V"`, número `"000001"` |
| `for detalle in detalles:` | Construye una línea de factura por cada producto vendido |
| `detalle.producto.codigo` | Saca el código del producto a través de la relación de SQLAlchemy |
| `precio_unitario * 1.18` | El precio CON IGV incluido (así lo pide el formato) |
| `requests.post(url, json=body, headers=headers)` | Envía el documento a Nubefact con el token en el header |
| `response.json()` | La respuesta del servicio (dice si salió bien o mal) |

**Dato importante de facturación:** en el Perú, el `precio_unitario` que ve el cliente lleva IGV incluido (por eso `* 1.18`), pero el `valor_unitario` es sin IGV. En nuestra BD guardamos el precio SIN IGV. Dos formas de ver el mismo precio.

---

## 3. Los 3 modelos (25 min)

### models/customer.py

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from db import db


class CustomerModel(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    documento: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    direccion: Mapped[str] = mapped_column(String(200), nullable=False)

    __tablename__ = "clientes"
```

**Pregunta que seguro te hiciste:** ¿por qué tamaños tan distintos? `email` es `String(120)` (un correo real cabe de sobra), `telefono` es `String(20)` (número con código de país) y `direccion` es `String(200)`.

**Respuesta:** porque los guardamos en **texto plano**, tal como llegan del frontend. El hash bcrypt lo reservamos para las contraseñas (el acceso); los datos del cliente se guardan normales, como en cualquier tienda real.

### models/sale.py

```python
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from db import db


class SaleModel(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    correlativo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey("clientes.id"), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    igv: Mapped[float] = mapped_column(Float, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="emitida")

    cliente = db.relationship("CustomerModel", backref="ventas")
    detalles = db.relationship("SaleDetailModel", backref="venta", cascade="all, delete-orphan")

    __tablename__ = "ventas"
```

### models/sale_detail.py

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Float, ForeignKey
from db import db


class SaleDetailModel(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    venta_id: Mapped[int] = mapped_column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id: Mapped[int] = mapped_column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    producto = db.relationship("ProductModel")

    __tablename__ = "venta_detalles"
```

### El modelo mental de las relaciones

```
 clientes 1 ──── N  ventas  1 ──── N  venta_detalles  N ──── 1  productos
```

- Una venta pertenece a **un** cliente. Un cliente tiene **muchas** ventas.
- Una venta tiene **muchos** detalles. Cada detalle pertenece a **una** venta.
- Cada detalle es de **un** producto.

**`cascade="all, delete-orphan"`** es la estrella: si borras la venta, sus detalles se borran solos. Los detalles no existen sin su venta. Es "si muere el papá, mueren los hijos".

### models/__init__.py

```python
from .role import RoleModel
from .category import CategoryModel
from .user import UserModel
from .product import ProductModel
from .customer import CustomerModel
from .sale import SaleModel
from .sale_detail import SaleDetailModel
```

### Migración

```bash
flask db migrate -m "agregar tablas clientes, ventas y venta_detalles"
flask db upgrade
```

---

## 4. Los schemas anidados (20 min)

Hasta hoy cada schema era plano. Hoy Pydantic muestra su verdadero poder: **un schema dentro de otro**.

### schemas/customer.py

```python
from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    documento: str
    nombre: str
    email: str
    telefono: str
    direccion: str


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    documento: str
    nombre: str
    email: str
    telefono: str
    direccion: str
```

### schemas/sale.py

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from .customer import CustomerCreate


class SaleDetailCreate(BaseModel):
    producto_id: int
    cantidad: int


class SaleCreate(BaseModel):
    cliente: CustomerCreate
    detalles: list[SaleDetailCreate]


class SaleDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float


class SaleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    correlativo: str
    cliente_id: int
    fecha: datetime
    subtotal: float
    igv: float
    total: float
    estado: str
    detalles: list[SaleDetailResponse]
```

### El JSON que valida `SaleCreate`

```json
{
  "cliente": {
    "documento": "20100039212",
    "nombre": "Empresa SAC",
    "email": "ventas@empresa.com",
    "telefono": "987654321",
    "direccion": "Av. Lima 123"
  },
  "detalles": [
    { "producto_id": 1, "cantidad": 2 }
  ]
}
```

**Mirá lo que logra una sola línea** (`SaleCreate(**request.get_json())`):

| Si el cliente manda... | Pydantic responde |
|------------------------|-------------------|
| Falta el documento del cliente | Error 400 con el detalle |
| `cantidad: "dos"` (texto en vez de número) | Error 400 |
| `detalles: {}` en vez de lista | Error 400 |
| Un campo extra que no existe | Error 400 |

Todo en cascada, todo automático. **ESTE era el momento en que "Pydantic parece exagerado con 2 campos".**

**¿Por qué `SaleDetailCreate` no tiene precio?** Porque el precio NO lo manda el cliente. Lo calcula el servidor con el precio guardado del producto. Nunca confíes en el precio que te envía el frontend.

### schemas/__init__.py

```python
from .auth import RegisterSchema, LoginSchema
from .role import RoleCreate, RoleResponse
from .category import CategoryCreate, CategoryResponse
from .user import UserCreate, UserResponse
from .product import ProductCreate, ProductResponse
from .customer import CustomerCreate, CustomerResponse
from .sale import SaleCreate, SaleResponse
```

---

## 5. El Resource de ventas (50 min)

### resources/saleResource.py

```python
from flask_restful import Resource
from flask import request
from pydantic import ValidationError
from db import db
from models.sale import SaleModel
from models.sale_detail import SaleDetailModel
from models.customer import CustomerModel
from models.product import ProductModel
from schemas.sale import SaleCreate, SaleResponse
from utils.helpers import NubefactHelper

IGV = 0.18


def generar_correlativo():
    ultima = SaleModel.query.order_by(SaleModel.id.desc()).first()
    numero = (ultima.id + 1) if ultima else 1
    return "V-" + str(numero).zfill(6)


class SaleResource(Resource):
    def get(self):
        ventas = SaleModel.query.all()
        return [SaleResponse.model_validate(v).model_dump(mode="json") for v in ventas], 200

    def post(self):
        try:
            data = SaleCreate(**request.get_json())
        except ValidationError as e:
            return {"msg": "Datos inválidos", "errores": e.errors()}, 400

        cliente = CustomerModel.query.filter_by(documento=data.cliente.documento).first()
        if not cliente:
            cliente = CustomerModel(
                documento=data.cliente.documento,
                nombre=data.cliente.nombre,
                email=data.cliente.email,
                telefono=data.cliente.telefono,
                direccion=data.cliente.direccion,
            )
            db.session.add(cliente)
            db.session.flush()

        subtotal = 0
        detalles = []
        for item in data.detalles:
            product = db.session.get(ProductModel, item.producto_id)
            if not product:
                return {"msg": "Producto no encontrado"}, 404
            if product.stock < item.cantidad:
                return {"msg": "Stock insuficiente"}, 400

            line_subtotal = product.precio * item.cantidad
            subtotal = subtotal + line_subtotal
            product.stock = product.stock - item.cantidad

            detalles.append(
                SaleDetailModel(
                    producto_id=product.id,
                    cantidad=item.cantidad,
                    precio_unitario=product.precio,
                    subtotal=line_subtotal,
                )
            )

        igv = round(subtotal * IGV, 2)
        total = round(subtotal + igv, 2)

        venta = SaleModel(
            correlativo=generar_correlativo(),
            cliente_id=cliente.id,
            subtotal=round(subtotal, 2),
            igv=igv,
            total=total,
        )
        venta.detalles = detalles
        db.session.add(venta)
        db.session.commit()

        factura = NubefactHelper.emitir_factura(venta, cliente, detalles, cliente.email)
        venta.estado = "emitida" if factura.get("success") else "pendiente"
        db.session.commit()

        response = SaleResponse.model_validate(venta).model_dump(mode="json")
        response["factura"] = factura
        return response, 201
```

### Paso 1 — El correlativo

```python
def generar_correlativo():
    ultima = SaleModel.query.order_by(SaleModel.id.desc()).first()
    numero = (ultima.id + 1) if ultima else 1
    return "V-" + str(numero).zfill(6)
```

- `order_by(SaleModel.id.desc()).first()` → la venta con el id más alto (la última)
- Si no hay ventas → `numero = 1`; si hay → `ultima.id + 1`
- `zfill(6)` → `"000001"`, y con el prefijo → `"V-000001"`

**¿Diferencia con el código de productos?** En productos usamos `count()` (porque nunca borramos, solo desactivamos). Acá usamos `ultima.id + 1` (porque el correlativo de la factura debe seguir la secuencia real). Dos problemas, dos soluciones.

### Paso 2 — Validación anidada

```python
data = SaleCreate(**request.get_json())
```

Una línea. Cliente completo + toda la lista de detalles, validados. Eso es Pydantic en su salsa.

### Paso 3 — Get-or-create del cliente

```python
cliente = CustomerModel.query.filter_by(documento=data.cliente.documento).first()
if not cliente:
    cliente = CustomerModel(
        ...,
        email=data.cliente.email,
        telefono=data.cliente.telefono,
        ...
    )
    db.session.add(cliente)
    db.session.flush()
```

**Patrón get-or-create:** buscamos por documento. Si existe, lo reutilizamos. Si no, lo creamos.

Detalle fino:
- `flush()` vs `commit()` → `flush()` envía el INSERT para generar el `id`, pero NO lo confirma. Si después algo falla (ej: stock insuficiente), todo se deshace y no queda un cliente huérfano. El `commit()` de verdad lo hacemos al final.

### Paso 4 — El bucle de detalles

```python
for item in data.detalles:
    product = db.session.get(ProductModel, item.producto_id)
    if not product:
        return {"msg": "Producto no encontrado"}, 404
    if product.stock < item.cantidad:
        return {"msg": "Stock insuficiente"}, 400

    line_subtotal = product.precio * item.cantidad
    subtotal = subtotal + line_subtotal
    product.stock = product.stock - item.cantidad
```

Por cada línea:
1. **¿Existe el producto?** → 404
2. **¿Hay stock suficiente?** → 400. La validación de stock es OBLIGATORIA antes de vender
3. Calcula el subtotal de la línea y lo **acumula** (variable acumuladora, como en la semana 1)
4. **Descuenta el stock** modificando `product.stock`

### Paso 5 — IGV y la venta

```python
igv = round(subtotal * IGV, 2)
total = round(subtotal + igv, 2)
```

**La cuenta del impuesto peruano:**

| Concepto | Fórmula | Ejemplo |
|----------|---------|---------|
| Subtotal | — | 7000.00 |
| IGV (18%) | `subtotal * 0.18` | 1260.00 |
| Total | `subtotal + igv` | 8260.00 |

`round(x, 2)` redondea a 2 decimales (céntimos), porque en dinero no se puede dejar 8260.123.

### Paso 6 — La línea más mágica del curso

```python
venta.detalles = detalles
db.session.add(venta)
db.session.commit()
```

**`venta.detalles = detalles`** le dice a SQLAlchemy: "esta venta tiene estos detalles". Gracias a la relación y al `cascade`, UN SOLO commit guarda la venta Y todas sus líneas. No hay que insertar cada detalle a mano.

### Paso 7 — Facturar

```python
factura = NubefactHelper.emitir_factura(venta, cliente, detalles, cliente.email)
venta.estado = "emitida" if factura.get("success") else "pendiente"
db.session.commit()
```

1. **Le pasamos el email en texto plano** — Nubefact lo necesita para mandarle la factura al cliente
2. Llamamos a Nubefact
3. Si respondió `success: true` → `estado = "emitida"`. Si falló → `"pendiente"` (la venta no se pierde, queda para reintentar)
4. La respuesta de Nubefact viaja en la respuesta final

### Registrar la ruta

`resources/__init__.py`:

```python
from .authResource import RegisterResource, LoginResource
from .roleResource import RoleResource
from .categoryResource import CategoryResource
from .productResource import ProductResource
from .saleResource import SaleResource
```

`router/__init__.py`:

```python
from flask_restful import Api
from resources import (
    RegisterResource,
    LoginResource,
    RoleResource,
    CategoryResource,
    ProductResource,
    SaleResource,
)


def register_routes(api: Api):
    api.add_resource(RegisterResource, "/api/auth/register")
    api.add_resource(LoginResource, "/api/auth/login")
    api.add_resource(RoleResource, "/api/roles")
    api.add_resource(CategoryResource, "/api/categorias")
    api.add_resource(ProductResource, "/api/productos")
    api.add_resource(SaleResource, "/api/ventas")
```

---

## 6. Pruebas en Postman (35 min)

### Preparar

Necesitás al menos un producto con stock. Si no tenés, créalo con POST `/api/productos` (recordá: form-data + imagen).

### Registrar una venta (POST)

- **POST** `http://127.0.0.1:5000/api/ventas`
- Body → raw → JSON:

```json
{
  "cliente": {
    "documento": "20100039212",
    "nombre": "Empresa SAC",
    "email": "ventas@empresa.com",
    "telefono": "987654321",
    "direccion": "Av. Lima 123"
  },
  "detalles": [
    { "producto_id": 1, "cantidad": 2 }
  ]
}
```

Resultado esperado: **201** con `correlativo: "V-000001"`, `subtotal`, `igv`, `total`, `estado` y `factura` (la respuesta de Nubefact).

**Verificá la cuenta a mano** (con precio 3500 y cantidad 2):

| Concepto | Cálculo |
|----------|---------|
| Subtotal | 3500 × 2 = **7000** |
| IGV | 7000 × 0.18 = **1260** |
| Total | 7000 + 1260 = **8260** |

### Listar (GET)

- **GET** `http://127.0.0.1:5000/api/ventas` → las ventas con sus detalles anidados

### Probar los errores

| Prueba | Resultado |
|--------|-----------|
| `producto_id: 999` | **404** "Producto no encontrado" |
| `cantidad` mayor al stock | **400** "Stock insuficiente" |
| Cliente sin `documento` | **400** con `errores` |

### El momento "wow" en pgAdmin

```sql
-- La venta y sus totales
SELECT id, correlativo, subtotal, igv, total, estado FROM ventas;

-- El detalle
SELECT venta_id, producto_id, cantidad, precio_unitario, subtotal FROM venta_detalles;

-- El cliente
SELECT documento, nombre, email, telefono FROM clientes;

-- El stock bajó
SELECT id, nombre, stock FROM productos;
```

Mirá la tabla `clientes`: los datos del cliente están en texto plano, tal como los mandaste. El stock del producto bajó porque la venta lo descontó. Todo quedó registrado en la BD.

---

## Resumen de conceptos

| Tema | Conceptos clave |
|------|-----------------|
| Nubefact | Facturación electrónica, `requests.post` con `Bearer` token |
| helpers | `NubefactHelper.emitir_factura` — los 3 helpers completos |
| Modelos | `cascade="all, delete-orphan"`, `backref`, 3 tablas relacionadas |
| Schemas anidados | `SaleCreate` = `cliente` + `detalles`, validación en cascada |
| Get-or-create | `filter_by(...).first()` + `flush()` sin commit |
| IGV | `subtotal * 0.18`, `round(x, 2)` |
| Relación en acción | `venta.detalles = detalles` → un commit guarda todo |
| Estado | `emitida` / `pendiente` según Nubefact |

---

## El proyecto está COMPLETO 🎉

En 4 sesiones construiste una API de e-commerce de verdad:

```
POST  /api/auth/register    Registrar usuario
POST  /api/auth/login       Login (token JWT)
GET   /api/roles            Listar roles (protegido)
POST  /api/roles            Crear rol (protegido)
GET   /api/categorias       Listar categorías
POST  /api/categorias       Crear categoría
GET   /api/productos        Listar productos activos
POST  /api/productos        Crear producto (imagen en Cloudinary)
PUT   /api/productos        Actualizar producto
DELETE/api/productos        Desactivar producto
GET   /api/ventas           Listar ventas
POST  /api/ventas           Registrar venta (IGV + factura en Nubefact)
```

Con usuarios y contraseñas cifradas, tokens JWT, imágenes en la nube, descuento de stock y facturación electrónica. **Eso no lo hace cualquiera. Eso es un backend real.**
