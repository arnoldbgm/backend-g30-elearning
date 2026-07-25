from flask_restful import Resource
# Esta clase para que pueda tener todo el poder
# de la API de FlaskRestfull debe de heredar
# el Resource => este viene de flask_restful
class ClientesResource(Resource):
   def get(self):
      return {
         "msg": "Hola entraste al GET"
      }
   def post(self):
      return {
         "msg": "Hola desde el metodo POST"
      }