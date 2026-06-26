def holaMundo():
   # pass # Significa que aqui vendra un bloque de codigo
   print("Hola mundo!")

holaMundo()


def saludar(jugador, equipo, goles):
   print(f"El jugador {jugador} del equipo {equipo} tiene {goles} goles")

saludar(goles=120, jugador='Lionel Messi', equipo='PSG')

def cuadrado(numero):
   return numero * numero


print(cuadrado(cuadrado(5)))


def mostrar_numeros(numeros):
   print(numeros)
   for numero in numeros:
      print(numero)

mostrar_numeros([1, 2, 3])

