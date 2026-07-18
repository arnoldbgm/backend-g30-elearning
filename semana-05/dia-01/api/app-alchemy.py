from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy # Traigo SQL Alchmemy

app = Flask(__name__)

# Configuraciones de tu servidor       dialect://username:password@host:port/database
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:root@localhost:5432/canciones"

db = SQLAlchemy(app) # Integro SQLAlchmey en mi servidor

# Definir Modelos - Tablas
class Artistas(db.Model): # Esta clase va a ser una Tabla 
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    genero = db.Column(db.String(50), nullable=False)
    pais_origen = db.Column(db.String(50), default="Perú")
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    # SQLAlchemy => AritsaModel
    __tablename__ = "artistas"

    def to_dic(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "genero": self.genero,
            "pais_origen": self.pais_origen,
            "activo": self.activo
        }

class Canciones(db.Model): # db.Model => Esta clase es una tabla
    # db.Column( TIPO DEL DATO, REGLAS)
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(150))
    duracion_segundos = db.Column(db.Integer)
    anio_lanzamiento = db.Column(db.Integer)
    artista_id = db.Column(db.Integer, db.ForeignKey("artistas.id"), nullable=False)
    __tablename__ = "canciones"


# Se solicita un endpoint, para poder obtener todos los artistas => /artistas
# Este endpoint tiene que ser del tipo GET
@app.route("/artistas", methods=["GET"])
def get_artistas():
    # Hacer la consulta
    artistas = Artistas.query.all() 
    print(artistas)
    print(artistas[0].nombre)
    # [Artistas, Artistas2, Artistas3, Artistas4]
    resultado_formateado = []
    for elmt in artistas:
        # formato = {
        #     "id": elmt.id,
        #     "nombre": elmt.nombre,
        #     "genero": elmt.genero,
        #     "pais_origen": elmt.pais_origen
        # }
        resultado_formateado.append(elmt.to_dic())

    # from flask import jsonify
    return jsonify(resultado_formateado)



# Definir Rutas - Endpoints

app.run(debug=True)