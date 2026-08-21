from flask import request
from flask_restful import Resource
from pydantic import ValidationError
from db import db
from schemas import SaleSchema
from models import CustomerModel, ProductsModel, SaleDetailModel, SalesModel
from datetime import datetime
import requests
import os

class SaleResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            validated_data = SaleSchema(**data)
            # 01 - Fase customers
            customer = CustomerModel.query.filter_by(document_number=validated_data.customer.document_number).first()

            if not customer:
                new_customer = CustomerModel(
                    name=validated_data.customer.name,
                    last_name=validated_data.customer.last_name,
                    email=validated_data.customer.email,
                    document_number=validated_data.customer.document_number,
                    address=validated_data.customer.address
                )
                db.session.add(new_customer)
                customer = new_customer
            else:
                customer.name = validated_data.customer.name
                customer.last_name = validated_data.customer.last_name
                customer.email = validated_data.customer.email
                customer.address = validated_data.customer.address

            db.session.flush()


            # { "product_id": 2, "quantity": 1, "price": 1180.00, "subtotal": 1180.00 }
            # 02 - Fase Productos (sales_details, products)
            new_sale_details = []
            for sale_detail in validated_data.sale_details:
                product = ProductsModel.query.get(sale_detail.product_id)

                if not product:
                    return {
                        "msg": "Producto no encontrado"
                    }, 400
                if not product.is_active:
                    return {
                        "msg": "Producto no se encuentra disponible"
                    }, 400
                if sale_detail.quantity > product.stock:
                    return {
                        "msg": "Stock insuficiente"
                    }, 400

                product.stock = product.stock - sale_detail.quantity
                new_sale_details.append(SaleDetailModel(
                    quantity=sale_detail.quantity,
                    price=sale_detail.price,
                    total=sale_detail.subtotal,
                    product_id=sale_detail.product_id
                ))

            # 03 - Fase Coorelativos - CODIGOS VENTA
            # Ultimo coorelativo ya emitido
            ULTIMO_CORRELATIVO_NUBEFACT = 3
            last_sale = SalesModel.query.order_by(SalesModel.id.desc()).first()

            if last_sale:
                last_number = int(last_sale.code.split("-")[1])
            else:
                last_number = ULTIMO_CORRELATIVO_NUBEFACT

            sale_code = f"B-{last_number+1}"

            # 04 - Fase de Creacion de Venta junto con su detalle
            new_sale = SalesModel(
                code=sale_code,
                total=validated_data.total,
                customer_id=customer.id
            )
            db.session.add(new_sale)
            db.session.flush()

            for detail in new_sale_details:
                detail.sale_id = new_sale.id
                db.session.add(detail)

            # 05 - Fase de Nubefact => Facturacion
            items = []
            total_gravada = 0 # Total sin IGV
            total_igv = 0     # Total IGV
            total_general = 0 # Gravado + IGV
            # { "product_id": 1, "quantity": 2, "price": 590.00,  "subtotal": 1180.00 }
            for sale_detail in validated_data.sale_details:
                product = ProductsModel.query.get(sale_detail.product_id)

                precio_unitario = sale_detail.price
                total = precio_unitario * sale_detail.quantity
                valor_unitario = precio_unitario / 1.18
                subtotal = total / 1.18
                igv = total - subtotal

                items.append({
                    "unidad_de_medida": "NIU",
                    "codigo": product.code,
                    "descripcion": product.name,
                    "cantidad": sale_detail.quantity,
                    "valor_unitario": round(valor_unitario, 2),
                    "precio_unitario": precio_unitario,
                    "subtotal": round(subtotal, 2),
                    "tipo_de_igv": 1,
                    "igv": round(igv,2),
                    "total": total,
                    "anticipo_regularizacion": False
                })

                total_gravada = total_gravada + subtotal
                total_igv = total_igv + igv
                total_general = total_general + total

            # Vamos a terminar de armar el Payload que se envia Nubefact
            payload = {
                "operacion": "generar_comprobante",
                "tipo_de_comprobante": 2, # 1=> Facturas 2=> Boletas
                "serie": "BBB1", # Boleta => BBB1 , Factura => FFF1
                "numero": int(new_sale.code.split("-")[1]),  # B-8 => 8
                "sunat_transaction": 1,
                "cliente_tipo_de_documento": 1, # DNI => 1 , RUC => 6
                "cliente_numero_de_documento": customer.document_number,
                "cliente_denominacion": f"{customer.name} {customer.last_name}",
                "cliente_direccion": customer.address,
                "cliente_email": customer.email,
                "fecha_de_emision": datetime.now().strftime('%d-%m-%Y'),
                "moneda":1,   # PEN => 1 , USD => 2 tipo_de_cambio
                "porcentaje_de_igv": 18.00,
                "total_gravada": round(total_gravada,2),
                "total_igv": round(total_igv,2),
                "total": round(total_general,2),
                "enviar_automaticamente_a_la_sunat": True,
                "enviar_automaticamente_al_cliente": True,
                "items": items
            }
            # Vamos a comunicarnos con NUBEFACT y enviaremos nuestra data
            # Para que se genere la factura
            response = requests.post(
                url=os.getenv("NUBEFACT_URL"),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + os.getenv('NUBEFACT_TOKEN')
                },
                json=payload
            )

            # Si nufecat me rechaza,lanzar un error
            if response.status_code != 200:
                raise Exception(response.json()['errors'])

            # Si todo sale OK
            new_sale.status = "CONFIRMED"
            db.session.commit()

            return {
                "message": "Producto vendido exitosamente",
                "nubefact": response.json()
            }
        except ValidationError as e:
            return {
                "msg": e.errors()
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                "msg": str(e)
            }, 500