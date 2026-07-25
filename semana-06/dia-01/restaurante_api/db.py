# Aqui vamos a podreceder a crear SQLAlchemy
# Porque vamos a reusar constantemente este archivo
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Ahora que ya tenemos SQLAlchemy empaquetada en una sola variable
# Vamos a pasar a llamar esta variable dentro de nuestro archivo
# app.py para que pueda correr SQLAlchemy