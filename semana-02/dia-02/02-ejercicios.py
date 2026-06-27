import random

class Tragamonedas:
   def __init__(self, nombre, creditos):
      self.nombre = nombre
      self.creditos = creditos

   def mostrar(self):
      print(f"🎰 {self.nombre} — Créditos: S/ {self.creditos}")

   def girar(self):
      resultado = []
      simbolos = ["🍒", "🔔", "💎", "🍀", "⭐", "7️⃣"]
      # random.randint(1,9)
      for elmt in range(3):
         indice = random.randint(0, len(simbolos)-1)
         resultado.append(simbolos[indice])
      print(resultado)
      return resultado
   
   def jugar(self, apuesta):
      if apuesta > self.creditos:
         print(f"No tienes suficientes creditos")
         return
      
      self.creditos -= apuesta
      resultado = self.girar()  # ['🔔', '🔔', '🔔']

      if resultado[0] == resultado[1] == resultado[2]:
         premio = apuesta * 10
         print(f"Ganaste {premio}")
         self.creditos += premio

      elif resultado[0] == resultado[1] or resultado[1] == resultado[2] or resultado[0] == resultado[2]:
         premio = apuesta * 2
         print(f"Ganaste {premio}")
         self.creditos += premio

      else:
         print(f"Lo siento PERDISTE {apuesta}")

maquina = Tragamonedas("La suerte andante", 100)
maquina1 = Tragamonedas("La siete", 100)

maquina1.jugar(90)