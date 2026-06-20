materias = ["Matematica", "CTA", "PFRH", "Civica", "EEFF"]

# Necesitamos que se inserte la materia Comunicacion

materias.append("Comunicacion")

materia_adicional = "Computo"

materias.append(materia_adicional) # materias.append("Computo")

materias.insert(0, "Quimica")

materias.extend(['Fisica', 'Biologia', 'Anatomia'])
print(materias)

#['Quimica', 'Matematica', 'CTA', 'PFRH', 'Civica', 'EEFF', 'Comunicacion', 'Computo', 'Fisica', 'Biologia', 'Anatomia']

# Metodos para ELIMINAR ELEMENTOS

print("Elementos despues de la eliminacion")

materia_eliminar = "CTA" # El usuario escribe mal la materia

if materia_eliminar in materias:
   materias.remove(materia_eliminar)
else:
   print("No se pudo eliminar la materia")

materias.pop()  # Elimino Anatomia
materias.pop()  # Elimino Biologia
materias.pop(1)

print(materias)


precios_vuelos = [150, 200, 300, 25, 45, 900, 225, 545]

precios_vuelos.sort(reverse=True)

alumnos = ["Ana", "Juan", "Pedro", "Zeta", "Benji"]

alumnos.sort(reverse=True)

print(alumnos)

mascotas = ["Firulais", "Lobo", "Cocer", "Firulais", "Firulais"]

print(mascotas.count("Firulais"))

esta_lobo = "Lobo" in mascotas

print(esta_lobo)

print(mascotas.index("Firulais"))