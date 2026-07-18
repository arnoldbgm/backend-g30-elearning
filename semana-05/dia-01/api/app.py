from flask import Flask, jsonify, request
import psycopg2 # Este es mi motor
from datetime import datetime

app = Flask(__name__) # La creacion de mi servidor de Flask

# Vamos a crear una funcion para poder conectarnos a la BD
# Informacion o datos para conectarnos a cualqueir BD
#   host     => Es el lugar donde esta alojado tu BD
#   database => Es el nombre de tu BD
#   user     => Es el usuario de tu BD
#   password => Es la contraseña de tu bd
#   port     => Es el puerto donde esta corriendo tu BD
#   host => localhost - 157.15.65.68 - pichangitas.com - aws.neon.com
#   database => canciones
#   user => postgres - neonuser
#   password => root - XasWerasrt985
#   port => 5432
def get_db_conection():
    conexion = psycopg2.connect(host='localhost',
                     database='canciones',
                     user='postgres',
                     password='root',
                     port='5432')
    return conexion

# Necesitamos que se devuelva todos los artistas
# Se solicita que se cree el endpoint => /artistas
# Del tipo GET
@app.route("/artistas", methods=["GET"]) #Debajo siempre va una funcion
def get_artistas():
    # Conectarnos a nuestra bd
    conn = get_db_conection() # Me conecto y guardo la conexion
    # Cursores => Vamos a poder ejecutar codigo SQL
    cur = conn.cursor()
    # Vamos a ejecutar una sentencia SQL para poder trear todo los artistitas
    # SELECT * FROM artistas;
    cur.execute("SELECT * FROM artistas")
    filas = cur.fetchall() # Capturar toda la informacion de SQL
    # La respuesta de la BD la tenemos guarda en la variable filas

    # Vamos a cerar el cursor y la conexion
    cur.close()
    conn.close()

    # [(1, 'Grupo 5', 'Cumbia', 'Perú', True, datetime.datetime(2026, 7, 16, 20, 3, 38, 934681)),
    #  (2, 'Agua Marina', 'Cumbia', 'Perú', True, datetime.datetime(2026, 7, 16, 20, 3, 38, 934681)), 
    # (3, 'Armonía 10', 'Cumbia', 'Perú', True, datetime.datetime(2026, 7, 16, 20, 3, 38, 934681))]

    # id, nombre, genero, pais_origen, activo

    # {id: 1, nombre: 'Grupo 5'}
    resultado_transformado = []
    for elmt in filas:
        formato = {
            "id": elmt[0],
            "nombre": elmt[1],
            "genero": elmt[2],
            "pais_origen": elmt[3],
            "activo": elmt[4]
        }
        resultado_transformado.append(formato)

    # SIEMPRE debe retornar una respuesta
    # Las respuetas de nuestras apis, deben estar en JSON
    return jsonify(resultado_transformado)


# Necesitamos que se devuelva todos los canciones
# Se solicita que se cree el endpoint => /canciones
# Del tipo GET

@app.route("/canciones", methods=["GET"])
def get_canciones():
    # Conectarnos a nuestra bd
    conn = get_db_conection() # Me conecto y guardo la conexion
    # Cursores => Vamos a poder ejecutar codigo SQL
    cur = conn.cursor()
    # Aqui recien viene nuestro codigo sql
    cur.execute("SELECT * FROM canciones")
    filas = cur.fetchall()
    # [(1, 'La Cumbia de las Aventuras', 'Grupo 5', 210, 2005, 1), 
    # (2, 'Nadie como Tú', 'Cumbia Total', 195, 2008, 1), 
    # (3, 'Loca', 'Loca', 200, 2010, 1)]

    # Vamos a cerar el cursor y la conexion
    cur.close()
    conn.close()

    resultado_formateado = []
    for elmt in filas:
        formato = {
            "id": elmt[0],
            "titulo": elmt[1],
            "albun": elmt[2],
            "duracion": elmt[3],
            "anio": elmt[4],
            "artista_id": elmt[5]
        }
        resultado_formateado.append(formato)

    return jsonify(resultado_formateado)

# Necesitamos que se devuelva a solo un artista
# Se solicita que se cree el endpoint => /artistas/<id>
# Del tipo GET

@app.route("/artistas/<int:id>", methods=["GET"])
def get_single_artista(id):
    conn = get_db_conection()
    cur = conn.cursor()
    # Aqui viene mi codigo SQL
    # ❌ cur.execute(f"SELECT * FROM artistas WHERE id = {id}")
    cur.execute("SELECT * FROM artistas WHERE id = %s", (id,))
    fila = cur.fetchone()

    cur.close()
    conn.close()

    if fila is None:
        return {
            "msg": "Artista no encontrado"
        }, 404 # 404 No encontrado

    print(fila)
    # (8, 'Zambo Cabero', 'Criolla', 'Perú', True, datetime.datetime(2026, 7, 16, 20, 3, 38, 934681))
    return {
        "id": fila[0],
        "nombre": fila[1],
        "genero": fila[2],
        "pais_origen": fila[3],
        "activo": fila[4]
    }

# Necesitamos que se devuelva a solo un cancion
# Se solicita que se cree el endpoint => /canciones/<id>
# Del tipo GET
@app.route("/canciones/<int:id>", methods=["GET"])
def get_single_cancion (id):
    conn = get_db_conection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM canciones WHERE id = %s", (id,))
    fila = cur.fetchone()
    # Vamos validar en caso de que no encontremos el registro
    if fila is None:
        return {
            "msg": "Cancion no encontrada"
        }, 404

    return {
        "id": fila[0],
        "titulo": fila[1],
        "album": fila[2],
        "duracion": fila[3],
        "anio_lanzamiento": fila[4],
        "artista_id": fila[5]
    }

# Necesitamos que se registre informacion en la artistas
# Se solicita que se cree el endpoint => /add-artistas
# Del tipo POST => Insertar informacion
@app.route("/add-artistas", methods=["POST"])
def add_artistas():
    # Vamos a capturar el JSON que nos envia el cliente (frontend)
    # {
    #  "nombre": "Rafaga",
    #  "genero": "Cumbia",
    #  "pais_origen": "Argentina",
    # }

    # Vamos a usar el request de Flask
    # from flask import Flask, request
    data = request.json

    # Al insertar data => Vamos aplicar multiples validaciones
    # El usuario no envia informacion => Json vacio
    if not data:
        return {
            "msg": "Debes de enviar informacion"
        }, 400

    if "nombre" not in data or len(data["nombre"].strip()) == 0:
        return {
            "msg": "Falta completar el campo nombre"
        }, 400

    if "genero" not in data or len(data["genero"].strip()) == 0:
        return {
            "msg": "Falta completar el campo genero"
        }, 400

    # Vamos a conectar a la bd y vamos a crear nuestro cursor
    conn = get_db_conection()
    cur = conn.cursor()

    #  data = {
    #  "nombre": "Rafaga",
    #  "genero": "Cumbia",
    #  "pais_origen": "Argentina",
    # }
    # Ejecucion de la sentencia SQL => INSERT - UPDATE Y DELETE
    cur.execute("""INSERT INTO artistas (nombre, genero, pais_origen)
                 VALUES (%s, %s, %s)""", 
                 (data["nombre"], data["genero"], data["pais_origen"]))
    
    conn.commit() # Estamos confirmando nuestra instruccion

    # Cerrar nuestras conexion y cursor
    cur.close()
    conn.close()

    # Vamos a retornar un mensaje al usuario
    return {
        "msg": "Creacion exitosa"
    }, 201


# Necesitamos que se registre informacion en la canciones
# Se solicita que se cree el endpoint => /add-canciones
# Del tipo POST => Insertar informacion
@app.route("/add-canciones", methods=["POST"])
def add_single_cancion():
    #Capturamos el JSON
    data = request.json

    #Validacion
    if not data:
        return{
            "msg": "Debes de enviar un JSON"
        }, 400

    # Validaremos que se envien todos los campos
    if "titulo" not in data or "album" not in data or "duracion_segundos" not in data or "anio_lanzamiento" not in data or "artista_id" not in data:
        return{
            "msg": "Los datos estan incompletos"
        }

    if data["duracion_segundos"] <= 0:
        return{
            "msg": "La duracion no puede ser negativa"
        }

    # from datetime import datetime
    if data["anio_lanzamiento"]<= 1600 or data["anio_lanzamiento"] > datetime.now().year:
        return {
            "msg": "El anio de lazanmiento no debe ser inferio a 1600 ni mayor al año actual"
        }

    # Controlar que el artista_id => Exista
    if data["artista_id"]:
        # Tendriamos que consultar a la bd si existe este registro
        conn = get_db_conection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM artistas WHERE id = %s", (data["artista_id"],))

        fila = cur.fetchone()

        conn.close()
        cur.close()

        if fila is None:
            return{
                "msg": "El artista no existe"
            }, 404
        

    conn = get_db_conection()
    cur = conn.cursor()

    cur.execute("""INSERT INTO canciones (titulo, album, duracion_segundos, anio_lanzamiento, artista_id)
                    VALUES (%s, %s, %s, %s, %s)""" ,
                    (data["titulo"], 
                     data["album"], 
                     data["duracion_segundos"], 
                     data["anio_lanzamiento"], 
                     data["artista_id"]))

    conn.commit() # Vamos a confirmar la insercion la bd

    conn.close()
    cur.close()

    return {
        "msg": "Cancion creada exitosamente"
    }, 201

# Encender - Hacer correr nuestro servidor
app.run(debug=True)