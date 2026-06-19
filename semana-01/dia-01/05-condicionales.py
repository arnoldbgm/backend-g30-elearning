# # Sentencias Condicionales - Estructuras de Control

# # if CONDICION

# edad = 15

# if edad >= 18:
#    print("Eres mayor de edad")
# else:
#    print("Eres menor de edad")

# # Operadores logicos
# ## Comparacion ==
# ## Mayor       >
# ## Menor       <
# ## Mayor o igual   >=
# ## Menor o igual  <=
# ## Diferente   != 


# # Ejemplo de Condicionales
# # Me contacta el BCP, que desea un login para su aplicacion en
# # terminal, el cual para ingresar al sistema, debe de colocar
# # sus credenciales
# # El usuario aceptado  =>   admin
# # La contraseaña aceptada =>   123456

# """
#    Este es un comentario
#    el cual se muestra en multiples lineas
# """

# '''
#    Este es otro comentario
#    el cual esta en multi linea
# '''


# usuario = input("¿Cual es tu usuario? ")
# contrasena = input("¿Cual es tu contraseña? ")

# if usuario == "admin" and contrasena == "123456":
#    print("Ingreso al sistema, exitoso")

# else:
#    print("Ingrso fallido, intente nuevamente")

# print("""
#    1. Sumar
#    2. Restar
#    3. Multiplicar
#    4. Dividir
# """)

# opcion = int(input("Cual es tu opcion: "))
# num1 = float(input("Ingresa tu primer numero"))
# num2 = float(input("Ingresa tu segundo numero"))




# if opcion == 1:
#    suma = num1 + num2
#    print(f"La suma es {suma}")

# elif opcion == 2:
#    resta = num1 - num2
#    print(f"La resta es {resta}")

# elif opcion == 3:
#    multiplicar = num1 * num2
#    print(f"La multiplicacion es {multiplicar}")

# elif opcion == 4:
#    if num2 == 0:
#       print("No se puede dividir entre cero")
#    else:
#       division = num1 / num2
#       print(f"La division es {division}")

# else:
#    print("Vuelve a escoger una opcion")

edad = "16"

if type(edad) is int:
   print("La edad es un entero")

else:
   print("La edad NO es un entero")