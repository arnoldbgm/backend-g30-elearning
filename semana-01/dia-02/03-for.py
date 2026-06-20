# Bucle
# Es una estructura que permite repetir instruciones varias veces
# Los objetos iterables => listas , diccionarios y tuplas

# frutas = ["manzana", "pera", "mandarina"]

# # for ALIAS_ELEMENTO in LISTA:

# for i in frutas:
#    # Viene el codigo que se va a ejecutar al recorrer cada elemento
#    print(i)

# numeros = [1, 5, 3, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]

# # Se solicita que primero ordene el Arreglo (ascendente)
# # Se solicita que imprima en pantalla solo los elementos mayores a 15

# numeros.sort()

# print(numeros) # [1, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]

# for element in numeros:
#    if element > 15:
#       print(element)

# notas = [14, 8, 17, 11, 6, 20, 13, 9]
# aprobados = 0
# alguien_saco_20 = False
# accumulador_notas = 0
# nota_mayor = notas[0]
# nota_menor = notas[0]
# # El promedio se calcula sumando todas las notas / cantidad de notas

# for notaAlumno in notas:
#    if notaAlumno >= 11:
#       aprobados = aprobados + 1
   
#    if notaAlumno == 20:
#       alguien_saco_20 = True

#    if notaAlumno >= nota_mayor:
#       nota_mayor = notaAlumno

#    if notaAlumno <= nota_menor:
#       nota_menor = notaAlumno

#    accumulador_notas = accumulador_notas + notaAlumno

# print(f"Mis alumnos aprobados son {aprobados}")
# print(f"¿Existe algun 20? {alguien_saco_20}")
# print(f"El promedio de notas es {accumulador_notas / len(notas)}")
# print(f"La nota menor es {nota_menor}")
# print(f"La nota mayor es {nota_mayor}")

# temperaturas = [22, 31, 28, 35, 18, 40, 27, 33, 15]
# conversion = []
# alta_temp=temperaturas[0]
# baja_temp=temperaturas[0]
# contar_30 = 0
# promedio = 0

# for temp in temperaturas:
#     conversion.append(temp * 9/5 + 32)
#     if alta_temp < temp:
#         alta_temp=temp
#     if baja_temp > temp:
#         baja_temp=temp
#     promedio=promedio+temp
#     if temp > 30:
#         contar_30 = contar_30 + 1

# print(f"La conversion de las temperaturas es: {conversion}")
# print(f"La mayor temperatura es {alta_temp}")
# print(f"La menor temperatura es {baja_temp}")
# print(f"La promedio de las {len(temperaturas)} temperatura es {promedio/len(temperaturas)}")
# print(f"El numero de temperaturas que superaron los 30 °C es {contar_30}")
# i=0
# for i in range(0, len(temperaturas), 1):
#     print(f"La temperatura {temperaturas[i]} es conversion {conversion[i]}")


# for t in temperaturas:
#     print(f"La temperatura {t} es conversion {conversion[i]}")
#     i=i+1

# cadena = "Hola, mundo!"
# for caracter in cadena:
#     print(caracter)

# # Contar cuantas veces se esta repitiendo la letra a
# frase = "¿Qué es la vida? Un frenesí. ¿Qué es la vida? Una ilusión, una sombra, una ficción; y el mayor bien es pequeño; que toda la vida es sueño, y los sueños, sueños son"

# frase_corta = "Que es La VidA. LA vida"
# accumulador = 0

# for letra in frase_corta:
#    if letra == "a" or letra == "A":
#       accumulador += 1

# print(f"Se repite la letra {accumulador} veces")

# # Para manipular str, convirtiendolos de mayuscula a minuscula

# # STR.lower() "La VIDA ES UN SUeño".lower()  => "la vida es un sueño"
# # STR.upper() "La VIDA ES UN SUeño".upper()  => "LA VIDA ES UN SUEÑO" 

# frutas = ["manzana", "pera", "mandarina"]

# for index, elemento in enumerate(frutas):
#    print(f"La fruta tal {elemento} esta en el indice {index}")


# animales = ["perro", "gato", "ratón", "loro", "pez"]
# mayusculas = [a.upper() for a in animales]

notas = [8, 9, 15 ,16 ,17 ,16 , 17]

notasAumentadas = [notas + 3 for nota in notas]

print(notasAumentadas)


