# 🧠 Guía — Día 1 (Semana 3): Entornos virtuales, pip y Flask

Bienvenidos AL BACKEND. Sí, hoy dejamos de ser usuarios de Python y nos convertimos en desarrolladores que exponen servicios. Vamos a crear nuestro propio servidor, nuestra propia API, y la vamos a probar como Dios manda con **Postman**. Prepárense que esto cambia el juego.

---

## 1. Entornos virtuales — la cajita mágica

Imaginate que tenés dos proyectos: uno usa Flask versión 2, el otro Flask versión 3. Sin entornos virtuales, es un caos — una cosa le gana a la otra, se te rompe todo y terminás formateando la compu (me pasó, y no está bueno).

Un entorno virtual es como una **caja aislada** para cada proyecto. Cada uno tiene su propio Flask, sus propias versiones, y no se pelean entre sí.

**Sin entorno virtual**: instalás Flask para el proyecto A, después el proyecto B necesita otra versión → conflicto, explosión, lágrimas.

**Con entorno virtual**: cada proyecto tiene su cajita. Una no toca a la otra. Paz mundial.

---

### 1A — Demo: Crear y activar un entorno virtual

1. Abrí una terminal en la carpeta de tu proyecto
2. Ejecutá:

```bash
python -m venv venv
```

Esto crea una carpeta `venv/` con una copia aislada de Python.

3. Activá el entorno:

```bash
# Windows
venv\Scripts\activate
```

Vas a ver que aparece `(venv)` al inicio de la línea. Eso significa que estás dentro del entorno virtual.

Para desactivarlo:

```bash
deactivate
```

Cuando está activo, todo `pip install` va a parar **dentro de esta caja**, no al sistema.

---

### 1B — Reto: Verificá que funciona

1. Creá un entorno virtual llamado `mundo-python`
2. Activarlo
3. Ejecutá `python --version` y `pip --version` para confirmar
4. Desactivarlo
5. Volvé a ejecutar `python --version` (sin el entorno activado) — todo sigue igual, el entorno no afecta al sistema

<details>
<summary><b>Solución (reto)</b></summary>

```bash
python -m venv mundo-python
mundo-python\Scripts\activate
python --version
pip --version
deactivate
python --version
```

</details>

---

## 2. pip — el dealer de paquetes

`pip` es el programa que usamos para instalar librerías externas. ¿Querés Flask? `pip install flask`. ¿Querés pandas? `pip install pandas`. ¿Querés hacer una API y que funcione? `pip install` todo lo que necesités.

Flask NO viene con Python. Nadie nace sabiendo, hay que instalarlo. Y para eso está pip.

### Comandos esenciales

| Comando | Qué hace |
|---------|----------|
| `pip install colorama` | Instala el paquete Colorama |
| `pip list` | Muestra los paquetes instalados |
| `pip freeze` | Lista los paquetes en formato `paquete==version` |
| `pip uninstall colorama` | Desinstala Colorama |

---

### 2A — Demo: Instalar Colorama y ver magia en la terminal

Primero lo primero: instalemos algo **que se vea**. Nada de instalar una librería y no pasar nada — con Colorama ves colores al toque.

Con el entorno virtual activado:

```bash
pip install colorama
```

Después ejecutá:

```bash
python
```

Y dentro de Python:

```python
from colorama import init, Fore
init()
print(Fore.RED + "ROJO" + Fore.RESET)
print(Fore.GREEN + "VERDE" + Fore.RESET)
print(Fore.BLUE + "AZUL" + Fore.RESET)
print(Fore.YELLOW + "AMARILLO" + Fore.RESET)
```

Salí con `exit()`. **Colorama en acción.** La terminal se viste de gala.

Ahora guardá la lista de dependencias:

```bash
pip freeze > requirements.txt
```

Esto crea un archivo que después cualquier otro puede usar para instalar exactamente las mismas versiones:

```bash
pip install -r requirements.txt
```

---

### 2B — Reto: Tu propio cartel luminoso

1. Con el entorno activado, asegurate de tener Colorama instalado
2. Escribí un archivo `cartel.py` que muestre un mensaje como este usando colores:

```
=== BIENVENIDO AL MUNDIAL 2026 ===
```

- El borde y el texto deben ser de distintos colores
- Usá `Fore.CYAN`, `Fore.MAGENTA`, `Fore.GREEN`, etc.
- Probalo varias veces cambiando colores

<details>
<summary><b>Solución (reto)</b></summary>

```python
from colorama import init, Fore

init()

print(Fore.CYAN + "=" * 35 + Fore.RESET)
print(Fore.YELLOW + "   BIENVENIDO AL MUNDIAL 2026" + Fore.RESET)
print(Fore.CYAN + "=" * 35 + Fore.RESET)
```

**Probá también:**
```python
print(Fore.MAGENTA + "Perú" + Fore.GREEN + " campeón" + Fore.RESET)
```

</details>

---

## 3. Flask — tu primer servidor (y te juro que no es brujería)

Flask es un **microframework**. ¿Qué significa "micro"? Que te da lo mínimo para construir un servidor web sin imponerte cómo ordenar tu código. No trae ORM, no trae autenticación, no trae un montón de cosas que no necesitás hoy. Cuando las necesites, las agregás.

Pero lo importante: **con 4 líneas de código ya tenés un servidor funcionando**. ¿A que no sabías que era tan fácil?

### 3A — Demo: Hola Mundo en Flask

Creá un archivo `app.py`:

```python
from flask import Flask

app = Flask(__name__)


@app.route("/")
def inicio():
    return "Hola, mundo Flask!"
```

Ahora ejecutalo:

```bash
python app.py
```

Abrí el navegador en `http://127.0.0.1:5000`. Vas a ver "Hola, mundo Flask!" en la pantalla. **Ya tenés un servidor web, loco. FELICITACIONES.**

**Lo que pasó (prestá atención porque esto es la BASE de todo):**
- `from flask import Flask` → importamos la clase principal de Flask
- `app = Flask(__name__)` → creamos una instancia de la aplicación
- `@app.route("/")` → esto es un **decorador**. Le decís a Flask: "Cuando alguien visite la raíz, ejecutá esta función"
- `def inicio()` → la función que se ejecuta. Tiene que devolver algo (un string, un JSON, un HTML)
- cuando ejecutás `app.py`, Flask inicia un servidor en `http://127.0.0.1:5000`

---

### 3B — Reto: Personalizá tu servidor

1. Creá un entorno virtual nuevo llamado `flask-crud`
2. Activarlo
3. Instalar Flask
4. Crear `app.py` con tu propio servidor que tenga:
   - Una ruta `/` que muestre "Bienvenido a la API de Jugadores del Mundial 2026"
   - Una ruta `/info` que devuelva `{"version": "1.0", "curso": "Backend con Flask"}`
   - **Probalo en Postman**: creá un GET a `http://127.0.0.1:5000/` y otro a `http://127.0.0.1:5000/info`

<details>
<summary><b>Solución (reto)</b></summary>

```bash
python -m venv flask-crud
flask-crud\Scripts\activate
pip install flask
```

```python
from flask import Flask

app = Flask(__name__)


@app.route("/")
def inicio():
    return "Bienvenido a la API de Jugadores del Mundial 2026"


@app.route("/info")
def info():
    return {"version": "1.0", "curso": "Backend con Flask"}
```

```bash
python app.py
```

En Postman:
- `GET http://127.0.0.1:5000/` → debe responder el string de bienvenida
- `GET http://127.0.0.1:5000/info` → debe responder el JSON

> **Nota:** Flask convierte automáticamente los diccionarios a JSON cuando los devolvés en una ruta.

</details>

---

## 4. Rutas dinámicas — cuando una URL vale más que mil palabras

Una API de verdad no tiene rutas fijas como `/jugador1`, `/jugador2`, `/jugador3`. Eso es una locura. Necesitás rutas que **cambien según lo que el cliente pida**. Algo como `/jugador/7` y que te devuelva al jugador con ID 7. Eso es una ruta dinámica, y es hermoso.

### Parámetros de ruta (`<tipo:nombre>`)

```python
@app.route("/jugador/<int:id>")
def obtener_jugador(id):
    return {"jugador_id": id, "nombre": "Ejemplo"}
```

### Parámetros de query (`request.args`)

```python
@app.route("/buscar")
def buscar():
    nombre = request.args.get("nombre")
    return {"buscaste": nombre}
```

Esto responde a: `GET /buscar?nombre=Paolo`

---

### 4A — Demo: Endpoint con jugadores hardcodeados

Fijate bien la estructura: **una lista de diccionarios**. Cada jugador tiene su propio `id` adentro, como debe ser.

```python
from flask import Flask, request

app = Flask(__name__)

jugadores = [
    {"id": 1, "nombre": "Paolo Guerrero", "edad": 41, "posicion": "Delantero", "equipo": "Alianza Lima", "seleccion": "Perú"},
    {"id": 2, "nombre": "André Carrillo", "edad": 33, "posicion": "Extremo", "equipo": "Al Hilal", "seleccion": "Perú"},
    {"id": 3, "nombre": "Renato Tapia", "edad": 29, "posicion": "Mediocampista", "equipo": "Leganés", "seleccion": "Perú"},
    {"id": 4, "nombre": "Lionel Messi", "edad": 38, "posicion": "Delantero", "equipo": "Inter Miami", "seleccion": "Argentina"},
    {"id": 5, "nombre": "Vinícius Jr", "edad": 25, "posicion": "Extremo", "equipo": "Real Madrid", "seleccion": "Brasil"},
]


@app.route("/")
def inicio():
    return "API de Jugadores del Mundial 2026"


@app.route("/jugador/<int:id>")
def obtener_jugador(id):
    for j in jugadores:
        if j["id"] == id:
            return j
    return {"error": "Jugador no encontrado"}, 404


@app.route("/jugadores")
def listar_jugadores():
    return jugadores
```

**Probalo en Postman:**
- `GET /` → bienvenida
- `GET /jugador/1` → datos de Paolo Guerrero
- `GET /jugador/99` → error 404
- `GET /jugadores` → lista de todos

---

### 4B — Reto: Endpoints de selecciones

Agregale al mismo `app.py`:

1. Una ruta `/seleccion/<nombre>` que devuelva todos los jugadores de esa selección. Ej: `GET /seleccion/Argentina` → solo Messi
2. Una ruta `/buscar` que acepte query params:
   - `?posicion=Delantero` → filtre por posición
   - `?edad_max=30` → jugadores menores o iguales a esa edad
   - **Combinables**: `?posicion=Delantero&edad_max=30`
3. Si no hay resultados, devolvé `{"mensaje": "No se encontraron jugadores"}` con código 200

> **Pista:** para `/seleccion/<nombre>`, el nombre llega como string, comparalo con `.title()` o `.lower()` según corresponda. Para `/buscar`, usá `request.args.get()` y verificate si cada filtro está presente.

<details>
<summary><b>Solución (reto)</b></summary>

```python
from flask import Flask, request

app = Flask(__name__)

jugadores = [
    {"id": 1, "nombre": "Paolo Guerrero", "edad": 41, "posicion": "Delantero", "equipo": "Alianza Lima", "seleccion": "Perú"},
    {"id": 2, "nombre": "André Carrillo", "edad": 33, "posicion": "Extremo", "equipo": "Al Hilal", "seleccion": "Perú"},
    {"id": 3, "nombre": "Renato Tapia", "edad": 29, "posicion": "Mediocampista", "equipo": "Leganés", "seleccion": "Perú"},
    {"id": 4, "nombre": "Lionel Messi", "edad": 38, "posicion": "Delantero", "equipo": "Inter Miami", "seleccion": "Argentina"},
    {"id": 5, "nombre": "Vinícius Jr", "edad": 25, "posicion": "Extremo", "equipo": "Real Madrid", "seleccion": "Brasil"},
]


@app.route("/")
def inicio():
    return "API de Jugadores del Mundial 2026"


@app.route("/jugador/<int:id>")
def obtener_jugador(id):
    for j in jugadores:
        if j["id"] == id:
            return j
    return {"error": "Jugador no encontrado"}, 404


@app.route("/jugadores")
def listar_jugadores():
    return jugadores


@app.route("/seleccion/<nombre>")
def jugadores_por_seleccion(nombre):
    resultado = []
    for j in jugadores:
        if j["seleccion"].lower() == nombre.lower():
            resultado.append(j)

    if not resultado:
        return {"mensaje": "No se encontraron jugadores"}, 200
    return resultado


@app.route("/buscar")
def buscar_jugadores():
    resultado = jugadores.copy()

    posicion = request.args.get("posicion")
    if posicion:
        filtrados = []
        for j in resultado:
            if j["posicion"].lower() == posicion.lower():
                filtrados.append(j)
        resultado = filtrados

    edad_max = request.args.get("edad_max")
    if edad_max:
        try:
            edad_max_val = int(edad_max)
            filtrados = []
            for j in resultado:
                if j["edad"] <= edad_max_val:
                    filtrados.append(j)
            resultado = filtrados
        except ValueError:
            return {"error": "edad_max debe ser un número"}, 400

    if not resultado:
        return {"mensaje": "No se encontraron jugadores"}, 200

    return resultado
```

**Probalo en Postman:**
- `GET /seleccion/Peru` → 3 jugadores
- `GET /seleccion/brasil` → Vinícius Jr
- `GET /buscar?posicion=Delantero` → Guerrero y Messi
- `GET /buscar?edad_max=30` → Tapia, Vinícius Jr
- `GET /buscar?posicion=Delantero&edad_max=35` → solo Messi
- `GET /buscar?posicion=Arquero` → "No se encontraron jugadores"

</details>

---

## 5. Mandar datos desde Postman — ya no es solo leer, ahora escribimos

Hasta ahora solo hicimos GET: pedir datos. Pero una API de verdad necesita **crear** cosas. ¿Y cómo le mandás datos al servidor? Por el **body** de la petición.

Imaginate que vas a un restaurante: GET es el menú (leer los platos), POST es hacer el pedido (crear algo nuevo). El mozo necesita saber QUÉ querés, y eso va en el body.

### Tipos de body (el que manda es JSON)

| Tipo | Content-Type | Cómo se lee en Flask |
|------|-------------|----------------------|
| JSON | `application/json` | `request.json` → devuelve un diccionario |
| Formulario | `application/x-www-form-urlencoded` | `request.form` |
| Texto plano | `text/plain` | `request.data` |

Nosotros usamos **JSON**, porque es el estándar en APIs REST. Punto.

### Cómo configurar Postman para mandar JSON

1. Elegí método **POST**
2. En la pestaña **Body** → **raw** → **JSON**
3. Escribí el JSON lindo y enviá

---

### 5A — Demo: Endpoint POST que recibe JSON

```python
from flask import Flask, request

app = Flask(__name__)


@app.route("/saludar", methods=["POST"])
def saludar():
    datos = request.json
    nombre = datos.get("nombre", "invitado")
    return {"mensaje": f"Hola {nombre}, bienvenido a la API del Mundial"}
```

**En Postman:**
- Método: POST
- URL: `http://127.0.0.1:5000/saludar`
- Body → raw → JSON:
```json
{
    "nombre": "Carlos"
}
```

**Respuesta esperada:**
```json
{
    "mensaje": "Hola Carlos, bienvenido a la API del Mundial"
}
```

**Conceptos importantes:**
- `methods=["POST"]` → por defecto Flask solo acepta GET. Hay que decirle explícitamente qué métodos acepta
- `request.json` → Flask parsea automáticamente el JSON del body y lo convierte en un diccionario
- Si no se envió JSON, `request.json` es `None`

---

### 5B — Reto: Validar datos recibidos

Creá un endpoint `POST /jugador` que reciba JSON con los datos de un nuevo jugador y lo agregue a la lista `jugadores`. Validá:

- `nombre`: obligatorio, no vacío
- `posicion`: obligatorio
- `seleccion`: obligatorio
- Si falta algún campo obligatorio, devolvé `{"error": "Falta el campo: nombre"}` con código **400**
- Si todo está bien, asignale un ID nuevo (el máximo + 1) y devolvé el jugador creado con código **201**

> **Pista:** para sacar el máximo ID tenés que recorrer la lista con un `for`, guardar el más grande, y sumarle 1.

<details>
<summary><b>Solución (reto)</b></summary>

```python
from flask import Flask, request

app = Flask(__name__)

jugadores = [
    {"id": 1, "nombre": "Paolo Guerrero", "edad": 41, "posicion": "Delantero", "equipo": "Alianza Lima", "seleccion": "Perú"},
    {"id": 2, "nombre": "André Carrillo", "edad": 33, "posicion": "Extremo", "equipo": "Al Hilal", "seleccion": "Perú"},
    {"id": 3, "nombre": "Renato Tapia", "edad": 29, "posicion": "Mediocampista", "equipo": "Leganés", "seleccion": "Perú"},
    {"id": 4, "nombre": "Lionel Messi", "edad": 38, "posicion": "Delantero", "equipo": "Inter Miami", "seleccion": "Argentina"},
    {"id": 5, "nombre": "Vinícius Jr", "edad": 25, "posicion": "Extremo", "equipo": "Real Madrid", "seleccion": "Brasil"},
]


@app.route("/")
def inicio():
    return "API de Jugadores del Mundial 2026"


@app.route("/jugador/<int:id>")
def obtener_jugador(id):
    for j in jugadores:
        if j["id"] == id:
            return j
    return {"error": "Jugador no encontrado"}, 404


@app.route("/jugadores")
def listar_jugadores():
    return jugadores


@app.route("/jugador", methods=["POST"])
def crear_jugador():
    datos = request.json

    if not datos:
        return {"error": "Debes enviar datos en formato JSON"}, 400

    if "nombre" not in datos or not str(datos.get("nombre", "")).strip():
        return {"error": "Falta el campo: nombre"}, 400

    if "posicion" not in datos or not str(datos.get("posicion", "")).strip():
        return {"error": "Falta el campo: posicion"}, 400

    if "seleccion" not in datos or not str(datos.get("seleccion", "")).strip():
        return {"error": "Falta el campo: seleccion"}, 400

    nuevo_id = 0
    for j in jugadores:
        if j["id"] > nuevo_id:
            nuevo_id = j["id"]
    nuevo_id += 1

    nuevo_jugador = {
        "id": nuevo_id,
        "nombre": datos["nombre"],
        "edad": datos.get("edad", 0),
        "posicion": datos["posicion"],
        "equipo": datos.get("equipo", ""),
        "seleccion": datos["seleccion"],
    }

    jugadores.append(nuevo_jugador)

    return nuevo_jugador, 201
```

**En Postman:**
- `POST /jugador` con body:
```json
{
    "nombre": "Alisson Becker",
    "edad": 33,
    "posicion": "Arquero",
    "equipo": "Liverpool",
    "seleccion": "Brasil"
}
```
→ Debe responder con los datos del jugador creado y código **201**

- `POST /jugador` con body:
```json
{
    "nombre": "James Rodríguez",
    "posicion": "Mediocampista",
    "seleccion": "Colombia"
}
```
→ Debe funcionar (edad y equipo son opcionales, toman valor por defecto)

- `POST /jugador` con body:
```json
{
    "nombre": ""
}
```
→ Debe responder `{"error": "Falta el campo: nombre"}` con código **400**

</details>

---

## 6. Códigos de estado HTTP — el servidor también tiene emociones

Cuando tu servidor responde, no solo manda datos. También manda un **código de estado** que es como su carita: le dice al cliente si todo salió bien, si se equivocó, si no encontró algo, o si explotó todo.

Y esto es CLAVE: una API no es solo devolver datos, es devolverlos con el código correcto. Si no, el cliente no sabe qué pasó.

### Los códigos que más vas a usar (aprendételos, en serio):

| Código | Significado | Cuándo usarlo |
|--------|------------|---------------|
| **200** | OK | Todo bien, acá están tus datos |
| **201** | Created | Acabo de crear algo, tomá |
| **204** | No Content | Lo eliminé, no hay nada que devolver |
| **400** | Bad Request | Mandaste cualquier cosa, revisá |
| **404** | Not Found | Eso que buscás no existe, pe |
| **500** | Internal Server Error | Algo explotó del lado del servidor |

En Flask, devolvés el código como segundo valor en el `return`:

```python
return {"error": "No encontrado"}, 404
return nuevo_jugador, 201
```

Sí, es así de simple. El primer valor son los datos, el segundo es el código.

---

### 6A — Demo: Probá los códigos en Postman como un profesional

Con tu `app.py` corriendo (el del reto anterior), probá esto en Postman y mirá el código que devuelve cada uno:

1. `GET /jugador/99` → código **404** — no existe, obvio
2. `POST /jugador` sin body o con body vacío → código **400** — mandaste mal los datos
3. `POST /jugador` con JSON válido → código **201** — se creó con éxito
4. `GET /jugador/6` → código **200** — acá está el jugador que creaste

En Postman, el código de estado aparece arriba a la derecha, bien grande. No lo ignorés. Es tan importante como los datos.

---

### 6B — Reto: Mejorá los códigos de estado

Tomá el `app.py` del reto 5B y asegurate de que **todas** las rutas devuelvan el código de estado correcto:

| Ruta | Caso | Código |
|------|------|--------|
| `GET /jugador/<id>` | Existe | 200 |
| `GET /jugador/<id>` | No existe | 404 |
| `GET /jugadores` | Siempre | 200 |
| `POST /jugador` | Datos válidos | 201 |
| `POST /jugador` | Faltan campos | 400 |
| `GET /seleccion/<nombre>` | Existe | 200 |
| `GET /seleccion/<nombre>` | No existe | 200 (con mensaje) |
| `GET /buscar` | Sin resultados | 200 (con mensaje) |

<details>
<summary><b>Solución (reto)</b></summary>

Revisá el código del reto 5B — ya tiene los códigos correctos. Verificá con Postman cada caso listado arriba y confirmá que el código que devuelve coincida.

Si algún endpoint no devuelve el código esperado, ajustalo.

</details>

---

## 🎯 Resumen de conceptos

| Tema | Demo | Reto | Conceptos clave |
|------|:----:|:----:|-----------------|
| 1. Entorno virtual | ✅ | ✅ | `venv`, activación, aislamiento |
| 2. pip y dependencias | ✅ | ✅ | `pip install`, `freeze`, `requirements.txt` |
| 3. Flask Hello World | ✅ | ✅ | `Flask`, `@app.route()`, servidor |
| 4. Rutas dinámicas | ✅ | ✅ | `<int:id>`, `request.args`, query params |
| 5. POST y request.json | ✅ | ✅ | `methods=["POST"]`, validación, código 201 |
| 6. Códigos HTTP | ✅ | ✅ | 200, 201, 400, 404 |
