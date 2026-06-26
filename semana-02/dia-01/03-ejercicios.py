# productos = [
#     {"nombre": "Laptop", "precio": 2499.99, "stock": 15},
#     {"nombre": "Mouse", "precio": 45.50, "stock": 30},
#     {"nombre": "Teclado", "precio": 5020.00, "stock": 8},
#     {"nombre": "Parlante", "precio": 75.00, "stock": 20},
# ]

# # Mostrar solo los productos con precio menor a S/100

# print("Precior menor a 100")
# for prod in productos:
#    if prod["precio"] < 100:
#       print(f"El producto {prod["nombre"]} tiene un precio de {prod["precio"]}")

# # Mostrar solo los que tienen stock menor a 10

# print("Stock menor a 10")
# for prod in productos:
#    if prod["stock"] < 10:
#       print(f"El producto {prod["nombre"]} tiene un stock {prod["stock"]}")

# # Encontrar el producto más caro

# producto_mas_caro = productos[0]["precio"]  # 2499.99

# for prod in productos:
#    if prod["precio"] >= producto_mas_caro:
#       producto_mas_caro = prod["precio"]

# print(f"El precio del producto mas caro es {producto_mas_caro} ")

# # Agrega a un arreglo solo aquellos productos que superen las 10 unidades
# productos_varias_unidades = []

# for prod in productos:
#    if prod["stock"] > 10:
#       productos_varias_unidades.append(prod["nombre"])

# print(productos_varias_unidades)


# clientes = [
#     {"nombre": "Ana", "deuda": 150.00, "dias_atraso": 45},
#     {"nombre": "Luis", "deuda": 0, "dias_atraso": 0},
#     {"nombre": "Sofia", "deuda": 320.50, "dias_atraso": 60},
#     {"nombre": "Carlos", "deuda": 75.00, "dias_atraso": 15},
#     {"nombre": "Marta", "deuda": 0, "dias_atraso": 0},
# ]


# clientes_sin_deuda = []

# for clie in clientes:
#    if clie["deuda"] == 0:
#       clientes_sin_deuda.append(clie)

# print(clientes_sin_deuda)



catalogo = [
    {"codigo": "LAP-001", "nombre": "Laptop Gamer", "precio": 3499.99, "stock": 5},
    {"codigo": "MOU-001", "nombre": "Mouse Inalambrico", "precio": 45.50, "stock": 20},
    {"codigo": "TEC-001", "nombre": "Teclado Mecanico", "precio": 120.00, "stock": 0},
    {"codigo": "MON-001", "nombre": "Monitor 4K", "precio": 899.00, "stock": 3},
]

for elmt in catalogo:
   print(f"Codigo: {elmt["codigo"]} Nombre: {elmt["nombre"]} Precio: {elmt["precio"]}")


codigo = input("Introduce tu codigo: ") # LAP-001
encontrado = None # Una variable en blanco o vacia  {"codigo": "LAP-001", "nombre": "Laptop Gamer", "precio": 3499.99, "stock": 5}

for producto in catalogo:
   if producto["codigo"] == codigo:
      encontrado = producto
      break

if encontrado:
   print(encontrado)

else:
   print("Lo siento no encontramos el producto")
