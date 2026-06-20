# Las Listas => Arrays

compras_semana = ["tomate", "cebolla", "aji", "zanahoria"]

datos_generales = [1, "mundo", 50.65, False]

paises_eliminados = []

lista_de_lista = [ [1,2,3,4,5], [6,7,8,9,10] ]


print(compras_semana[1])

print(datos_generales[2])

print(compras_semana[-4])

print(lista_de_lista[0][3])

print(compras_semana[1:])

print(compras_semana[:3])

lenguajes_programacion = ["Py", "Js", "Go", "Ruby", "Php"]

# Se solicita que se acceda al elemento Go y se modifique (reasinge)
# por Java

lenguajes_programacion[2] = "Java"

print(lenguajes_programacion)

equipos_mundial_a = ["USA", "Brasil", "Rusia", "Canada"]

equipos_mundial_b = ["Argentina", "Francia", "Uruguay", "Peru"]

nuevos_equipos = equipos_mundial_a + equipos_mundial_b

print(nuevos_equipos)

print(f"En el grupo A hay {len(equipos_mundial_a)}")
print(f"En el grupo unido hay {len(nuevos_equipos)}")

lista_de_lista = [ [1,2,3,4,5], [6,7,8,9,10] , [11,12,13,14]]

print(len(lista_de_lista[0]))