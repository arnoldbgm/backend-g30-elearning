# 🧠 Guía — Día 1 (Semana 3): Entornos virtuales, pip y Flask

<p align="center">
  <img src="https://cdn.simpleicons.org/python" alt="Logo de Python" height="68" loading="lazy">
  &nbsp;&nbsp;&nbsp;
  <img src="https://cdn.simpleicons.org/flask/000000" alt="Logo de Flask" height="68" loading="lazy">
  &nbsp;&nbsp;&nbsp;
  <img src="https://cdn.simpleicons.org/postman" alt="Logo de Postman" height="68" loading="lazy">
  &nbsp;&nbsp;&nbsp;
  <img src="https://cdn.simpleicons.org/pypi" alt="Logo de PyPI" height="68" loading="lazy">
</p>


<p align="center">
  <img src="https://quickchart.io/graphviz?graph=digraph%20G%20%7B%0A%20%20graph%20%5Brankdir%3DLR%2C%20bgcolor%3D%22transparent%22%2C%20pad%3D%220.3%22%5D%3B%0A%20%20node%20%5Bshape%3Dbox%2C%20style%3D%22rounded%2Cfilled%22%2C%20color%3D%22%23384152%22%2C%20fillcolor%3D%22%23F6F8FA%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D14%5D%3B%0A%20%20edge%20%5Bcolor%3D%22%23607080%22%2C%20arrowsize%3D0.8%5D%3B%0A%20%20A%20%5Blabel%3D%221.%20venv%0AAislar%20proyecto%22%5D%3B%0A%20%20B%20%5Blabel%3D%222.%20pip%0AInstalar%20paquetes%22%5D%3B%0A%20%20C%20%5Blabel%3D%223.%20Postman%0AProbar%20requests%22%5D%3B%0A%20%20D%20%5Blabel%3D%224.%20Flask%0AServidor%20local%22%5D%3B%0A%20%20E%20%5Blabel%3D%225-7.%20API%0ARutas%2C%20JSON%2C%20c%C3%B3digos%20HTTP%22%5D%3B%0A%20%20A%20-%3E%20B%20-%3E%20C%20-%3E%20D%20-%3E%20E%3B%0A%7D" alt="Ruta visual del Día 1: venv, pip, Postman, Flask y API" width="760" loading="lazy">
</p>


Bienvenidos AL BACKEND. Sí, hoy dejamos de ser usuarios de Python y nos convertimos en desarrolladores que exponen servicios. Vamos a crear nuestro propio servidor, nuestra propia API, y la vamos a probar como Dios manda con **Postman**. Prepárense que esto cambia el juego.

Antes de escribir una sola línea, quiero que entiendan **por qué** existe todo esto. Porque si solo copian código sin entender el modelo mental, el día que algo falle van a estar perdidos. Así que vamos con calma al principio, y después sí, a codear.

---

## 0. El modelo cliente-servidor — la base de TODO lo que viene

<p align="center">
  <img src="https://quickchart.io/graphviz?graph=digraph%20G%20%7B%0A%20%20graph%20%5Brankdir%3DLR%2C%20bgcolor%3D%22transparent%22%2C%20pad%3D%220.3%22%5D%3B%0A%20%20node%20%5Bshape%3Dbox%2C%20style%3D%22rounded%2Cfilled%22%2C%20color%3D%22%23344054%22%2C%20fillcolor%3D%22%23F8FAFC%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D14%5D%3B%0A%20%20edge%20%5Bcolor%3D%22%23475467%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D12%5D%3B%0A%20%20C%20%5Blabel%3D%22Cliente%0APostman%20%2F%20navegador%20%2F%20app%22%5D%3B%0A%20%20S%20%5Blabel%3D%22Servidor%0AFlask%20en%20app.py%22%5D%3B%0A%20%20C%20-%3E%20S%20%5Blabel%3D%22Request%0AGET%20%2Fjugadores%22%5D%3B%0A%20%20S%20-%3E%20C%20%5Blabel%3D%22Response%0AJSON%20%2B%20c%C3%B3digo%20HTTP%22%5D%3B%0A%7D" alt="Diagrama cliente-servidor con request y response" width="760" loading="lazy">
</p>


Hasta ahora, cuando programaban en Python, ustedes escribían un script, lo ejecutaban, y ESE MISMO programa hacía todo: leía datos, los procesaba, mostraba resultados. Un solo actor.

En backend, la cosa cambia. Ahora hay **dos actores separados**:

- El **cliente**: es quien pide algo. Puede ser un navegador, una app de celular, Postman, otro programa. El cliente no sabe (ni le importa) cómo está hecho el servidor por dentro.
- El **servidor**: es quien escucha pedidos y responde. Nuestro `app.py` con Flask va a ser el servidor.

**Analogía (guárdensela, la van a usar todo el curso):** piensa en un restaurante. Tú (cliente) no entras a la cocina a cocinar tu propio plato. Le pides al mozo (la petición, el *request*) y la cocina (el servidor) te devuelve el plato (la respuesta, el *response*). No te importa cómo está organizada la cocina por dentro — te importa que el pedido llegue bien y rápido.

Eso es exactamente lo que va a pasar entre Postman (o cualquier app) y nuestro Flask:

```
Cliente (Postman)  --- pide algo -->  Servidor (Flask)
Cliente (Postman)  <-- responde ---  Servidor (Flask)
```

Cada "pedido" tiene una estructura: un **método** (¿qué quieres hacer? leer, crear, borrar...), una **URL** (¿a dónde le pides?), a veces un **body** (¿qué datos mandas?), y el servidor responde con **datos** + un **código de estado** (¿salió bien o mal?).

Con esto en la cabeza, ahora sí, empecemos a construir la cocina.

---

## 1. Entornos virtuales — la cajita mágica

<p align="center">
  <img src="https://quickchart.io/graphviz?graph=digraph%20G%20%7B%0A%20%20graph%20%5Brankdir%3DLR%2C%20bgcolor%3D%22transparent%22%2C%20pad%3D%220.3%22%5D%3B%0A%20%20node%20%5Bshape%3Dbox%2C%20style%3D%22rounded%2Cfilled%22%2C%20color%3D%22%23344054%22%2C%20fillcolor%3D%22%23F8FAFC%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D13%5D%3B%0A%20%20edge%20%5Bcolor%3D%22%23667085%22%5D%3B%0A%20%20SYS%20%5Blabel%3D%22Python%20del%20sistema%22%5D%3B%0A%20%20P1%20%5Blabel%3D%22Proyecto%20A%0Avenv%20propio%0AFlask%202%22%5D%3B%0A%20%20P2%20%5Blabel%3D%22Proyecto%20B%0Avenv%20propio%0AFlask%203%22%5D%3B%0A%20%20P3%20%5Blabel%3D%22Proyecto%20C%0Avenv%20propio%0Aotras%20librer%C3%ADas%22%5D%3B%0A%20%20SYS%20-%3E%20P1%3B%0A%20%20SYS%20-%3E%20P2%3B%0A%20%20SYS%20-%3E%20P3%3B%0A%7D" alt="Entornos virtuales aislados por proyecto" width="760" loading="lazy">
</p>


Imaginate que tienes dos proyectos: uno usa Flask versión 2, el otro Flask versión 3. Sin entornos virtuales, es un caos — una cosa le gana a la otra, se te rompe todo y terminas formateando la compu (me pasó, y no está bueno).

Un entorno virtual es como una **caja aislada** para cada proyecto. Cada uno tiene su propio Flask, sus propias versiones, y no se pelean entre sí.

**Sin entorno virtual**: instalas Flask para el proyecto A, después el proyecto B necesita otra versión → conflicto, explosión, lágrimas.

**Con entorno virtual**: cada proyecto tiene su cajita. Una no toca a la otra. Paz mundial.

**Otra analogía, porque esta es importante:** piensa en un edificio de departamentos. Cada departamento (proyecto) tiene sus propios muebles (librerías) y nadie se mete a poner sus cosas en el departamento del vecino. Python "del sistema" sería como la calle — de ahí NO quieres que dependa nada importante, porque ahí pasa cualquiera y desordena todo.

¿Por qué importa esto en un trabajo real? Porque cuando trabajes en una empresa, vas a tener 5, 10, 20 proyectos distintos en tu compu. Si todos comparten el mismo Python "pelado", el día que actualices una librería para el proyecto nuevo, le rompes el proyecto viejo sin darte cuenta. Los entornos virtuales evitan ESO.

---

### 1A — Demo: Crear y activar un entorno virtual

1. Abre una terminal en la carpeta de tu proyecto
2. Ejecuta:

```bash
python -m venv venv
```

Esto crea una carpeta `venv/` con una copia aislada de Python. Fíjate que aparece una carpeta nueva en tu proyecto — ábrela y vas a ver que tiene su propio `python.exe`, su propio `pip`, todo aparte.

3. Activa el entorno:

```bash
# Windows
venv\Scripts\activate
```

Vas a ver que aparece `(venv)` al inicio de la línea. Eso significa que estás dentro del entorno virtual. Es como si te hubieras puesto una casaca que dice "todo lo que instale ahora es solo para este proyecto".

Para desactivarlo:

```bash
deactivate
```

Cuando está activo, todo `pip install` va a parar **dentro de esta caja**, no al sistema.

---

### 1B — Reto: Verificá que funciona

1. Crea un entorno virtual llamado `mundo-python`
2. Activarlo
3. Ejecuta `python --version` y `pip --version` para confirmar
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

<p align="center">
  <img src="https://quickchart.io/graphviz?graph=digraph%20G%20%7B%0A%20%20graph%20%5Brankdir%3DLR%2C%20bgcolor%3D%22transparent%22%2C%20pad%3D%220.3%22%5D%3B%0A%20%20node%20%5Bshape%3Dbox%2C%20style%3D%22rounded%2Cfilled%22%2C%20color%3D%22%23344054%22%2C%20fillcolor%3D%22%23F8FAFC%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D13%5D%3B%0A%20%20edge%20%5Bcolor%3D%22%23667085%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D12%5D%3B%0A%20%20A%20%5Blabel%3D%22Terminal%0Avenv%20activado%22%5D%3B%0A%20%20B%20%5Blabel%3D%22pip%20install%20flask%22%5D%3B%0A%20%20C%20%5Blabel%3D%22PyPI.org%0Arepositorio%20de%20paquetes%22%5D%3B%0A%20%20D%20%5Blabel%3D%22venv%2F%0Apaquete%20instalado%22%5D%3B%0A%20%20A%20-%3E%20B%20-%3E%20C%20-%3E%20D%3B%0A%7D" alt="Flujo de instalación con pip desde PyPI hacia el entorno virtual" width="760" loading="lazy">
</p>


`pip` es el programa que usamos para instalar librerías externas. ¿Quieres Flask? `pip install flask`. ¿Quieres pandas? `pip install pandas`. ¿Quieres hacer una API y que funcione? `pip install` todo lo que necesités.

Flask NO viene con Python. Nadie nace sabiendo, hay que instalarlo. Y para eso está pip.

**Analogía:** pip es como el mercado central de Python. Python trae lo básico en la "despensa" (la librería estándar: `os`, `math`, `random`, etc.), pero para lo especializado — hacer un servidor web, procesar Excel, entrenar un modelo de IA — tienes que ir al mercado (PyPI, el repositorio oficial de paquetes) y traerlo con `pip install`.

Cuando haces `pip install flask` dentro de tu entorno virtual, pip va a **PyPI.org**, descarga el paquete y lo instala SOLO en la cajita de ese proyecto. Por eso el orden importa: primero creas y activas el entorno, DESPUÉS instalas.

### Comandos esenciales

| Comando | Qué hace |
|---------|----------|
| `pip install colorama` | Instala el paquete Colorama |
| `pip list` | Muestra los paquetes instalados |
| `pip freeze` | Lista los paquetes en formato `paquete==version` |
| `pip uninstall colorama` | Desinstala Colorama |

**¿Por qué `pip freeze` es tan importante?** Porque cuando trabajes en equipo (o subas tu proyecto a producción), nadie va a instalar paquete por paquete a mano. Generás un `requirements.txt` con las versiones EXACTAS que tú usaste, y cualquier otra persona (o servidor) puede recrear tu mismo entorno con un solo comando. Esto evita el clásico "en mi compu funciona" — chiste recontra viejo en programación, pero real como la vida misma.

---

### 2A — Demo: Instalar Colorama y ver magia en la terminal

Primero lo primero: instalemos algo **que se vea**. Nada de instalar una librería y no pasar nada — con Colorama ves colores al toque.

Con el entorno virtual activado:

```bash
pip install colorama
```

Después ejecuta:

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

1. Con el entorno activado, asegúrate de tener Colorama instalado
2. Escribí un archivo `cartel.py` que muestre un mensaje como este usando colores:

```
=== BIENVENIDO AL MUNDIAL 2026 ===
```

- El borde y el texto deben ser de distintos colores
- Usá `Fore.CYAN`, `Fore.MAGENTA`, `Fore.GREEN`, etc.
- Pruébalo varias veces cambiando colores

<details>
<summary><b>Solución (reto)</b></summary>

```python
from colorama import init, Fore

init()

print(Fore.CYAN + "=" * 35 + Fore.RESET)
print(Fore.YELLOW + "   BIENVENIDO AL MUNDIAL 2026" + Fore.RESET)
print(Fore.CYAN + "=" * 35 + Fore.RESET)
```

**Prueba también:**
```python
print(Fore.MAGENTA + "Perú" + Fore.GREEN + " campeón" + Fore.RESET)
```

</details>

---

## 3. Postman — la herramienta con la que vamos a vivir todo el curso

<p align="center">
  <img src="https://cdn.simpleicons.org/postman" alt="Logo de Postman" height="80" loading="lazy">
</p>

<p align="center">
  <img src="https://quickchart.io/graphviz?graph=digraph%20G%20%7B%0A%20%20graph%20%5Brankdir%3DLR%2C%20bgcolor%3D%22transparent%22%2C%20pad%3D%220.3%22%5D%3B%0A%20%20node%20%5Bshape%3Dbox%2C%20style%3D%22rounded%2Cfilled%22%2C%20color%3D%22%23344054%22%2C%20fillcolor%3D%22%23F8FAFC%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D13%5D%3B%0A%20%20edge%20%5Bcolor%3D%22%23667085%22%5D%3B%0A%20%20M%20%5Blabel%3D%22M%C3%A9todo%0AGET%20%2F%20POST%20%2F%20PATCH%20%2F%20DELETE%22%5D%3B%0A%20%20U%20%5Blabel%3D%22URL%0Ahttp%3A%2F%2F127.0.0.1%3A5000%2Fjugadores%22%5D%3B%0A%20%20B%20%5Blabel%3D%22Body%0AJSON%20cuando%20toca%22%5D%3B%0A%20%20S%20%5Blabel%3D%22Send%22%5D%3B%0A%20%20R%20%5Blabel%3D%22Respuesta%0Abody%20%2B%20status%20code%22%5D%3B%0A%20%20M%20-%3E%20U%20-%3E%20B%20-%3E%20S%20-%3E%20R%3B%0A%7D" alt="Partes principales de una petición en Postman" width="760" loading="lazy">
</p>


Antes de Flask, un momento para esto: **Postman va a ser tu compañero de todos los días de acá en adelante**. No es opcional, no es "para después". Cada endpoint que hagamos se prueba en Postman AL TOQUE, apenas está escrito. No hay excusas de "ya lo probaré después".

**¿Por qué no usar el navegador y ya?** Porque el navegador solo sabe hacer GET fácilmente. No puedes mandar un body en JSON con un click, no puedes guardar tus peticiones, no puedes armar una colección ordenada de todos tus endpoints. Postman te da control total sobre el método, la URL, los headers y el body — que es exactamente lo que necesitás para probar una API de verdad.

### 3.1 — Instalación

1. Ve a **postman.com/downloads** y descargá la versión para tu sistema operativo.

> **Imagen sugerida para clase:** puedes reemplazar este bloque por una captura propia de `postman.com/downloads`, mostrando los botones de descarga para Windows/Mac/Linux. Mejor captura propia que imagen ajena, pe.

2. Instalá como cualquier programa (siguiente, siguiente, finalizar).
3. Abre Postman y crea una cuenta gratuita (o entrá como invitado, para lo que vamos a hacer alcanza).

### 3.2 — Conociendo la interfaz

Cuando abras Postman por primera vez, prestá atención a estas zonas:

- **Botón "New" / "+"** → para crear una petición nueva.
- **Selector de método** (GET, POST, PATCH, DELETE...) → arriba a la izquierda del campo de URL.
- **Campo de URL** → donde escribís, por ejemplo, `http://127.0.0.1:5000/jugadores`.
- **Pestaña "Body"** → donde vas a mandar JSON cuando hagamos POST o PATCH.
- **Botón "Send"** → dispara la petición.
- **Zona de respuesta** (abajo) → acá aparece lo que el servidor te devolvió, y el código de estado bien grande arriba a la derecha.

> **Imagen sugerida para clase:** captura propia de Postman con una petición GET armada, señalando método, URL y botón **Send**.

> **Imagen sugerida para clase:** captura propia de la pestaña **Body → raw → JSON**, con un JSON pequeño de ejemplo.

**Regla de oro del curso:** cada vez que creemos un endpoint nuevo en Flask, el siguiente paso — SIEMPRE — es abrir Postman y probarlo. No seguimos al próximo endpoint sin haber confirmado que el anterior responde bien.

---

## 4. Flask — tu primer servidor (y te juro que no es brujería)

<p align="center">
  <img src="https://cdn.simpleicons.org/flask/000000" alt="Logo de Flask" height="80" loading="lazy">
</p>

<p align="center">
  <img src="https://quickchart.io/graphviz?graph=digraph%20G%20%7B%0A%20%20graph%20%5Brankdir%3DLR%2C%20bgcolor%3D%22transparent%22%2C%20pad%3D%220.3%22%5D%3B%0A%20%20node%20%5Bshape%3Dbox%2C%20style%3D%22rounded%2Cfilled%22%2C%20color%3D%22%23344054%22%2C%20fillcolor%3D%22%23F8FAFC%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D13%5D%3B%0A%20%20edge%20%5Bcolor%3D%22%23667085%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D12%5D%3B%0A%20%20URL%20%5Blabel%3D%22GET%20%2F%22%5D%3B%0A%20%20DEC%20%5Blabel%3D%22%40app.route%28%27%2F%27%29%22%5D%3B%0A%20%20FUN%20%5Blabel%3D%22def%20inicio%28%29%22%5D%3B%0A%20%20RES%20%5Blabel%3D%22return%20%27Hola%2C%20mundo%20Flask%21%27%22%5D%3B%0A%20%20URL%20-%3E%20DEC%20-%3E%20FUN%20-%3E%20RES%3B%0A%7D" alt="Cómo Flask conecta una URL con una función" width="760" loading="lazy">
</p>


Flask es un **microframework**. ¿Qué significa "micro"? Que te da lo mínimo para construir un servidor web sin imponerte cómo ordenar tu código. No trae ORM, no trae autenticación, no trae un montón de cosas que no necesitás hoy. Cuando las necesites, las agregás.

**Analogía:** si Django (otro framework de Python) es como comprar un departamento amoblado — ya viene con todo puesto, pero tienes que acomodarte a como está armado — Flask es como comprar un departamento vacío. Tú decidís dónde va cada mueble. Al principio da un poco más de trabajo, pero para aprender backend desde cero es IDEAL, porque entendés qué hace cada pieza en vez de que la magia te la esconda.

Pero lo importante: **con 4 líneas de código ya tienes un servidor funcionando**. ¿A que no sabías que era tan fácil?

### 4A — Demo: Hola Mundo en Flask

Crea un archivo `app.py`:

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

Abre el navegador en `http://127.0.0.1:5000`. Vas a ver "Hola, mundo Flask!" en la pantalla. **Ya tienes un servidor web, loco. FELICITACIONES.**

**Lo que pasó (prestá atención porque esto es la BASE de todo):**
- `from flask import Flask` → importamos la clase principal de Flask
- `app = Flask(__name__)` → creamos una instancia de la aplicación. Este objeto `app` es literalmente "tu restaurante": todo lo que agreguemos de acá en adelante (rutas, configuración) cuelga de él.
- `@app.route("/")` → esto es un **decorador**. Le decís a Flask: "Cuando alguien visite la raíz, ejecuta esta función". Es como poner un cartel en la puerta del restaurante: "acá se atiende el pedido de la mesa 1".
- `def inicio()` → la función que se ejecuta. Tiene que devolver algo (un string, un JSON, un HTML)
- cuando ejecutas `app.py`, Flask inicia un servidor en `http://127.0.0.1:5000` (`127.0.0.1` es tu propia computadora — se llama "localhost" — y `5000` es el puerto, como el número de mesa donde te vienen a atender)

**Ahora sí, probemos esto en Postman en vez de en el navegador** (recordá la regla de oro):

- Método: `GET`
- URL: `http://127.0.0.1:5000/`
- Send → deberías ver "Hola, mundo Flask!" en la zona de respuesta, con código **200**.

---

### 4B — Reto: Personaliza tu servidor

1. Crea un entorno virtual nuevo llamado `flask-crud`
2. Activarlo
3. Instalar Flask
4. Crear `app.py` con tu propio servidor que tenga:
   - Una ruta `/` que muestre "Bienvenido a la API de Jugadores del Mundial 2026"
   - Una ruta `/info` que devuelva `{"version": "1.0", "curso": "Backend con Flask"}`
   - **Pruébalo en Postman**: crea un GET a `http://127.0.0.1:5000/` y otro a `http://127.0.0.1:5000/info`

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

> **Nota:** Flask convierte automaticamente los diccionarios a JSON cuando los devuelves en una ruta.

</details>

---

## 5. Rutas dinámicas — cuando una URL vale más que mil palabras

<p align="center">
  <img src="https://quickchart.io/graphviz?graph=digraph%20G%20%7B%0A%20%20graph%20%5Brankdir%3DTB%2C%20bgcolor%3D%22transparent%22%2C%20pad%3D%220.3%22%5D%3B%0A%20%20node%20%5Bshape%3Dbox%2C%20style%3D%22rounded%2Cfilled%22%2C%20color%3D%22%23344054%22%2C%20fillcolor%3D%22%23F8FAFC%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D13%5D%3B%0A%20%20edge%20%5Bcolor%3D%22%23667085%22%5D%3B%0A%20%20A%20%5Blabel%3D%22%2Fjugador%2F7%0APar%C3%A1metro%20de%20ruta%0AIdentifica%20un%20recurso%22%5D%3B%0A%20%20B%20%5Blabel%3D%22%2Fbuscar%3Fposicion%3DDelantero%26edad_max%3D30%0AQuery%20params%0AFiltran%20una%20lista%22%5D%3B%0A%7D" alt="Diferencia entre parámetro de ruta y query params" width="760" loading="lazy">
</p>


Una API de verdad no tiene rutas fijas como `/jugador1`, `/jugador2`, `/jugador3`. Eso es una locura. Necesitás rutas que **cambien según lo que el cliente pida**. Algo como `/jugador/7` y que te devuelva al jugador con ID 7. Eso es una ruta dinámica, y es hermoso.

**Analogía:** piensa en las casillas de un correo. No existe una ventanilla distinta para cada paquete del mundo — existe UNA ventanilla que dice "casillero N°___", y tú completás el número. `/jugador/<int:id>` es exactamente eso: una sola ruta que sirve para CUALQUIER id que le pongas.

Hay dos formas de mandarle información extra a una ruta:

### Parámetros de ruta (`<tipo:nombre>`)

Van pegados a la URL, y normalmente identifican **un recurso específico**.

```python
@app.route("/jugador/<int:id>")
def obtener_jugador(id):
    return {"jugador_id": id, "nombre": "Ejemplo"}
```

### Parámetros de query (`request.args`)

Van después de un `?`, y normalmente sirven para **filtrar o buscar**, no para identificar un recurso puntual.

```python
@app.route("/buscar")
def buscar():
    nombre = request.args.get("nombre")
    return {"buscaste": nombre}
```

Esto responde a: `GET /buscar?nombre=Paolo`

**¿Cuándo uso cada uno?** Regla práctica: si estás pidiendo "ESE jugador puntual" → parámetro de ruta (`/jugador/3`). Si estás pidiendo "dame los que cumplan tal condición" → query params (`/buscar?posicion=Delantero`).

---

### 5A — Demo: Endpoint con jugadores hardcodeados

Fíjate bien la estructura: **una lista de diccionarios**. Cada jugador tiene su propio `id` adentro, como debe ser. Esto es clave: como todavía no usamos base de datos, la lista `jugadores` vive en la memoria del programa mientras el servidor está corriendo — es nuestra "base de datos falsa" por ahora.

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

**Fíjate cómo buscamos al jugador:** recorremos la lista entera con un `for`, comparamos `id` por `id`, y en el momento que coincide, devolvemos. Si el `for` termina y nunca encontró nada, cae en el `return` de abajo con el error 404. **Nada de acceso directo por índice o por clave mágica** — así es como se busca en una lista de diccionarios, y así lo vamos a hacer TODO el curso.

**Pruébalo en Postman:**
- `GET /` → bienvenida
- `GET /jugador/1` → datos de Paolo Guerrero
- `GET /jugador/99` → error 404
- `GET /jugadores` → lista de todos

---

### 5B — Reto: Endpoints de selecciones

Agregale al mismo `app.py`:

1. Una ruta `/seleccion/<nombre>` que devuelva todos los jugadores de esa selección. Ej: `GET /seleccion/Argentina` → solo Messi
2. Una ruta `/buscar` que acepte query params:
   - `?posicion=Delantero` → filtre por posición
   - `?edad_max=30` → jugadores menores o iguales a esa edad
   - **Combinables**: `?posicion=Delantero&edad_max=30`
3. Si no hay resultados, devuelve `{"mensaje": "No se encontraron jugadores"}` con código 200

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

**Pruébalo en Postman:**
- `GET /seleccion/Peru` → 3 jugadores
- `GET /seleccion/brasil` → Vinícius Jr
- `GET /buscar?posicion=Delantero` → Guerrero y Messi
- `GET /buscar?edad_max=30` → Tapia, Vinícius Jr
- `GET /buscar?posicion=Delantero&edad_max=35` → solo Messi
- `GET /buscar?posicion=Arquero` → "No se encontraron jugadores"

</details>

---

## 6. Mandar datos desde Postman — ya no es solo leer, ahora escribimos

<p align="center">
  <img src="https://quickchart.io/graphviz?graph=digraph%20G%20%7B%0A%20%20graph%20%5Brankdir%3DLR%2C%20bgcolor%3D%22transparent%22%2C%20pad%3D%220.3%22%5D%3B%0A%20%20node%20%5Bshape%3Dbox%2C%20style%3D%22rounded%2Cfilled%22%2C%20color%3D%22%23344054%22%2C%20fillcolor%3D%22%23F8FAFC%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D13%5D%3B%0A%20%20edge%20%5Bcolor%3D%22%23667085%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D12%5D%3B%0A%20%20P%20%5Blabel%3D%22Postman%0ABody%20raw%20JSON%22%5D%3B%0A%20%20F%20%5Blabel%3D%22Flask%0Arequest.json%22%5D%3B%0A%20%20D%20%5Blabel%3D%22dict%20de%20Python%0Adatos.get%28%27nombre%27%29%22%5D%3B%0A%20%20R%20%5Blabel%3D%22Respuesta%0AJSON%20%2B%20201%22%5D%3B%0A%20%20P%20-%3E%20F%20-%3E%20D%20-%3E%20R%3B%0A%7D" alt="Flujo de datos JSON desde Postman hacia Flask" width="760" loading="lazy">
</p>


Hasta ahora solo hicimos GET: pedir datos. Pero una API de verdad necesita **crear** cosas. ¿Y cómo le mandas datos al servidor? Por el **body** de la petición.

Retomando la analogía del restaurante: GET es el menú (leer los platos), POST es hacer el pedido (crear algo nuevo). El mozo necesita saber QUÉ quieres, y eso va en el body — no lo puedes meter en la URL porque puede ser información compleja (nombre, edad, posición, todo junto).

### Tipos de body (el que manda es JSON)

| Tipo | Content-Type | Cómo se lee en Flask |
|------|-------------|----------------------|
| JSON | `application/json` | `request.json` → devuelve un diccionario |
| Formulario | `application/x-www-form-urlencoded` | `request.form` |
| Texto plano | `text/plain` | `request.data` |

Nosotros usamos **JSON**, porque es el estándar en APIs REST. Punto.

**¿Por qué JSON y no, no sé, Python puro?** Porque el cliente que le habla a tu API no siempre es Python. Puede ser una app en JavaScript, una app de Android, otro servidor en Java. JSON es un formato de texto que TODOS los lenguajes saben leer y escribir, así que es el idioma universal para que sistemas distintos se entiendan. Y fíjate que su estructura es prácticamente igual a un diccionario de Python — por eso Flask lo convierte tan fácil.

### Cómo configurar Postman para mandar JSON

1. Elegí método **POST**
2. En la pestaña **Body** → **raw** → **JSON**
3. Escribí el JSON lindo y enviá

> **Imagen sugerida para clase:** captura propia de Postman con método **POST**, pestaña **Body → raw → JSON**, JSON cargado y botón **Send** resaltado.

---

### 6A — Demo: Endpoint POST que recibe JSON

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
- `methods=["POST"]` → por defecto Flask solo acepta GET. Hay que decirle explícitamente qué métodos acepta. Si pruebas con GET en Postman sobre esta ruta, Flask te va a devolver un error 405 ("Method Not Allowed") — pruébalo, para que veas el error con tus propios ojos.
- `request.json` → Flask parsea automaticamente el JSON del body y lo convierte en un diccionario
- Si no se envió JSON, `request.json` es `None`, y si intentas hacer `.get()` sobre `None` te va a explotar el programa — por eso en el reto de abajo validamos antes de usar los datos.

---

### 6B — Reto: Validar datos recibidos

Crea un endpoint `POST /jugador` que reciba JSON con los datos de un nuevo jugador y lo agregue a la lista `jugadores`. Validá:

- `nombre`: obligatorio, no vacío
- `posicion`: obligatorio
- `seleccion`: obligatorio
- Si falta algún campo obligatorio, devuelve `{"error": "Falta el campo: nombre"}` con código **400**
- Si todo está bien, asignale un ID nuevo (el máximo + 1) y devuelve el jugador creado con código **201**

> **Pista:** para sacar el máximo ID tienes que recorrer la lista con un `for`, guardar el más grande, y sumarle 1. Nunca uses `len(jugadores) + 1` para el ID — si alguna vez borran un jugador del medio, te van a quedar IDs repetidos. El máximo + 1 es la forma correcta.

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

## 7. Códigos de estado HTTP — el servidor también tiene emociones

<p align="center">
  <img src="https://quickchart.io/graphviz?graph=digraph%20G%20%7B%0A%20%20graph%20%5Brankdir%3DLR%2C%20bgcolor%3D%22transparent%22%2C%20pad%3D%220.3%22%5D%3B%0A%20%20node%20%5Bshape%3Dbox%2C%20style%3D%22rounded%2Cfilled%22%2C%20color%3D%22%23344054%22%2C%20fillcolor%3D%22%23F8FAFC%22%2C%20fontname%3D%22Arial%22%2C%20fontsize%3D13%5D%3B%0A%20%20A%20%5Blabel%3D%222xx%0A%C3%89xito%0A200%20%2F%20201%20%2F%20204%22%5D%3B%0A%20%20B%20%5Blabel%3D%224xx%0AError%20del%20cliente%0A400%20%2F%20404%22%5D%3B%0A%20%20C%20%5Blabel%3D%225xx%0AError%20del%20servidor%0A500%22%5D%3B%0A%7D" alt="Familias de códigos HTTP más usadas" width="760" loading="lazy">
</p>


Cuando tu servidor responde, no solo manda datos. También manda un **código de estado** que es como su carita: le dice al cliente si todo salió bien, si se equivocó, si no encontró algo, o si explotó todo.

**Analogía:** piensa en un semáforo con muchos más colores que el normal. Verde total (200-201) significa "ve tranquilo, todo salió bien". Amarillo (400) significa "pará, algo mandaste mal, revisa tu pedido". Un cartel de "no existe" (404) significa "acá no hay nada, seguí buscando en otro lado". Y rojo total (500) significa "chocamos, algo se rompió del lado del servidor, y no es tu culpa".

Y esto es CLAVE: una API no es solo devolver datos, es devolverlos con el código correcto. Si no, el cliente (que puede ser una app hecha por OTRO equipo, que ni conocés) no tiene forma de saber automaticamente si su pedido salió bien o mal — tendría que "adivinar" leyendo el mensaje de texto, y eso rompe toda la lógica de una API bien hecha.

### Los códigos que más vas a usar (apréndetelos, en serio):

| Código | Significado | Cuándo usarlo |
|--------|------------|---------------|
| **200** | OK | Todo bien, acá están tus datos |
| **201** | Created | Acabo de crear algo, toma |
| **204** | No Content | Lo eliminé, no hay nada que devolver |
| **400** | Bad Request | Mandaste cualquier cosa, revisa |
| **404** | Not Found | Eso que buscas no existe, pe |
| **500** | Internal Server Error | Algo explotó del lado del servidor |

**Un dato que les va a servir toda la carrera:** los códigos están agrupados por familia según el primer dígito. Los que empiezan con **2** son éxito, los que empiezan con **4** son error DEL CLIENTE (mandaste algo mal tú), y los que empiezan con **5** son error DEL SERVIDOR (la rompió el backend, no tú). Cuando algo falle, mira primero ese primer número — te dice para qué lado mirar.

En Flask, devuelves el código como segundo valor en el `return`:

```python
return {"error": "No encontrado"}, 404
return nuevo_jugador, 201
```

Sí, es así de simple. El primer valor son los datos, el segundo es el código. Si no pones nada, Flask asume **200** por defecto — por eso en el Hola Mundo del principio nunca escribimos un código y todo funcionó igual.

---

### 6A — Demo: Prueba los códigos en Postman como un profesional

Con tu `app.py` corriendo (el del reto anterior), prueba esto en Postman y mira el código que devuelve cada uno:

1. `GET /jugador/99` → código **404** — no existe, obvio
2. `POST /jugador` sin body o con body vacío → código **400** — mandaste mal los datos
3. `POST /jugador` con JSON válido → código **201** — se creó con éxito
4. `GET /jugador/6` → código **200** — acá está el jugador que creaste

En Postman, el código de estado aparece arriba a la derecha, bien grande, y viene coloreado (verde para éxito, naranja/rojo para error). No lo ignores. Es tan importante como los datos.

> **Imagen sugerida para clase:** captura propia de la zona de respuesta de Postman resaltando el código de estado, por ejemplo **200 OK** o **404 Not Found**.

---

### 7B — Reto: Mejora los códigos de estado

Toma el `app.py` del reto 5B y asegúrate de que **todas** las rutas devuelvan el código de estado correcto:

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

Revisa el código del reto 5B — ya tiene los códigos correctos. Verificá con Postman cada caso listado arriba y confirmá que el código que devuelve coincida.

Si algún endpoint no devuelve el código esperado, ajustalo.

</details>

---

## 🖼️ Checklist visual para el profe

Antes de dictar esta guía, revisa que tengas estas imágenes visibles o reemplazadas por capturas propias:

| Imagen | Ya incluida | Recomendación |
|--------|:-----------:|---------------|
| Logos de Python, Flask, Postman y PyPI | ✅ | Úsalos solo como referencia educativa. |
| Diagrama cliente-servidor | ✅ | Explícalo antes de codear. |
| Diagrama de entorno virtual | ✅ | Refuerza la idea de aislamiento. |
| Flujo `pip install` → PyPI → `venv` | ✅ | Sirve para explicar `requirements.txt`. |
| Partes de una petición en Postman | ✅ | Postman first, causa. |
| Capturas reales de Postman | ⚠️ | Mejor toma capturas propias en tu PC. |
| Códigos HTTP por familia | ✅ | Úsalo cuando empiecen los errores. |

---

## 🎯 Resumen de conceptos

| Tema | Demo | Reto | Conceptos clave |
|------|:----:|:----:|-----------------|
| 0. Cliente-servidor | — | — | request, response, modelo de comunicación |
| 1. Entorno virtual | ✅ | ✅ | `venv`, activación, aislamiento |
| 2. pip y dependencias | ✅ | ✅ | `pip install`, `freeze`, `requirements.txt` |
| 3. Postman | — | — | instalación, interfaz, método, URL, body |
| 4. Flask Hello World | ✅ | ✅ | `Flask`, `@app.route()`, servidor |
| 5. Rutas dinámicas | ✅ | ✅ | `<int:id>`, `request.args`, query params |
| 6. POST y request.json | ✅ | ✅ | `methods=["POST"]`, validación, código 201 |
| 7. Códigos HTTP | ✅ | ✅ | familias 2xx/4xx/5xx, 200, 201, 400, 404 |

---

## Fuentes visuales usadas

- Logos vía Simple Icons CDN: `https://cdn.simpleicons.org/`
- Diagramas generados como imágenes con QuickChart Graphviz: `https://quickchart.io/graphviz`
- Referencias oficiales/marca para revisar antes de publicación externa:
  - Python Software Foundation — uso del logo de Python
  - Postman — press/media y logo usage
  - Flask/Pallets — proyecto Flask
  - PyPI — Python Package Index

> Para material interno de clase está bien como apoyo visual. Para vender/publicar el curso, revisa las guías de marca de cada logo, causa.

