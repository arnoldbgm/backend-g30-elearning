# Facturación Electrónica con Nubefact

> Guía para la clase de hoy: construir el endpoint `POST /api/v1/sales` que registra una
> venta en nuestra base de datos y, al mismo tiempo, genera el **comprobante electrónico
> (factura)** a través de Nubefact para enviarlo a la SUNAT.
>
> **Metodología:** vamos a construir la lógica **en fases**. Cada fase agrega un bloque
> nuevo al mismo `Resource`, para que sea fácil de seguir. Al final juntamos todo.

---

## 0. El mapa de la clase

| Fase | Qué construimos | JSON de ejemplo |
|---|---|---|
| **Fase 1** | Buscar o crear el cliente (upsert por DNI) | `customer` |
| **Fase 2** | Recorrer los productos: validar y descontar stock | `sale_details` |
| **Fase 3** | Código correlativo de venta (opcional, arranca en `B-0004`) | — |
| **Fase 4** | Crear la venta y sus detalles | venta completa |
| **Fase 5** | Generar el comprobante de pago (Nubefact) | payload a Nubefact |

El JSON **final** que enviaremos desde el cliente:

```json
{
  "total": 2360.00,
  "customer": {
    "name": "Juan",
    "last_name": "Perez",
    "email": "juan.perez@example.com",
    "document_number": "45678912",
    "address": "Av. Los Alamos 123, Lima"
  },
  "sale_details": [
    { "product_id": 1, "quantity": 2, "price": 590.00,  "subtotal": 1180.00 },
    { "product_id": 2, "quantity": 1, "price": 1180.00, "subtotal": 1180.00 }
  ]
}
```

Precios **con IGV incluido**: 590 → base 500 + IGV 90 · 1180 → base 1000 + IGV 180.
Total gravada = 2000 · IGV = 360 · Total general = 2360.

---

## 1. Conceptos rápidos (para la clase)

| Concepto | Qué es |
|---|---|
| **Boleta** | Comprobante para personas naturales. No da derecho a crédito fiscal. |
| **Factura** | Comprobante para empresas/clientes con RUC. En nuestro caso `tipo_de_comprobante = 2`. |
| **IGV** | Impuesto del 18%. Nuestros precios **ya incluyen IGV**, por eso la base gravada es `total / 1.18`. |
| **Valor unitario** | Precio sin IGV → `precio / 1.18` |
| **Nubefact** | Proveedor que recibe nuestra data y genera el XML/PDF para SUNAT, e incluso lo envía por correo. |
| **Serie** | Prefijo del comprobante (ej. `F001`, `BBB1`). |
| **flush()** | Envía la sentencia a la BD **sin hacer commit** (nos sirve para obtener el `id` antes de guardar). |
| **commit()** | Confirma y hace permanente todo lo pendiente en la BD. |
| **rollback()** | Deshace todo lo pendiente (usado cuando algo falla). |

---

## 2. Base de cada fase: schemas y esqueleto del Resource

Creamos `schemas/sale_schemas.py`:

```python
from pydantic import BaseModel, Field


class CustomerSchema(BaseModel):
    name: str
    last_name: str
    email: str
    document_number: str
    address: str


class SaleDetailSchema(BaseModel):
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)          # Precio unitario (IGV incluido)
    subtotal: float = Field(gt=0)       # Total de la línea = price * quantity
    product_id: int


class SaleSchema(BaseModel):
    total: float = Field(gt=0)
    customer: CustomerSchema
    sale_details: list[SaleDetailSchema]
```

Registrarlo en `schemas/__init__.py`:

```python
from .sale_schemas import CustomerSchema, SaleDetailSchema, SaleSchema
```

Creamos `resources/sale_resources.py` con el **esqueleto** que iremos completando:

```python
from flask import request
from flask_restful import Resource
from pydantic import ValidationError
from db import db
from schemas import SaleSchema
from models import CustomerModel, ProductsModel, SalesModel, SaleDetailModel
from models.sales_model import SaleStatus
import requests
import os
from datetime import datetime


class SaleResource(Resource):

    def post(self):
        try:
            data = request.get_json()
            validated_data = SaleSchema(**data)

            # >>> aquí agregamos el código de cada fase <<<

            return {'message': 'Sale created successfully'}, 200

        except ValidationError as e:
            return {'error': e.errors()}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
```

---

## 3. Fase 1 — El cliente: ¿existe o lo creamos?

**Objetivo:** dado el `document_number` del cliente, buscarlo en la tabla `customers`.
Si no existe, crearlo. Si existe, actualizar sus datos. Al final conocer su `id` (gracias
al `flush()`).

**Código que agregamos:**

```python
            # 1. Buscar por su número de documento (DNI)
            customer = CustomerModel.query.filter_by(
                document_number=validated_data.customer.document_number
            ).first()

            # 2. ¿No existe? Lo creamos
            if not customer:
                customer = CustomerModel(
                    name=validated_data.customer.name,
                    last_name=validated_data.customer.last_name,
                    email=validated_data.customer.email,
                    document_number=validated_data.customer.document_number,
                    address=validated_data.customer.address
                )
                db.session.add(customer)
            else:
                # 3. Ya existe: actualizamos sus datos
                customer.name = validated_data.customer.name
                customer.last_name = validated_data.customer.last_name
                customer.email = validated_data.customer.email
                customer.address = validated_data.customer.address

            db.session.flush()      # obtenemos customer.id sin guardar aún
```

**JSON de ejemplo (la parte que usamos en esta fase):**

```json
{
  "customer": {
    "name": "Juan",
    "last_name": "Perez",
    "email": "juan.perez@example.com",
    "document_number": "45678912",
    "address": "Av. Los Alamos 123, Lima"
  }
}
```

**Qué pasa:**

1. Primera vez: `45678912` no está en la BD → se **crea** el cliente.
2. Segunda vez con el mismo DNI: el cliente **ya existe** → se actualiza su email/dirección.
3. `db.session.flush()` → la BD ya asignó el `id` (ej. `1`) pero todavía no está guardado.

> 💡 Este patrón se llama **upsert**: `update` + `insert`.

---

## 4. Fase 2 — Los productos: validar y descontar stock

**Objetivo:** recorrer `sale_details`, y por cada producto: verificar que exista, que esté
activo y que tenga stock suficiente. Si todo está bien, **descontar el stock** y guardar el
detalle de la venta en una lista temporal.

**Código que agregamos:**

```python
            new_sale_details = []

            for sale_detail in validated_data.sale_details:
                product = ProductsModel.query.get(sale_detail.product_id)

                if not product:
                    return {'error': 'Product not found'}, 404

                if not product.is_active:
                    return {'error': 'Product is out of stock'}, 404

                if product.stock < sale_detail.quantity:
                    return {'error': 'Not enough stock'}, 400

                # Descontar el stock vendido
                product.stock -= sale_detail.quantity

                # Guardar el detalle (aún sin sale_id, lo asignamos en la Fase 4)
                new_sale_details.append(SaleDetailModel(
                    quantity=sale_detail.quantity,
                    price=sale_detail.price,
                    total=sale_detail.subtotal,      # nuestro modelo usa la columna 'total'
                    product_id=sale_detail.product_id
                ))
```

**JSON de ejemplo (la parte que usamos en esta fase):**

```json
{
  "sale_details": [
    { "product_id": 1, "quantity": 2, "price": 590.00,  "subtotal": 1180.00 },
    { "product_id": 2, "quantity": 1, "price": 1180.00, "subtotal": 1180.00 }
  ]
}
```

**Qué pasa:**

1. Producto 1 existe, está activo y tiene stock (ej. `10`) → stock queda en `8`.
2. Producto 2 igual → stock queda en `9`.
3. Si algún producto no existe / está inactivo / no alcanza el stock → **retorna error** y
   nada se guarda.

> 💡 Nota: el código original usaba `product.status`; nuestro modelo usa `product.is_active`.

---

## 5. Fase 3 — Código correlativo de venta *(opcional, la más simple)*

**Objetivo:** generar un código único por venta: `B-0004`, `B-0005`, ... tomando como base
la última venta registrada. Como ya emitimos comprobantes en Nubefact hasta el **3**,
arrancamos en el **4**.

**Código que agregamos:**

```python
            # Último correlativo ya emitido en Nubefact antes de usar el sistema
            ULTIMO_CORRELATIVO_NUBEFACT = 3

            last_sale = SalesModel.query.order_by(SalesModel.id.desc()).first()

            if last_sale:
                last_number = int(last_sale.code.split('-')[1])
            else:
                last_number = ULTIMO_CORRELATIVO_NUBEFACT   # sin ventas: partimos del 3

            sale_code = f'B-{str(last_number + 1).zfill(4)}'   # 'B-0004'
```

**Explicación rápida:**

- No hay ventas en BD → `last_number = 3` → el código es `B-0004` (no se duplica con
  los comprobantes que ya emitiste en Nubefact).
- Ya hay ventas → tomamos el último número guardado y le sumamos 1.
- `split('-')[1]` → toma la parte numérica del código.
- `zfill(4)` → rellena con ceros a la izquierda (4 dígitos).

> 💡 El valor `3` puede ir en el `.env` como `ULTIMO_CORRELATIVO_NUBEFACT` si prefieres
> no tocarlo en el código.

---

## 6. Fase 4 — Crear la venta y sus detalles

**Objetivo:** crear el registro en la tabla `sales` y asociarle cada detalle de la Fase 2.

**Código que agregamos:**

```python
            sale = SalesModel(
                code=sale_code,                     # de la Fase 3
                total=validated_data.total,
                customer_id=customer.id             # de la Fase 1
            )
            db.session.add(sale)
            db.session.flush()                      # obtenemos sale.id

            # Nuestros modelos no tienen relaciones, por eso asignamos el sale_id a mano
            for detail in new_sale_details:
                detail.sale_id = sale.id
                db.session.add(detail)
```

**JSON de ejemplo (ya completo, lo que usa esta fase):**

```json
{
  "total": 2360.00,
  "customer": {
    "name": "Juan",
    "last_name": "Perez",
    "email": "juan.perez@example.com",
    "document_number": "45678912",
    "address": "Av. Los Alamos 123, Lima"
  },
  "sale_details": [
    { "product_id": 1, "quantity": 2, "price": 590.00,  "subtotal": 1180.00 },
    { "product_id": 2, "quantity": 1, "price": 1180.00, "subtotal": 1180.00 }
  ]
}
```

**Qué pasa:**

1. Se crea la venta con código `B-0004`, total `2360.00` y el `customer_id` del cliente.
2. `flush()` → la BD le asigna `sale.id = 1`.
3. Cada detalle temporal recibe ese `sale_id` y se agrega a la sesión.

> ⚠️ **Aún no hacemos `commit()`.** Guardamos eso para la Fase 5, cuando sepamos si Nubefact
> aceptó o no la factura.

---

## 7. Fase 5 — El comprobante de pago (Nubefact)

**Objetivo:** armar el payload con los totales e ítems, enviarlo a Nubefact y, **solo si
responde OK**, confirmar la venta con `commit()`.

**Código que agregamos** (antes del `return` del esqueleto):

```python
            # ---- Cálculo de los totales (el precio incluye IGV) ----
            items = []
            total_gravada = 0      # suma de subtotales (sin IGV)
            total_igv = 0          # suma del IGV (18%)
            total_general = 0      # suma total (gravada + igv)

            for sale_detail in validated_data.sale_details:
                product = ProductsModel.query.get(sale_detail.product_id)

                precio_unitario = sale_detail.price
                total = precio_unitario * sale_detail.quantity
                valor_unitario = precio_unitario / 1.18      # precio sin IGV
                subtotal = total / 1.18                      # base gravada
                igv = total - subtotal

                items.append({
                    'unidad_de_medida': 'NIU',          # Catálogo SUNAT: "Unidad"
                    'codigo': product.code,
                    'descripcion': product.name,
                    'cantidad': sale_detail.quantity,
                    'valor_unitario': round(valor_unitario, 2),
                    'precio_unitario': precio_unitario,
                    'subtotal': round(subtotal, 2),
                    'tipo_de_igv': 1,                   # 1 = gravado
                    'igv': round(igv, 2),
                    'total': total,
                    'anticipo_regularizacion': False
                })

                total_gravada += subtotal
                total_igv += igv
                total_general += total

            # ---- Armamos el payload para Nubefact ----
            payload = {
                'operacion': 'generar_comprobante',
                'tipo_de_comprobante': 2,                 # 2 = FACTURA
                'serie': 'BBB1',
                'numero': int(sale.code.split('-')[1]),   # correlativo de la Fase 3
                'sunat_transaction': 1,                   # 1 = venta interna
                'cliente_tipo_de_documento': 1,           # 1 = DNI
                'cliente_numero_de_documento': customer.document_number,
                'cliente_denominacion': f'{customer.name} {customer.last_name}',
                'cliente_direccion': customer.address,
                'cliente_email': customer.email,
                'fecha_de_emision': datetime.now().strftime('%d-%m-%Y'),
                'moneda': 1,                              # 1 = Soles (PEN)
                'porcentaje_de_igv': 18.00,
                'total_gravada': round(total_gravada, 2),
                'total_igv': round(total_igv, 2),
                'total': round(total_general, 2),
                'enviar_automaticamente_a_la_sunat': True,
                'enviar_automaticamente_al_cliente': True,
                'items': items
            }

            # ---- Llamada HTTP a Nubefact ----
            response = requests.post(
                url=os.getenv('NUBEFACT_URL'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + os.getenv('NUBEFACT_TOKEN')
                },
                json=payload
            )

            # ---- Si Nubefact rechazó, lanzamos error (activará el rollback) ----
            if response.status_code != 200:
                raise Exception(response.json()['errors'])

            # ---- Todo OK: confirmamos la venta y persistimos ----
            sale.status = SaleStatus.CONFIRMED
            db.session.commit()
```

**JSON de ejemplo (lo que Nubefact recibe):**

```json
{
  "operacion": "generar_comprobante",
  "tipo_de_comprobante": 2,
  "serie": "BBB1",
  "numero": 4,
  "sunat_transaction": 1,
  "cliente_tipo_de_documento": 1,
  "cliente_numero_de_documento": "45678912",
  "cliente_denominacion": "Juan Perez",
  "cliente_direccion": "Av. Los Alamos 123, Lima",
  "cliente_email": "juan.perez@example.com",
  "fecha_de_emision": "14-08-2026",
  "moneda": 1,
  "porcentaje_de_igv": 18.00,
  "total_gravada": 2000.00,
  "total_igv": 360.00,
  "total": 2360.00,
  "enviar_automaticamente_a_la_sunat": true,
  "enviar_automaticamente_al_cliente": true,
  "items": [
    {
      "unidad_de_medida": "NIU",
      "codigo": "P-00001",
      "descripcion": "Polera Negra",
      "cantidad": 2,
      "valor_unitario": 500.00,
      "precio_unitario": 590.00,
      "subtotal": 1000.00,
      "tipo_de_igv": 1,
      "igv": 180.00,
      "total": 1180.00,
      "anticipo_regularizacion": false
    },
    {
      "unidad_de_medida": "NIU",
      "codigo": "P-00002",
      "descripcion": "Polo Blanco",
      "cantidad": 1,
      "valor_unitario": 1000.00,
      "precio_unitario": 1180.00,
      "subtotal": 1000.00,
      "tipo_de_igv": 1,
      "igv": 180.00,
      "total": 1180.00,
      "anticipo_regularizacion": false
    }
  ]
}
```

**Qué pasa:**

1. Calculamos por cada ítem su base gravada, IGV y total.
2. Enviamos el payload a Nubefact con el token del `.env`.
3. Si Nubefact responde `200` → confirmamos la venta y `commit()` (se guarda todo:
   cliente, venta, detalles y stock).
4. Si Nubefact responde error → `raise Exception` → cae en el `except` → `rollback()`
   deshace **todo** (nada queda a medias).

---

## 8. Código completo del Resource (para referencia)

```python
from flask import request
from flask_restful import Resource
from pydantic import ValidationError
from db import db
from schemas import SaleSchema
from models import CustomerModel, ProductsModel, SalesModel, SaleDetailModel
from models.sales_model import SaleStatus
import requests
import os
from datetime import datetime


class SaleResource(Resource):

    def get(self):
        try:
            sales = SalesModel.query.order_by(SalesModel.id.desc()).all()

            response = []
            for sale in sales:
                customer = CustomerModel.query.get(sale.customer_id)
                details = SaleDetailModel.query.filter_by(sale_id=sale.id).all()

                sale_details = []
                for detail in details:
                    product = ProductsModel.query.get(detail.product_id)
                    sale_details.append({
                        'id': detail.id,
                        'quantity': detail.quantity,
                        'subtotal': float(detail.total),
                        'product': {
                            'id': product.id,
                            'name': product.name,
                            'description': product.description
                        }
                    })

                response.append({
                    'id': sale.id,
                    'code': sale.code,
                    'total': float(sale.total),
                    'status': sale.status.value,
                    'created_at': str(sale.created_at),
                    'customer': {
                        'id': customer.id,
                        'name': customer.name,
                        'last_name': customer.last_name,
                        'email': customer.email,
                        'document_number': customer.document_number,
                        'address': customer.address
                    },
                    'sale_details': sale_details
                })

            return {'message': 'Sales fetched successfully', 'data': response}, 200
        except Exception as e:
            return {'error': str(e)}, 400

    def post(self):
        try:
            data = request.get_json()
            validated_data = SaleSchema(**data)

            new_sale_details = []
            items = []
            total_gravada = 0
            total_igv = 0
            total_general = 0

            # ---------- FASE 2: productos, validación y stock ----------
            for sale_detail in validated_data.sale_details:
                product = ProductsModel.query.get(sale_detail.product_id)

                if not product:
                    return {'error': 'Product not found'}, 404
                if not product.is_active:
                    return {'error': 'Product is out of stock'}, 404
                if product.stock < sale_detail.quantity:
                    return {'error': 'Not enough stock'}, 400

                product.stock -= sale_detail.quantity

                new_sale_details.append(SaleDetailModel(
                    quantity=sale_detail.quantity,
                    price=sale_detail.price,
                    total=sale_detail.subtotal,
                    product_id=sale_detail.product_id
                ))

                precio_unitario = sale_detail.price
                total = precio_unitario * sale_detail.quantity
                valor_unitario = precio_unitario / 1.18
                subtotal = total / 1.18
                igv = total - subtotal

                items.append({
                    'unidad_de_medida': 'NIU',
                    'codigo': product.code,
                    'descripcion': product.name,
                    'cantidad': sale_detail.quantity,
                    'valor_unitario': round(valor_unitario, 2),
                    'precio_unitario': precio_unitario,
                    'subtotal': round(subtotal, 2),
                    'tipo_de_igv': 1,
                    'igv': round(igv, 2),
                    'total': total,
                    'anticipo_regularizacion': False
                })

                total_gravada += subtotal
                total_igv += igv
                total_general += total

            # ---------- FASE 1: cliente (upsert) ----------
            customer = CustomerModel.query.filter_by(
                document_number=validated_data.customer.document_number
            ).first()

            if not customer:
                customer = CustomerModel(
                    name=validated_data.customer.name,
                    last_name=validated_data.customer.last_name,
                    email=validated_data.customer.email,
                    document_number=validated_data.customer.document_number,
                    address=validated_data.customer.address
                )
                db.session.add(customer)
            else:
                customer.name = validated_data.customer.name
                customer.last_name = validated_data.customer.last_name
                customer.email = validated_data.customer.email
                customer.address = validated_data.customer.address

            db.session.flush()

            # ---------- FASE 3: código correlativo ----------
            ULTIMO_CORRELATIVO_NUBEFACT = 3

            last_sale = SalesModel.query.order_by(SalesModel.id.desc()).first()

            if last_sale:
                last_number = int(last_sale.code.split('-')[1])
            else:
                last_number = ULTIMO_CORRELATIVO_NUBEFACT

            sale_code = f'B-{str(last_number + 1).zfill(4)}'

            # ---------- FASE 4: crear la venta y sus detalles ----------
            sale = SalesModel(
                code=sale_code,
                total=validated_data.total,
                customer_id=customer.id
            )
            db.session.add(sale)
            db.session.flush()

            for detail in new_sale_details:
                detail.sale_id = sale.id
                db.session.add(detail)

            # ---------- FASE 5: Nubefact (comprobante de pago) ----------
            payload = {
                'operacion': 'generar_comprobante',
                'tipo_de_comprobante': 2,
                'serie': 'BBB1',
                'numero': int(sale.code.split('-')[1]),
                'sunat_transaction': 1,
                'cliente_tipo_de_documento': 1,
                'cliente_numero_de_documento': customer.document_number,
                'cliente_denominacion': f'{customer.name} {customer.last_name}',
                'cliente_direccion': customer.address,
                'cliente_email': customer.email,
                'fecha_de_emision': datetime.now().strftime('%d-%m-%Y'),
                'moneda': 1,
                'porcentaje_de_igv': 18.00,
                'total_gravada': round(total_gravada, 2),
                'total_igv': round(total_igv, 2),
                'total': round(total_general, 2),
                'enviar_automaticamente_a_la_sunat': True,
                'enviar_automaticamente_al_cliente': True,
                'items': items
            }

            response = requests.post(
                url=os.getenv('NUBEFACT_URL'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + os.getenv('NUBEFACT_TOKEN')
                },
                json=payload
            )

            if response.status_code != 200:
                raise Exception(response.json()['errors'])

            sale.status = SaleStatus.CONFIRMED
            db.session.commit()

            return {
                'message': 'Sale created successfully',
                'data': {
                    'id': sale.id,
                    'code': sale.code,
                    'total': float(sale.total)
                }
            }, 200

        except ValidationError as e:
            return {'error': e.errors()}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
```

---

## 9. Registro de la ruta y configuración

### 9.1 `router/__init__.py`

```python
from resources import (UserResource,
                       CategoryResource,
                       OneCategoryResource,
                       RegisterResource,
                       LoginResource,
                       ProductResource,
                       SaleResource)

def register_routes(api: Api):
    api.add_resource(UserResource, "/api/users")
    api.add_resource(CategoryResource, "/api/v1/categories")
    api.add_resource(OneCategoryResource, "/api/v1/categories/<int:id>")
    api.add_resource(RegisterResource, "/api/v1/user/register")
    api.add_resource(LoginResource, "/api/v1/user/login")
    api.add_resource(ProductResource, "/api/v1/products")
    api.add_resource(SaleResource, "/api/v1/sales")
```

### 9.2 `requirements.txt`

`requests` no está en el proyecto. Agregar:

```
requests==2.32.4
```

### 9.3 `.env`

```env
NUBEFACT_URL=https://api.nubefact.com/api/v1/<tu-token>
NUBEFACT_TOKEN=tu-token-de-nubefact
```

> Nota: según tu plan de Nubefact, el token puede ir como parte de la URL o como header
> `Authorization: Bearer`.

---

## 10. Prueba final con curl

```bash
curl --location --request POST "http://localhost:5000/api/v1/sales" \
  --header "Content-Type: application/json" \
  --data '{
    "total": 2360.00,
    "customer": {
      "name": "Juan",
      "last_name": "Perez",
      "email": "juan.perez@example.com",
      "document_number": "45678912",
      "address": "Av. Los Alamos 123, Lima"
    },
    "sale_details": [
      {
        "product_id": 1,
        "quantity": 2,
        "price": 590.00,
        "subtotal": 1180.00
      },
      {
        "product_id": 2,
        "quantity": 1,
        "price": 1180.00,
        "subtotal": 1180.00
      }
    ]
  }'
```

**Respuesta esperada (200):**

```json
{
  "message": "Sale created successfully",
  "data": {
    "id": 1,
    "code": "B-0004",
    "total": 2360.0
  }
}
```

Para listar ventas:

```bash
curl --location --request GET "http://localhost:5000/api/v1/sales"
```

---

## 11. Errores posibles

| Caso | Respuesta |
|---|---|
| JSON inválido o campos faltantes | `400` con `{"error": [...errores de pydantic...]}` |
| Producto no existe | `404` con `{"error": "Product not found"}` |
| Producto inactivo | `404` con `{"error": "Product is out of stock"}` |
| Stock insuficiente | `400` con `{"error": "Not enough stock"}` |
| Nubefact rechaza la factura | `500` con `{"error": "...errores de Nubefact..."}` y rollback de BD |
| Error interno | `500` con `{"error": "..."}` y rollback |

---

## 12. Para pensar en la clase

- ¿Qué pasa si Nubefact está caído? La venta no se guarda (rollback). ¿Convendría guardarla
  como `PENDING` y reintentar después? (cola de pendientes).
- El modelo de cliente tiene `document_number: String(8)` (DNI). Si mañana vendemos a una
  empresa con RUC (11 dígitos), habría que ajustar el modelo y el `cliente_tipo_de_documento`.
- La serie `BBB1` y el tipo de comprobante (boleta/factura) podrían elegirse según el tipo
  de cliente.
- El `GET` consulta varias tablas en un loop (problema N+1). Con `relationship()` +
  `joinedload` se resuelve en una sola consulta.
