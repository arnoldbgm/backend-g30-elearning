# 🧠 Guía — Día 2 (Semana 3): CRUD completo + Frontend

Bienvenidos al día en que TODO cobra sentido. Hoy no solo vamos a leer datos — vamos a **Crear, Leer, Actualizar y Eliminar** jugadores como si fuéramos dueños de la base de datos del Mundial. Y después... ¡conectamos todo con un frontend! HTML, JavaScript, fetch, la combinación letal. Todo validado con Postman, obvio.

---

## 1. CRUD — las 4 letras que mueven el mundo

CRUD no es una mala palabra, son las **4 operaciones básicas** de cualquier sistema que persista datos. Literalmente, el 90% de las APIs que existen hacen solo esto:

| Operación | Método HTTP | ¿Qué hace? |
|-----------|------------|------------|
| **C**reate | POST | Crear un recurso nuevo |
| **R**ead | GET | Obtener uno o varios recursos |
| **U**pdate | PUT / PATCH | Actualizar un recurso que ya existe |
| **D**elete | DELETE | Borrar un recurso |

Hoy implementamos las 4. Sin base de datos, sin vueltas — en memoria, paso a paso.

---

## 2. CRUD completo con lista en memoria

### 2A — Demo: GET y POST (lo tenemos del Día 1)

Arrancamos con el código que tenemos:

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

---

### 2B — Reto: Agregar PUT y DELETE

Agregale a ese `app.py` los endpoints faltantes:

1. **`PUT /jugador/<id>`** — Actualiza los datos de un jugador existente
   - Recibe JSON con los campos a actualizar
   - Solo actualiza los campos que vienen en el JSON (no reemplaza todo)
   - Si el jugador no existe, devolvé 404
   - Si no envía datos, devolvé 400
   - Devolvé el jugador actualizado con código 200

2. **`DELETE /jugador/<id>`** — Elimina un jugador
   - Si existe, lo elimina de la lista
   - Devolvé `{"mensaje": "Jugador eliminado"}` con código 200
   - Si no existe, devolvé 404

> **Pista:** para actualizar, primero encontrá al jugador con un `for`, después actualizá campo por campo. Para eliminar, encontrá al jugador, usá `jugadores.remove(j)` y cortá con `return`.

<details>
<summary><b>Solución (reto)</b></summary>

Agregá estos endpoints al `app.py`:

```python
@app.route("/jugador/<int:id>", methods=["PUT"])
def actualizar_jugador(id):
    for j in jugadores:
        if j["id"] == id:
            datos = request.json

            if not datos:
                return {"error": "Debes enviar datos en formato JSON"}, 400

            for campo in datos:
                if campo in j:
                    j[campo] = datos[campo]

            return j, 200

    return {"error": "Jugador no encontrado"}, 404


@app.route("/jugador/<int:id>", methods=["DELETE"])
def eliminar_jugador(id):
    for j in jugadores:
        if j["id"] == id:
            jugadores.remove(j)
            return {"mensaje": "Jugador eliminado"}, 200

    return {"error": "Jugador no encontrado"}, 404
```

**Probalo en Postman:**

| Método | URL | Body | Qué esperar |
|--------|-----|------|-------------|
| `PUT` | `/jugador/3` | `{"edad": 30, "equipo": "Celta de Vigo"}` | Renato Tapia actualizado, código 200 |
| `PUT` | `/jugador/99` | `{"edad": 25}` | Error 404 |
| `DELETE` | `/jugador/5` | - | "Jugador eliminado", código 200 |
| `GET` | `/jugadores` | - | Lista sin Vinícius Jr |
| `DELETE` | `/jugador/99` | - | Error 404 |

</details>

---

## 3. PUT vs PATCH — la confusión más común (y cómo evitarla)

Esta es una pregunta de entrevista de trabajo, te lo juro. Y la mayoría la pifia.

| Método | Qué hace | ¿Qué pasa con los campos que no mandaste? |
|--------|----------|-------------------------------------------|
| **PUT** | Reemplaza TODO el recurso | Se pierden. Adiós. Se fueron. |
| **PATCH** | Actualiza SOLO los campos que llegan | Los que no mandaste se quedan como están |

En nuestro código del reto anterior usamos `PUT` pero en realidad hicimos **PATCH** (porque actualizamos solo los campos que llegaban). Está bien para aprender, pero en una API de verdad, si hacés un PUT que se comporta como PATCH, un backend experimentado te va a mirar feo.

Honestamente: **usá PATCH**. Es más correcto y no perdés nada.

### 3A — Demo: PUT vs PATCH en acción

Con el servidor corriendo, hacé estas pruebas en Postman:

**Caso PUT puro (reemplazo total):**

Si el endpoint hiciera reemplazo total, un `PUT /jugador/1` con body:

```json
{
    "nombre": "Paolo Guerrero",
    "edad": 42
}
```

...borraría `posicion`, `equipo` y `seleccion`. No queremos eso.

**Caso PATCH (nuestra implementación):**

Nuestra versión actualiza solo lo que llega. Si enviás `{"edad": 42}`, los demás campos se mantienen.

Probá:
```
PUT /jugador/1
Body: {"edad": 42}
```
→ El jugador 1 ahora tiene edad 42, pero todo lo demás igual.

Después revertilo:
```
PUT /jugador/1
Body: {"edad": 41}
```

---

### 3B — Reto: Refactor con PATCH y validación extra

Mejorá tu API:

1. Cambiá la ruta de actualización para que use **`methods=["PATCH"]`** (más correcto semánticamente)
2. Validá que `edad` (si se envía) sea un número positivo y menor a 100
3. Validá que `posicion` (si se envía) no esté vacío
4. Si alguna validación falla, devolvé código **400** con el mensaje específico

<details>
<summary><b>Solución (reto)</b></summary>

```python
@app.route("/jugador/<int:id>", methods=["PATCH"])
def actualizar_jugador(id):
    for j in jugadores:
        if j["id"] == id:
            datos = request.json

            if not datos:
                return {"error": "Debes enviar datos en formato JSON"}, 400

            if "edad" in datos:
                try:
                    edad = int(datos["edad"])
                    if edad < 0 or edad > 100:
                        return {"error": "La edad debe estar entre 0 y 100"}, 400
                except (ValueError, TypeError):
                    return {"error": "La edad debe ser un número válido"}, 400

            if "posicion" in datos and not str(datos["posicion"]).strip():
                return {"error": "La posición no puede estar vacía"}, 400

            if "nombre" in datos and not str(datos["nombre"]).strip():
                return {"error": "El nombre no puede estar vacío"}, 400

            if "seleccion" in datos and not str(datos["seleccion"]).strip():
                return {"error": "La selección no puede estar vacía"}, 400

            for campo in datos:
                if campo in j:
                    j[campo] = datos[campo]

            return j, 200

    return {"error": "Jugador no encontrado"}, 404
```

**Probá en Postman:**

```
PATCH /jugador/1
Body: {"edad": 42}
```
→ 200, edad actualizada

```
PATCH /jugador/1
Body: {"edad": -5}
```
→ 400, "La edad debe estar entre 0 y 100"

```
PATCH /jugador/1
Body: {"posicion": ""}
```
→ 400, "La posición no puede estar vacía"

</details>

---

## 4. Frontend — ahora sí, algo que se ve bonito

Hasta ahora todo lo probamos con Postman. Y está bien, Postman es el amigo fiel del backend. Pero una API no vive para Postman — vive para que **otros programas** la consuman.

Hoy creamos un frontend en HTML plano que se conecta a nuestra API usando `fetch`. Nada de React, nada de Vue, nada de frameworks — HTML, JavaScript y ganas.

### El problema del CORS (y por qué existe)

Cuando tu frontend corre en `file://` o en un puerto distinto al del backend, el navegador se pone nervioso y dice "eh, esto es sospechoso" y **bloquea la petición**. No es malo, es seguridad. Pero nosotros tenemos que decirle: "tranqui, confiá".

### 4A — Demo: Servir el frontend DESDE Flask (sin vueltas)

La solución más limpia: que Flask sirva el HTML. Mismo origen, cero CORS, cero problemas.

Primero, instalá Flask-CORS por si acaso:

```bash
pip install flask-cors
```

Después, actualizá `app.py`:

```python
from flask import Flask, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite peticiones desde cualquier origen (por si acaso)


@app.route("/")
def servir_frontend():
    return send_from_directory(".", "index.html")
```

Ahora creá un archivo `index.html` en la **misma carpeta** que `app.py`:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Jugadores del Mundial 2026</title>
</head>
<body>
    <h1>Jugadores del Mundial 2026</h1>

    <button onclick="cargarJugadores()">Cargar Jugadores</button>

    <ul id="lista"></ul>

    <script>
        const API = "http://127.0.0.1:5000";

        async function cargarJugadores() {
            const respuesta = await fetch(`${API}/jugadores`);
            const jugadores = await respuesta.json();

            const lista = document.getElementById("lista");
            lista.innerHTML = "";

            jugadores.forEach(j => {
                const item = document.createElement("li");
                item.textContent = `${j.nombre} - ${j.posicion} - ${j.seleccion}`;
                lista.appendChild(item);
            });
        }
    </script>
</body>
</html>
```

Ahora andá a `http://127.0.0.1:5000/`. ¿Qué ves? **Tu frontend.** Servido por Flask. Mismo origen, cero configuraciones raras, cero dolores de cabeza.

---

### 4B — Reto: Mejorá el frontend

Agregale al `index.html`:

1. Un campo de texto para buscar por **nombre** (input + botón). Cuando escribas y des click, llamá a un endpoint de búsqueda... esperá, no tenemos endpoint de búsqueda por nombre. Agregá uno:

```
GET /buscar-por-nombre?q=Paolo
```

2. Mostrá los resultados en una tabla (no en lista) con columnas: Nombre, Edad, Posición, Equipo, Selección
3. Si no hay resultados, mostrá "No se encontraron jugadores"

<details>
<summary><b>Solución (reto)</b></summary>

**En `app.py`**, agregá:

```python
@app.route("/buscar-por-nombre")
def buscar_por_nombre():
    q = request.args.get("q", "").lower()
    resultado = []
    for j in jugadores:
        if q in j["nombre"].lower():
            resultado.append(j)

    if not resultado:
        return {"mensaje": "No se encontraron jugadores"}

    return resultado
```

**En `index.html`:**

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Jugadores del Mundial 2026</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        input, button { padding: 8px; margin-right: 5px; }
        table { border-collapse: collapse; width: 100%; margin-top: 10px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background: #1a3a5c; color: white; }
        .error { color: #999; font-style: italic; }
    </style>
</head>
<body>
    <h1>Jugadores del Mundial 2026</h1>

    <div>
        <input type="text" id="busqueda" placeholder="Buscar por nombre...">
        <button onclick="buscarJugador()">Buscar</button>
        <button onclick="cargarJugadores()">Ver todos</button>
    </div>

    <p id="mensaje"></p>
    <table>
        <thead>
            <tr>
                <th>Nombre</th>
                <th>Edad</th>
                <th>Posición</th>
                <th>Equipo</th>
                <th>Selección</th>
            </tr>
        </thead>
        <tbody id="tabla-jugadores"></tbody>
    </table>

    <script>
        const API = "http://127.0.0.1:5000";

        async function cargarJugadores() {
            const respuesta = await fetch(`${API}/jugadores`);
            const jugadores = await respuesta.json();
            mostrarJugadores(jugadores);
        }

        async function buscarJugador() {
            const q = document.getElementById("busqueda").value.trim();
            if (!q) {
                cargarJugadores();
                return;
            }

            const respuesta = await fetch(`${API}/buscar-por-nombre?q=${q}`);
            const datos = await respuesta.json();
            mostrarJugadores(datos);
        }

        function mostrarJugadores(datos) {
            const tbody = document.getElementById("tabla-jugadores");
            const mensaje = document.getElementById("mensaje");

            tbody.innerHTML = "";
            mensaje.textContent = "";

            if (datos.mensaje || datos.length === 0) {
                mensaje.textContent = datos.mensaje || "No se encontraron jugadores";
                mensaje.className = "error";
                return;
            }

            datos.forEach(j => {
                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td>${j.nombre}</td>
                    <td>${j.edad}</td>
                    <td>${j.posicion}</td>
                    <td>${j.equipo}</td>
                    <td>${j.seleccion}</td>
                `;
                tbody.appendChild(fila);
            });
        }

        cargarJugadores();
    </script>
</body>
</html>
```

**Probá:**
- La página carga automáticamente todos los jugadores
- Buscá "Paolo" → solo Guerrero
- Buscá "zzz" → "No se encontraron jugadores"
- Click en "Ver todos" → vuelve la lista completa

</details>

---

## 5. CRUD desde el navegador — el frontend completo

Ahora viene lo bueno. Ya tenemos la API que hace CRUD. Ya tenemos un frontend que muestra datos. Es hora de **unir todo** y crear, editar y eliminar jugadores directamente desde el navegador. Sin Postman, sin terminal — todo desde la interfaz.

### 5A — Demo: Agregar jugador desde el frontend

Agregá esto al `index.html`:

```html
<h2>Agregar jugador</h2>
<form id="form-crear">
    <input type="text" name="nombre" placeholder="Nombre" required>
    <input type="number" name="edad" placeholder="Edad">
    <input type="text" name="posicion" placeholder="Posición" required>
    <input type="text" name="equipo" placeholder="Equipo">
    <input type="text" name="seleccion" placeholder="Selección" required>
    <button type="submit">Agregar</button>
</form>
```

```javascript
document.getElementById("form-crear").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const datos = Object.fromEntries(formData.entries());

    const respuesta = await fetch(`${API}/jugador`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(datos),
    });

    if (respuesta.ok) {
        e.target.reset();
        cargarJugadores();
    } else {
        const error = await respuesta.json();
        alert("Error: " + (error.error || "No se pudo crear"));
    }
});
```

Agregá esto al HTML (después de la tabla) y al script. Cuando creés un jugador desde el formulario, la tabla se actualiza automáticamente.

---

### 5B — Reto: CRUD completo en frontend

Agregá al `index.html`:

1. **Botón "Eliminar"** en cada fila de la tabla. Al hacer click:
   - Confirmá con `confirm("¿Seguro que querés eliminar a X?")`
   - Hacé un `DELETE` a `{API}/jugador/{id}`
   - Si funciona, recargá la tabla

2. **Edición inline**: al hacer click en un nombre, convertí esa celda en un input para editar. Al perder el foco o presionar Enter, enviá un `PATCH` con el nuevo nombre.

3. Mostrá los **códigos de error** del servidor (400, 404) en la interfaz, no solo con `alert()`.

> **Pista:** para el botón eliminar, necesitás el ID de cada jugador. Modificá `mostrarJugadores()` para guardar el ID en un atributo `data-id` de la fila.

<details>
<summary><b>Solución (reto)</b></summary>

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Jugadores del Mundial 2026</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; max-width: 900px; }
        input, button { padding: 8px; margin: 3px; }
        table { border-collapse: collapse; width: 100%; margin-top: 10px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background: #1a3a5c; color: white; }
        .error { color: #999; font-style: italic; }
        .btn-eliminar { background: #d9534f; color: white; border: none; cursor: pointer; }
        .btn-eliminar:hover { background: #c9302c; }
        form { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; }
        input { border: 1px solid #ccc; border-radius: 3px; }
        .mensaje-error { color: #d9534f; font-weight: bold; }
        .celda-editable { cursor: pointer; }
        .celda-editable:hover { background: #fff3cd; }
    </style>
</head>
<body>
    <h1>Jugadores del Mundial 2026</h1>

    <form id="form-crear">
        <h3>Agregar jugador</h3>
        <input type="text" name="nombre" placeholder="Nombre" required>
        <input type="number" name="edad" placeholder="Edad">
        <input type="text" name="posicion" placeholder="Posición" required>
        <input type="text" name="equipo" placeholder="Equipo">
        <input type="text" name="seleccion" placeholder="Selección" required>
        <button type="submit">Agregar</button>
    </form>

    <div>
        <input type="text" id="busqueda" placeholder="Buscar por nombre...">
        <button onclick="buscarJugador()">Buscar</button>
        <button onclick="cargarJugadores()">Ver todos</button>
    </div>

    <p id="mensaje-estado"></p>

    <table>
        <thead>
            <tr>
                <th>Nombre</th>
                <th>Edad</th>
                <th>Posición</th>
                <th>Equipo</th>
                <th>Selección</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody id="tabla-jugadores"></tbody>
    </table>

    <script>
        const API = "http://127.0.0.1:5000";

        async function cargarJugadores() {
            const respuesta = await fetch(`${API}/jugadores`);
            const jugadores = await respuesta.json();
            mostrarJugadores(jugadores);
        }

        async function buscarJugador() {
            const q = document.getElementById("busqueda").value.trim();
            if (!q) { cargarJugadores(); return; }

            const respuesta = await fetch(`${API}/buscar-por-nombre?q=${q}`);
            const datos = await respuesta.json();
            mostrarJugadores(datos);
        }

        function mostrarJugadores(datos) {
            const tbody = document.getElementById("tabla-jugadores");
            const estado = document.getElementById("mensaje-estado");
            tbody.innerHTML = "";
            estado.textContent = "";

            if (datos.mensaje || datos.length === 0) {
                estado.textContent = datos.mensaje || "No se encontraron jugadores";
                estado.className = "error";
                return;
            }

            datos.forEach(j => {
                const fila = document.createElement("tr");
                fila.dataset.id = j.id;
                fila.innerHTML = `
                    <td class="celda-editable" data-campo="nombre">${j.nombre}</td>
                    <td>${j.edad}</td>
                    <td>${j.posicion}</td>
                    <td>${j.equipo}</td>
                    <td>${j.seleccion}</td>
                    <td><button class="btn-eliminar" data-id="${j.id}" data-nombre="${j.nombre}">Eliminar</button></td>
                `;
                tbody.appendChild(fila);
            });

            document.querySelectorAll(".btn-eliminar").forEach(btn => {
                btn.addEventListener("click", eliminarJugador);
            });

            document.querySelectorAll(".celda-editable").forEach(celda => {
                celda.addEventListener("click", editarCelda);
            });
        }

        async function eliminarJugador(e) {
            const id = e.target.dataset.id;
            const nombre = e.target.dataset.nombre;

            if (!confirm(`¿Seguro que querés eliminar a ${nombre}?`)) return;

            const respuesta = await fetch(`${API}/jugador/${id}`, {
                method: "DELETE"
            });

            if (respuesta.ok) {
                cargarJugadores();
            } else {
                const error = await respuesta.json();
                document.getElementById("mensaje-estado").textContent = "Error: " + (error.error || "No se pudo eliminar");
                document.getElementById("mensaje-estado").className = "mensaje-error";
            }
        }

        function editarCelda(e) {
            const celda = e.target;
            const campo = celda.dataset.campo;
            const id = celda.closest("tr").dataset.id;
            const valorActual = celda.textContent;

            const input = document.createElement("input");
            input.type = "text";
            input.value = valorActual;
            celda.textContent = "";
            celda.appendChild(input);
            input.focus();

            async function guardar() {
                const nuevoValor = input.value.trim();
                if (nuevoValor && nuevoValor !== valorActual) {
                    const respuesta = await fetch(`${API}/jugador/${id}`, {
                        method: "PATCH",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({[campo]: nuevoValor}),
                    });

                    if (respuesta.ok) {
                        cargarJugadores();
                    } else {
                        const error = await respuesta.json();
                        document.getElementById("mensaje-estado").textContent = "Error: " + (error.error || "No se pudo actualizar");
                        document.getElementById("mensaje-estado").className = "mensaje-error";
                        celda.textContent = valorActual;
                    }
                } else {
                    celda.textContent = valorActual;
                }
            }

            input.addEventListener("blur", guardar);
            input.addEventListener("keydown", (e) => {
                if (e.key === "Enter") {
                    e.preventDefault();
                    input.blur();
                }
                if (e.key === "Escape") {
                    celda.textContent = valorActual;
                }
            });
        }

        document.getElementById("form-crear").addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const datos = Object.fromEntries(formData.entries());

            if (datos.edad) datos.edad = parseInt(datos.edad);

            const respuesta = await fetch(`${API}/jugador`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(datos),
            });

            if (respuesta.ok) {
                e.target.reset();
                cargarJugadores();
            } else {
                const error = await respuesta.json();
                document.getElementById("mensaje-estado").textContent = "Error: " + (error.error || "No se pudo crear");
                document.getElementById("mensaje-estado").className = "mensaje-error";
            }
        });

        cargarJugadores();
    </script>
</body>
</html>
```

**Eso es todo. Tenés un CRUD completo funcionando:**
- El backend sirve el frontend y expone la API
- El frontend consume la API con `fetch`
- Podés crear, leer, actualizar (editando inline) y eliminar jugadores

</details>

---

## 6. Proyecto final — el desafío que separa a los que entienden de los que solo copian

### 6A — Demo: La arquitectura completa (mirá TODO lo que construimos)

Pará un toque y mirá esto:

```
Navegador (index.html)
       │
       │ fetch()  ← GET, POST, PATCH, DELETE
       ▼
Flask (app.py) ──► jugadores (lista de diccionarios en memoria)
       │
       │ send_from_directory()
       ▼
   index.html servido por Flask
```

¿Te das cuenta? **Todo vive en una sola URL** (`http://127.0.0.1:5000`). Flask sirve el frontend Y expone la API. Sin CORS, sin configuraciones raras, sin magia. Solo código que vos escribiste.

Hiciste un backend completo, con frontend incluido, que hace CRUD. Eso no es poco, causa.

---

### 6B — Reto final: Extendé la API con equipos (el que hace esto, ya la tiene clara)

Ahora que tenés el CRUD de jugadores funcionando como un campeón, agregá un nuevo recurso: **Equipos de fútbol**. Porque un jugador sin equipo es como un backend sin endpoints — no funciona.

1. Creá un diccionario `equipos` con data así:
```python
equipos = {
    1: {"nombre": "Real Madrid", "pais": "España", "liga": "La Liga", "copas": 15},
    2: {"nombre": "Liverpool", "pais": "Inglaterra", "liga": "Premier League", "copas": 6},
}
```

2. Implementá el CRUD completo para equipos (GET todos, GET por ID, POST, PATCH, DELETE)

3. Modificá `GET /jugadores` para que en lugar de mandar el nombre del equipo como texto, mande el objeto completo del equipo. O sea, si el jugador tiene `"equipo": "Real Madrid"`, que el endpoint devuelva los datos completos del Real Madrid.

4. Agregá en el frontend una sección para listar y crear equipos

5. **PLUS:** Hacé que al crear un jugador, el campo `equipo` sea un `<select>` que cargue los equipos desde la API. O sea, el frontend pide `GET /equipos` y llena el combo. Nivel dios.

<details>
<summary><b>Pistas (no solución — este reto es tuyo)</b></summary>

No te voy a dar la solución completa porque este es el ejercicio que separa a los que entienden de los que copian y pegan. Pero te tiro unos tips:

- Los endpoints de equipos son IDÉNTICOS en estructura a los de jugadores. Literalmente podés copiar y pegar, cambiar "jugador" por "equipo", y funciona.
- Para el punto 3, vas a necesitar un endpoint `GET /equipos` que devuelva un diccionario clave=nombre, valor=datos. Después en el frontend, cuando mostrés jugadores, buscá el equipo por nombre.
- Para el `<select>`, hacé un `fetch` a la API de equipos cuando cargue la página y llená las opciones.

Si te trabás, preguntá. Pero primero intentá. La diferencia entre un dev que sabe y uno que no, es que el primero **prueba antes de preguntar**.

</details>

---

## 🎯 Resumen de conceptos

| Tema | Demo | Reto | Conceptos clave |
|------|:----:|:----:|-----------------|
| 1. CRUD completo | ✅ | ✅ | GET, POST, PUT/PATCH, DELETE |
| 2. Validación de datos | ✅ | ✅ | Códigos 400, validar campos |
| 3. PUT vs PATCH | ✅ | ✅ | Reemplazo vs actualización parcial |
| 4. Frontend con fetch | ✅ | ✅ | `fetch()`, `GET`, HTML dinámico |
| 5. Servir HTML desde Flask | ✅ | ✅ | `send_from_directory()`, CORS |
| 6. CRUD desde frontend | ✅ | ✅ | POST/PATCH/DELETE con fetch |
| 7. Edición inline | ✅ | ✅ | Eventos de DOM, actualización parcial |
| 8. Proyecto integrador | ✅ | ✅ | CRUD completo funcional |
