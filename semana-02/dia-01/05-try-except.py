# # JAVASCRIPT => try - catch - finally
# # PYTHON => try  -  except - finally

# # El try se puede entender como INTENTA ejecutar lo siguiente
# try:
#    numero = int(input("Ingresa un número: "))
# except TypeError:
#    print("Numero invalido")

# # Conectate a tu bd y actualiza lo siguientes valores
# #try:
#    # db.conection()
#    # usuariosTable.update(id=1, idTo=2)
#    # return "Operacion exitosa , UPDATE HECHO"
# #except:
#    # print("Internal server error")
# #finally:
#    # db.close()


def pedir_entero(mensaje):
   # pedir un valor con input()
   # intentar convertirlo a int
   # si falla, mostrar "Eso no es un número"
   # si funciona, devolver el número
   try:
      numero = int(input(mensaje))
      return numero
   except:
      print("Eso no es un numero")


edad = pedir_entero("¿Cuántos años tenés? ")
print(f"Tenés {edad} años")