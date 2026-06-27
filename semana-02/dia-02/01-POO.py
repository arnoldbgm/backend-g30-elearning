# Programacion Orientada a Objetos

# ¿Que es un paradigma?
# Un paradigma es un patron , un modelo la forma en como actuar

# Es un paradigma donde el codigo se organiza bajo lo que son
# objetos y clases

# ¿Que es una clase?
# Es una plantilla o un molde, vamos abstraer
# todas las caracteriscticas que observemos de un elemento

# Las caracteristicas que tiene una clase => Atributos
# Los comportamientos o acciones          => Metodos

class Jugador:
   # nombre = 'Messi'
   # edad = 39
   # posicion = 'Delantero'
   # equipo = 'Argentina'
   def __init__(self, nombre, edad, posicion, equipo, mundiales_ganados = 0):
      self.nombre = nombre
      self.edad = edad
      self.posicion = posicion
      self.equipo = equipo
      self.mundiales_ganados = mundiales_ganados

   def mostrar_informacion(self):
      # Aqui definimos el comportamiento de este metodo
      print(f"El jugador {self.nombre} | {self.edad} años | {self.equipo}")

   def celebrar(self):
      print(f"Gol de {self.nombre}!!!!")

# Para poder materializar mi clase => Instanciar
messi = Jugador('Messi', 39, 'Delantero', 'Argentina')
mbappe = Jugador('Kylian Mbappe', 27, 'Delantero', 'Francia')
vinicius = Jugador('Vinicius Jr', 25, 'Delantero', 'Brasil')

class Equipo:
   def __init__(self, nombre, pais):
      self.nombre = nombre
      self.pais = pais
      self.jugadores = []

   def agregar_jugador(self, jug):
      self.jugadores.append(jug)
      print(f"El jugador {jug.nombre} {jug.edad} se unio EXITOSAMENTE")
   
   def mostrar_jugadores(self):
      for elmt in self.jugadores:
         print(f"Nombre {elmt.nombre} Edad {elmt.edad} Posicion {elmt.posicion}")

brasil = Equipo("Seleccion Brasileña", "Brasil")
brasil.agregar_jugador(vinicius)
brasil.mostrar_jugadores()

# Padre
class Animal:
   def __init__(self, nombre):
      self.nombre = nombre

# Hija
class Perro(Animal):
   def __init__(self, nombre, raza):
      super().__init__(nombre)
      self.raza = raza

# Hija -> Hija
class Cachoro(Perro):
   def __init__(self, nombre, apodo):
      self.nombre = nombre
      self.apodo = apodo

c = Cachoro("Tomas","Tomasito")

print(c.apodo)


def operaciones(a,b):
   suma = a + b
   resta = a - b
   multiplicacion = a * b
   division = a / b
   return suma, resta, multiplicacion, division

resultados = operaciones(4, 6)

print(resultados)


class Persona:
   def __init__(self, nombre, edad, dni):
      self.nombre = nombre
      self._edad = edad # Protegido
      self.__dni = dni  # Privado

   def mostrar_dni(self):
      print(self.__dni)

   def __str__(self):
      return f"{self.nombre} {self._edad} {self.__dni}"

juan = Persona("Juan", 34, 10036523)

print(juan)