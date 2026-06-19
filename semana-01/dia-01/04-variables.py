nombre:str = "Arnold"
ciudad:str = "Arequipa"
edad:int = 29

# Se puede crear usando
# camelCase
# snake_case
# 🔴 IMPORTANTE: No se puede crear
# Variables con QuebackCase ☢️ nombre-alumno

# nombreAlumno = "Guillermo"
# apellido_alumno = "Garcia"
# edad_alumno = 33
# mayor_de_edad = True

# # Se necesita que se muestre en pantalla
# # El nombre es alumno, apellido la edad es XX

# # print("El nombre es" + nombreAlumno + "su edad es " + str(edad_alumno))

# print(f"El nombre es {nombreAlumno} su edad es {edad_alumno}")

# Input permite que el usuario pueda introducir informacion mediante la consola
nombre = input("Ingresar nombre: ")
edad = int(input("ingrese su edad: "))
ciudad = input("ingrese su ciudad: ")
lenguaje = input("¿Cuál es su lenguaje preferido?")

print(f"Hola soy {nombre}, tengo {edad} años, vivo en {ciudad} y programo en {lenguaje}")
print(f"Tipo de nombre: {type(nombre)}")
print(f"Tipo de edad: {type(edad)}")
print(f"Tipo de ciudad: {type(ciudad)}")
print(f"Tipo de lenguaje: {type(lenguaje)}")

anioNacimiento = 2026 - edad
# 2026 - 29 
# 1997