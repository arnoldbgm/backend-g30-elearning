from flask import Flask, request

# class Flask:
#    pass

app = Flask(__name__)

# El cliente hace peticiones
# A donde hace esas peticiones
# A las rutas del backend ( endpoints )
# http://127.0.0.1:5000/allUsers
# http://127.0.0.1:5000/deleteUser

jugadores = [
    {"id": 1, "nombre": "Paolo Guerrero", "edad": 41, "posicion": "Delantero", "equipo": "Alianza Lima", "seleccion": "Peru"},
    {"id": 2, "nombre": "Andre Carrillo", "edad": 33, "posicion": "Extremo", "equipo": "Al Hilal", "seleccion": "Peru"},
    {"id": 3, "nombre": "Renato Tapia", "edad": 29, "posicion": "Mediocampista", "equipo": "Leganes", "seleccion": "Peru"},
    {"id": 4, "nombre": "Lionel Messi", "edad": 38, "posicion": "Delantero", "equipo": "Inter Miami", "seleccion": "Argentina"},
    {"id": 5, "nombre": "Vinicius Jr", "edad": 25, "posicion": "Extremo", "equipo": "Real Madrid", "seleccion": "Brasil"},
    {"id": 6, "nombre": "Luis Diaz", "edad": 28, "posicion": "Extremo", "equipo": "Liverpool", "seleccion": "Colombia"},
    {"id": 7, "nombre": "Federico Valverde", "edad": 27, "posicion": "Mediocampista", "equipo": "Real Madrid", "seleccion": "Uruguay"},
    {"id": 8, "nombre": "Rodrygo", "edad": 25, "posicion": "Extremo", "equipo": "Real Madrid", "seleccion": "Brasil"},
    {"id": 9, "nombre": "Julian Alvarez", "edad": 26, "posicion": "Delantero", "equipo": "Manchester City", "seleccion": "Argentina"},
    {"id": 10, "nombre": "Christian Cueva", "edad": 33, "posicion": "Mediocampista", "equipo": "Cienciano", "seleccion": "Peru"},
]

# Cuando un usuario entre a la ruta "/"
# Quiero que retorne un Hola mundo desde Flask
@app.route("/")
def inicio():
   return "Hola mundo desde Flask"

# Cuando un usuario entre a la ruta "/productos"
# Quiero que retorne un Hola se acabaron los productos
@app.route("/productos")
def productos():
   print("Cargando productos")
   return "Hola se acabaron los productos"

# Cuando ingrese a la ruta  "/jugadores/5"
@app.route("/jugadores/<int:id>")
def obtener_jugador(id):
   return { "jugador_id": id, "nombre": "David" }

# Necesitamos una ruta "/buscar?apellido=Guerrero"
@app.route("/buscar")
def buscar_jugador():
   # Request => Solicitud
   # from flask import request
   apellido = request.args.get('apellido')
   return {"apellido_jugador": apellido}

# Crea un endpoint "/jugador/4"
# Cuando un usuario ingrese a este endpoint debe
# de devolverse al jugador con el id en mencion
@app.route("/jugador/<int:id>")
def obtener_jugador_especifico(id):
   for jugador in jugadores:
      if jugador["id"] == id:
         return jugador
      
   return {"error": "Jugador no encontrado"}

@app.route("/seleccion/<pais>")
def obtener_jugadores_pais(pais):
   resultados = []
   for jugador in jugadores:
      if jugador["seleccion"] == pais:
         resultados.append(jugador)
   return resultados

app.run()