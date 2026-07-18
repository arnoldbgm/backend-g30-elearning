# 🧠 Guía — Día 2 (Semana 5): Consultas SELECT con Flask-SQLAlchemy

<p align="center">
  <img src="https://www.sqlalchemy.org/img/sqla_logo.png" alt="Logo de SQLAlchemy" height="80">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://flask.palletsprojects.com/en/stable/_static/flask-logo.png" alt="Logo de Flask" height="60">
</p>

Ayer aprendimos a conectarnos a PostgreSQL con psycopg2 y escribir SQL manual. Hoy damos el siguiente paso: aprender a hacer **consultas SELECT, INSERT, UPDATE y DELETE** con el estilo clásico de Flask-SQLAlchemy (`Model.query`). Con esto completamos el **CRUD completo** — las 4 operaciones básicas que todo sistema necesita.

Si ayer fue como cocinar siguiendo una receta paso a paso (escribiendo cada query), hoy es como tener un asistente de cocina que entiende lo que querés hacer solo con que se lo pidas.

---

## 0. El modelo de hoy — Usuario (10 min)

Para esta guía vamos a usar un modelo `Usuario` más sencillo que el de ayer, así nos enfocamos en aprender las consultas sin complicarnos con relaciones:

```python
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost:5432/musica_peruana"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    edad = db.Column(db.Integer)
    correo = db.Column(db.String(100))
    activo = db.Column(db.Boolean)
```

**¿Por qué este modelo?** Porque es simple: 5 columnas, sin relaciones. Nos permite practicar cada tipo de consulta sin distracciones.

### Crear la tabla y datos de prueba

Ejecutá esto en pgAdmin para crear la tabla y llenarla con datos:

```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    edad INTEGER,
    correo VARCHAR(100),
    activo BOOLEAN
);

INSERT INTO usuarios (nombre, edad, correo, activo) VALUES
    ('Juan', 20, 'juan@gmail.com', TRUE),
    ('Ana', 30, 'ana@gmail.com', TRUE),
    ('Pedro', 25, 'pedro@gmail.com', TRUE),
    ('María', 17, 'maria@gmail.com', FALSE),
    ('Carlos', 22, NULL, TRUE),
    ('Laura', 35, 'laura@gmail.com', TRUE),
    ('Diego', 15, 'diego@gmail.com', FALSE),
    ('Sofía', 28, 'sofia@gmail.com', TRUE),
    ('Luis', 40, NULL, FALSE),
    ('Carmen', 19, 'carmen@gmail.com', TRUE);
```

---

## 1. Básicas — Obtener registros (20 min)

Estas son las consultas que vas a usar el 90% del tiempo. Son como los utensilios básicos de una cocina: sin ellos no podés cocinar.

### 1A — Obtener todos los registros

```python
usuarios = Usuario.query.all()
```

**¿Qué devuelve?** Una **lista** de objetos `Usuario`. Es como pedirle a la base de datos: "dame todo lo que tengas en la tabla usuarios".

**Resultado:**
```
[<Usuario 1>, <Usuario 2>, <Usuario 3>, ...]
```

Para verlos bonitos en Flask:

```python
@app.route("/usuarios", methods=["GET"])
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([u.__dict__ for u in usuarios])
```

---

### 1B — Obtener el primer registro

```python
usuario = Usuario.query.first()
```

**¿Qué devuelve?** Un **objeto** `Usuario` o `None` si la tabla está vacía.

Es como decir: "dame el primero que encuentres". No importa cuántos haya, solo trae el primero.

---

### 1C — Buscar por clave primaria

```python
usuario = Usuario.query.get(1)
```

**¿Qué devuelve?** El usuario con `id=1` o `None` si no existe.

`.get()` es especial porque busca directamente por la primary key. Es como tener un archivero con numeración: le decís "dame el documento número 1" y te lo trae directo.

---

### 1D — Obtener un solo registro obligatorio

```python
usuario = Usuario.query.filter_by(id=1).one()
```

**¿Qué devuelve?** Un usuario o **lanza excepción** si no existe o si hay más de uno.

Usá `.one()` cuando estás **seguro** de que solo hay un resultado. Si hay más de uno o ninguno, Python lanza error. Es como decir: "dame UNO, y si no hay uno solo, ¡alarmame!"

---

### 1E — Obtener uno o ninguno

```python
usuario = Usuario.query.filter_by(id=1).one_or_none()
```

**¿Qué devuelve?** Un usuario o `None`. No lanza excepción.

Es la versión tranquila de `.one()`. Si hay más de uno, también lanza error. Pero si no hay ninguno, simplemente devuelve `None`.

---

### Comparación de los métodos básicos

| Método | ¿Qué hace? | Si no hay nada | Si hay varios |
|--------|-------------|----------------|---------------|
| `.all()` | Trae todos | Lista vacía `[]` | Lista con todos |
| `.first()` | Trae el primero | `None` | Solo el primero |
| `.get(id)` | Busca por PK | `None` | — |
| `.one()` | Busca uno solo | Excepción | Excepción |
| `.one_or_none()` | Busca uno solo | `None` | Excepción |

---

### 1F — Reto: Probá los métodos básicos

Creá una ruta `GET /usuarios/primero` que devuelva el primer usuario de la base de datos.

<details>
<summary><b>Solución (reto)</b></summary>

```python
@app.route("/usuarios/primero", methods=["GET"])
def get_primero():
    usuario = Usuario.query.first()

    if usuario is None:
        return jsonify({"mensaje": "No hay usuarios"}), 200

    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "edad": usuario.edad,
        "correo": usuario.correo,
        "activo": usuario.activo
    })
```

**¿Por qué verificamos `None`?** Porque `.first()` puede devolver `None` si la tabla está vacía. Si intentamos acceder a `usuario.nombre` sin verificar, tendríamos un error.

</details>

---

## 2. Filtrar registros (25 min)

Filtrar es como decirle a la base de datos: "no me des todo, solo lo que cumpla esta condición". Es una de las cosas más importantes que vas a hacer.

### 2A — filter_by() — Filtrado por igualdad

```python
usuarios = Usuario.query.filter_by(nombre="Juan").all()
```

**`filter_by()`** es para filtros **simples** por igualdad. Es como decir: "dame todos los usuarios que se llamen Juan".

También podés combinar varios campos:

```python
usuarios = Usuario.query.filter_by(
    nombre="Juan",
    activo=True
).all()
```

Esto es como decir: "dame todos los usuarios que se llamen Juan **Y** que estén activos".

---

### 2B — filter() — Filtrado con operadores

```python
usuarios = Usuario.query.filter(
    Usuario.edad > 18
).all()
```

**`filter()`** es más potente que `filter_by()` porque permite **operadores de comparación**. Es como decir: "dame todos los usuarios mayores de 18".

La diferencia clave es que con `filter()` usás la **clase** (`Usuario.edad`) en vez de un string (`edad`).

---

### Operadores de comparación

| Operador | Ejemplo | Significado |
|----------|---------|-------------|
| `==` | `Usuario.nombre == "Pedro"` | Igual |
| `!=` | `Usuario.nombre != "Pedro"` | Distinto |
| `>` | `Usuario.edad > 18` | Mayor que |
| `>=` | `Usuario.edad >= 18` | Mayor o igual |
| `<` | `Usuario.edad < 18` | Menor que |
| `<=` | `Usuario.edad <= 18` | Menor o igual |

**Ejemplo completo:**

```python
# Todos los menores de 18
menores = Usuario.query.filter(Usuario.edad < 18).all()

# Todos los que no se llaman Juan
no_juan = Usuario.query.filter(Usuario.nombre != "Pedro").all()

# Todos los mayores o iguales a 30
mayores = Usuario.query.filter(Usuario.edad >= 30).all()
```

---

### 2C — Reto: Filtrá por edad

Creá una ruta `GET /usuarios/mayores` que devuelva todos los usuarios mayores de 18 años.

<details>
<summary><b>Solución (reto)</b></summary>

```python
@app.route("/usuarios/mayores", methods=["GET"])
def get_mayores():
    usuarios = Usuario.query.filter(Usuario.edad > 18).all()

    return jsonify([{
        "id": u.id,
        "nombre": u.nombre,
        "edad": u.edad
    } for u in usuarios])
```

</details>

---

## 3. Combinar filtros — AND, OR, NOT (20 min)

Hasta ahora filtramos por una sola condición. Pero en la vida real, casi siempre necesitás combinar varias condiciones. Es como cuando pedís delivery: "quiero algo que sea de comida **Y** que esté cerca **Y** que no sea muy caro".

### 3A — AND (todas las condiciones)

```python
from sqlalchemy import and_

# Opción 1: separar con coma (más fácil)
usuarios = Usuario.query.filter(
    Usuario.edad > 18,
    Usuario.activo == True
).all()

# Opción 2: usar and_ (más explícito)
usuarios = Usuario.query.filter(
    and_(
        Usuario.edad > 18,
        Usuario.activo == True
    )
).all()
```

**¿Qué hace?** Trae usuarios que cumplan **TODAS** las condiciones: mayores de 18 **Y** activos.

La opción 1 (separar con coma) es más corta y se usa más. La opción 2 es más explícita cuando querés dejar claro que es un AND.

---

### 3B — OR (al menos una condición)

```python
from sqlalchemy import or_

usuarios = Usuario.query.filter(
    or_(
        Usuario.edad < 18,
        Usuario.activo == True
    )
).all()
```

**¿Qué hace?** Trae usuarios que cumplan **AL MENOS UNA** condición: menores de 18 **O** activos (o ambos).

---

### 3C — NOT (negar una condición)

```python
from sqlalchemy import not_

usuarios = Usuario.query.filter(
    not_(Usuario.activo)
).all()
```

**¿Qué hace?** Trae usuarios que **NO** estén activos. Es como decir: "dame todos los que NO estén activos".

También podés escribirlo así:

```python
usuarios = Usuario.query.filter(
    Usuario.activo == False
).all()
```

Ambas formas son equivalentes.

---

### 3D — Reto: Combina filtros

Creá una ruta `GET /usuarios/jovenes-activos` que devuelva usuarios menores de 25 años que estén activos.

<details>
<summary><b>Solución (reto)</b></summary>

```python
@app.route("/usuarios/jovenes-activos", methods=["GET"])
def get_jovenes_activos():
    usuarios = Usuario.query.filter(
        Usuario.edad < 25,
        Usuario.activo == True
    ).all()

    return jsonify([{
        "id": u.id,
        "nombre": u.nombre,
        "edad": u.edad,
        "activo": u.activo
    } for u in usuarios])
```

</details>

---

## 4. Búsqueda de patrones — LIKE e ILIKE (10 min)

LIKE es como un buscador de Google dentro de la base de datos. Es cuando querés encontrar algo que **contenga** un texto, sin necesidad de saber el texto exacto.

### 4A — LIKE

```python
# Buscar usuarios cuyo nombre contenga "Juan"
usuarios = Usuario.query.filter(
    Usuario.nombre.like("%Juan%")
).all()
```

**Sintaxis de LIKE:**

| Patrón | Significado | Ejemplo |
|--------|-------------|---------|
| `%texto%` | Contiene "texto" | `%Juan%` → "Juan", "Juan Carlos" |
| `texto%` | Empieza con "texto" | `Ju%` → "Juan", "Julia" |
| `%texto` | Termina con "texto" | `%an` → "Juan", "Sofían" |

**Ejemplos:**

```python
# Nombres que empiezan con "J"
usuarios = Usuario.query.filter(
    Usuario.nombre.like("J%")
).all()

# Nombres que terminan con "a"
usuarios = Usuario.query.filter(
    Usuario.nombre.like("%a")
).all()

# Correos que contienen "gmail"
usuarios = Usuario.query.filter(
    Usuario.correo.like("%gmail%")
).all()
```

---

### 4B — ILIKE (ignora mayúsculas)

```python
# Buscar "juan" sin importar mayúsculas/minúsculas
usuarios = Usuario.query.filter(
    Usuario.nombre.ilike("%juan%")
).all()
```

**ILIKE** es igual a LIKE pero **ignora mayúsculas y minúsculas**. Si buscás `%juan%`, con ILIKE también encuentra "Juan", "JUAN", "jUaN", etc.

**¿Cuándo usar ILIKE?** Casi siempre. Es más flexible y los usuarios no siempre escriben con las mayúsculas correctas.

---

### 4C — Reto: Buscador de usuarios

Creá una ruta `GET /usuarios/buscar?q=texto` que busque usuarios cuyo nombre contenga el texto enviado (case-insensitive).

<details>
<summary><b>Solución (reto)</b></summary>

```python
from flask import request

@app.route("/usuarios/buscar", methods=["GET"])
def buscar_usuarios():
    texto = request.args.get("q", "")

    if not texto:
        return jsonify({"error": "Debes enviar un parámetro 'q'"}), 400

    usuarios = Usuario.query.filter(
        Usuario.nombre.ilike(f"%{texto}%")
    ).all()

    return jsonify([{
        "id": u.id,
        "nombre": u.nombre,
        "edad": u.edad
    } for u in usuarios])
```

**Probá en Postman:**
- GET `http://127.0.0.1:5000/usuarios/buscar?q=ju` → Juan
- GET `http://127.0.0.1:5000/usuarios/buscar?q=AN` → Ana, Carmen
- GET `http://127.0.0.1:5000/usuarios/buscar?q=xyz` → Lista vacía

</details>

---

## 5. IN, NOT IN y BETWEEN (15 min)

Estos operadores son como hacer preguntas rápidas a la base de datos: "¿estás en este grupo?" o "¿estás en este rango?"

### 5A — IN (¿está en esta lista?)

```python
usuarios = Usuario.query.filter(
    Usuario.id.in_([1, 2, 3, 4])
).all()
```

**¿Qué hace?** Trae usuarios cuyo ID esté en la lista `[1, 2, 3, 4]`. Es como decir: "dame a Juan, Ana, Pedro y María" — los buscás por nombre.

---

### 5B — NOT IN (NO está en esta lista)

```python
usuarios = Usuario.query.filter(
    ~Usuario.id.in_([1, 2, 3])
).all()
```

**¿Qué hace?** Trae usuarios cuyo ID **NO** esté en la lista. El `~` significa "negación". Es como decir: "dame a todos MENOS Juan, Ana y Pedro".

---

### 5C — BETWEEN (¿está en este rango?)

```python
usuarios = Usuario.query.filter(
    Usuario.edad.between(18, 30)
).all()
```

**¿Qué hace?** Trae usuarios cuya edad esté **entre 18 y 30** (inclusivo). Es como decir: "dame a todos los que tengan entre 18 y 30 años".

---

### 5D — IS NULL / IS NOT NULL

```python
# Usuarios SIN correo
usuarios = Usuario.query.filter(
    Usuario.correo == None
).all()

# Usuarios CON correo
usuarios = Usuario.query.filter(
    Usuario.correo != None
).all()
```

**Nota:** En Python se usa `== None` y `!= None`, no `is None`. SQLAlchemy lo traduce automáticamente a `IS NULL` e `IS NOT NULL` en SQL.

---

### 5E — Reto: Filtrá por rango

Creá una ruta `GET /usuarios/rango?min=18&max=30` que devuelva usuarios en ese rango de edad.

<details>
<summary><b>Solución (reto)</b></summary>

```python
@app.route("/usuarios/rango", methods=["GET"])
def get_usuarios_rango():
    min_edad = request.args.get("min", type=int)
    max_edad = request.args.get("max", type=int)

    if min_edad is None or max_edad is None:
        return jsonify({"error": "Debes enviar parámetros 'min' y 'max'"}), 400

    usuarios = Usuario.query.filter(
        Usuario.edad.between(min_edad, max_edad)
    ).all()

    return jsonify([{
        "id": u.id,
        "nombre": u.nombre,
        "edad": u.edad
    } for u in usuarios])
```

**Probá en Postman:**
- GET `http://127.0.0.1:5000/usuarios/rango?min=18&max=25` → Juan, Pedro, Carlos, Carmen
- GET `http://127.0.0.1:5000/usuarios/rango?min=30&max=50` → Ana, Laura, Luis

</details>

---

## 6. Ordenar y limitar (15 min)

Estos métodos son como organizar una estantería: primero ordenás los libros como querés, y después podés sacar solo los primeros N.

### 6A — order_by() — Ordenar resultados

```python
# Orden ascendente (A → Z, 0 → 9)
usuarios = Usuario.query.order_by(Usuario.nombre).all()

# Orden descendente (Z → A, 9 → 0)
usuarios = Usuario.query.order_by(Usuario.edad.desc()).all()

# Múltiples ordenamientos
usuarios = Usuario.query.order_by(
    Usuario.edad.desc(),
    Usuario.nombre
).all()
```

**¿Cómo funciona?**
- Sin nada = ascendente (por defecto)
- `.desc()` = descendente
- Podés combinar varios campos: primero ordena por el primero, y si hay empates, ordena por el segundo

---

### 6B — limit() y offset() — Paginación

```python
# Los primeros 10 usuarios
usuarios = Usuario.query.limit(10).all()

# Saltar los primeros 20 y traer los siguientes 10
usuarios = Usuario.query.offset(20).limit(10).all()
```

**Analogía:** Imaginá un libro de 100 páginas.
- `limit(10)` = leer las primeras 10 páginas
- `offset(20)` = saltar las primeras 20 páginas
- `offset(20).limit(10)` = saltar 20 y leer las siguientes 10 (páginas 21-30)

**¿Para qué sirve?** Para cuando tenés muchos registros y querés mostrarlos de a poco. Como las páginas de Google: en vez de mostrarte todos los resultados de golpe, te muestra 10 por página.

---

### 6C — Paginación con Flask-SQLAlchemy

Flask-SQLAlchemy tiene un método especial para paginación que hace todo más fácil:

```python
@app.route("/usuarios/pagina", methods=["GET"])
def get_usuarios_paginados():
    pagina = Usuario.query.paginate(
        page=1,         # Página actual
        per_page=20,    # Usuarios por página
        error_out=False  # No lanzar error si la página no existe
    )

    return jsonify({
        "usuarios": [{
            "id": u.id,
            "nombre": u.nombre,
            "edad": u.edad
        } for u in pagina.items],
        "total_paginas": pagina.pages,
        "total_usuarios": pagina.total,
        "tiene_siguiente": pagina.has_next,
        "tiene_anterior": pagina.has_prev
    })
```

**¿Qué devuelve?**

| Atributo | Significado |
|----------|-------------|
| `pagina.items` | Los usuarios de esta página |
| `pagina.pages` | Total de páginas |
| `pagina.total` | Total de usuarios |
| `pagina.has_next` | ¿Hay página siguiente? |
| `pagina.has_prev` | ¿Hay página anterior? |

---

### 6D — Reto: Paginá los usuarios

Creá una ruta `GET /usuarios/pagina/<int:numero>` que devuelva 3 usuarios por página.

<details>
<summary><b>Solución (reto)</b></summary>

```python
@app.route("/usuarios/pagina/<int:numero>", methods=["GET"])
def get_pagina(numero):
    if numero < 1:
        return jsonify({"error": "El número de página debe ser mayor a 0"}), 400

    pagina = Usuario.query.paginate(
        page=numero,
        per_page=3,
        error_out=False
    )

    if not pagina.items:
        return jsonify({"mensaje": "No hay usuarios en esta página"}), 200

    return jsonify({
        "pagina": numero,
        "usuarios": [{
            "id": u.id,
            "nombre": u.nombre,
            "edad": u.edad
        } for u in pagina.items],
        "tiene_siguiente": pagina.has_next,
        "tiene_anterior": pagina.has_prev
    })
```

**Probá en Postman:**
- GET `http://127.0.0.1:5000/usuarios/pagina/1` → Primeros 3
- GET `http://127.0.0.1:5000/usuarios/pagina/2` → Siguientes 3
- GET `http://127.0.0.1:5000/usuarios/pagina/4` → "No hay usuarios en esta página"

</details>

---

## 7. Contar, verificar y seleccionar (15 min)

Estos métodos son las operaciones "especiales": contar registros, verificar si existe algo, o traer solo algunas columnas.

### 7A — count() — Contar registros

```python
# Total de usuarios
cantidad = Usuario.query.count()

# Usuarios activos
activos = Usuario.query.filter(Usuario.activo == True).count()
```

**¿Qué devuelve?** Un número entero. Es como decir: "¿cuántos usuarios hay?".

---

### 7B — Verificar si existe un registro

```python
existe = Usuario.query.filter_by(
    correo="juan@gmail.com"
).first() is not None
```

**¿Qué devuelve?** `True` o `False`.

La lógica es: intento buscar el usuario con `.first()`. Si lo encuentra, devuelve un objeto (que no es `None`), así que el resultado es `True`. Si no lo encuentra, devuelve `None`, así que el resultado es `False`.

---

### 7C — with_entities() — Seleccionar columnas específicas

```python
# Solo nombre y edad (no trae todo)
usuarios = Usuario.query.with_entities(
    Usuario.nombre,
    Usuario.edad
).all()
```

**¿Qué devuelve?** Una lista de **tuplas** en vez de objetos:

```python
[("Juan", 20), ("Ana", 30), ("Pedro", 25)]
```

**¿Para qué sirve?** Para cuando no necesitás todas las columnas. Es más eficiente pedir solo lo que necesitás.

---

### 7D — distinct() — Eliminar duplicados

```python
usuarios = Usuario.query.with_entities(
    Usuario.nombre
).distinct().all()
```

**¿Qué hace?** Trae solo valores únicos de nombre. Si hay dos "Juan", solo trae uno.

---

### 7E — Reto: Cuenta de usuarios activos

Creá una ruta `GET /usuarios/estadisticas` que devuelva:
- Total de usuarios
- Usuarios activos
- Usuarios inactivos

<details>
<summary><b>Solución (reto)</b></summary>

```python
@app.route("/usuarios/estadisticas", methods=["GET"])
def get_estadisticas():
    total = Usuario.query.count()
    activos = Usuario.query.filter(Usuario.activo == True).count()
    inactivos = total - activos

    return jsonify({
        "total": total,
        "activos": activos,
        "inactivos": inactivos
    })
```

</details>

---

## 8. Funciones SQL — Agregaciones (15 min)

Cuando necesitás hacer cálculos con los datos (suma, promedio, máximo, mínimo), SQLAlchemy tiene funciones que reemplazan las funciones SQL.

Primero importá `func`:

```python
from sqlalchemy import func
```

### 8A — Funciones de agregación

```python
# Edad máxima
edad_max = db.session.query(func.max(Usuario.edad)).scalar()

# Edad mínima
edad_min = db.session.query(func.min(Usuario.edad)).scalar()

# Promedio de edad
promedio = db.session.query(func.avg(Usuario.edad)).scalar()

# Suma de edades (poco común, pero sirve para ejemplo)
suma = db.session.query(func.sum(Usuario.edad)).scalar()

# Contar
cantidad = db.session.query(func.count(Usuario.id)).scalar()
```

**¿Qué hace `.scalar()`?** Devuelve directamente el valor (un número) en vez de una tupla. Es como desempacar el resultado.

---

### 8B — GROUP BY — Agrupar registros

```python
# Usuarios por cada edad
usuarios_por_edad = Usuario.query.with_entities(
    Usuario.edad,
    func.count(Usuario.id)
).group_by(
    Usuario.edad
).all()
```

**¿Qué devuelve?** Una lista de tuplas con la edad y la cantidad de usuarios con esa edad:

```python
[(15, 1), (17, 1), (19, 1), (20, 1), (22, 1), (25, 1), (28, 1), (30, 1), (35, 1), (40, 1)]
```

---

### 8C — GROUP BY + HAVING

```python
# Edades con más de 2 usuarios
edades_populares = Usuario.query.with_entities(
    Usuario.edad,
    func.count(Usuario.id)
).group_by(
    Usuario.edad
).having(
    func.count(Usuario.id) > 2
).all()
```

**¿Qué hace `having`?** Es como un `WHERE` pero para resultados agrupados. Filtra después de agrupar.

---

## 9. JOIN — Unir tablas (20 min)

En el día 1 vimos JOINs con SQL manual. Ahora vamos a hacer lo mismo pero con SQLAlchemy. Es como unir dos hojas de cálculo por una columna en común.

### 9A — join() — INNER JOIN

Supongamos que tenemos un modelo `Pedido` relacionado con `Usuario`:

```python
class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    producto = db.Column(db.String(100))
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
```

Para traer todos los usuarios que tienen pedidos:

```python
usuarios = Usuario.query.join(Pedido).all()
```

**¿Qué hace?** Solo trae usuarios que tengan **al menos un pedido**. Los usuarios sin pedidos no aparecen.

---

### 9B — outerjoin() — LEFT JOIN

```python
usuarios = Usuario.query.outerjoin(Pedido).all()
```

**¿Qué hace?** Trae **todos** los usuarios, incluyendo los que no tienen pedidos. Los que no tengan pedidos tendrán `None` en los campos del pedido.

**Comparación:**

| Método | SQL | ¿Qué trae? |
|--------|-----|-------------|
| `.join()` | INNER JOIN | Solo registros con coincidencia |
| `.outerjoin()` | LEFT JOIN | Todos los registros, con o sin coincidencia |

---

## 10. Encadenar consultas (15 min)

Una de las cosas más lindas de SQLAlchemy es que podés **encadenar** métodos uno tras otro. Es como construir una oración: primero digo qué quiero, luego filtro, luego ordeno, y así.

```python
usuarios = (
    Usuario.query
    .filter(Usuario.activo == True)    # Solo activos
    .filter(Usuario.edad > 18)         # Mayores de 18
    .order_by(Usuario.nombre)          # Ordenados por nombre
    .limit(10)                         # Máximo 10
    .all()                             # Ejecutar
)
```

**¿Qué hace esto?** Es como decir: "dame los primeros 10 usuarios activos mayores de 18, ordenados por nombre".

**Regla:** Poné `.all()`, `.first()`, `.one()` o `.count()` **al final**. Estos métodos son los que ejecutan la consulta. Todo lo demás es construir la consulta.

```python
# ❌ MAL - ejecuta antes de terminar de construir
usuarios = Usuario.query.filter(Usuario.edad > 18).all()
usuarios = usuarios.filter(Usuario.activo == True)  # ERROR: lista no tiene .filter()

# ✅ BIEN - construir primero, ejecutar al final
usuarios = Usuario.query.filter(Usuario.edad > 18).filter(Usuario.activo == True).all()
```

---

### 10A — Reto: Consulta encadenada

Creá una ruta `GET /usuarios/activos-mayores` que devuelva usuarios activos mayores de 18, ordenados por edad descendente, límite de 5.

<details>
<summary><b>Solución (reto)</b></summary>

```python
@app.route("/usuarios/activos-mayores", methods=["GET"])
def get_activos_mayores():
    usuarios = (
        Usuario.query
        .filter(Usuario.activo == True)
        .filter(Usuario.edad > 18)
        .order_by(Usuario.edad.desc())
        .limit(5)
        .all()
    )

    return jsonify([{
        "id": u.id,
        "nombre": u.nombre,
        "edad": u.edad,
        "activo": u.activo
    } for u in usuarios])
```

</details>

---

## 11. INSERT — Crear registros (25 min)

Hasta ahora solo leemos datos de la base de datos. Ahora vamos a **escribir** datos nuevos. Es como pasar de solo mirar el menú a empezar a cocinar.

### 11A — Crear un registro nuevo

```python
# Crear un nuevo usuario
nuevo_usuario = Usuario(
    nombre="Roberto",
    edad=28,
    correo="roberto@gmail.com",
    activo=True
)

db.session.add(nuevo_usuario)   # Agregar a la sesión
db.session.commit()             # Guardar en la base de datos
```

**¿Qué hace cada línea?**

| Línea | Significado |
|-------|-------------|
| `Usuario(...)` | Creo un objeto de Python (todavía NO existe en la BD) |
| `db.session.add(nuevo_usuario)` | Le digo a SQLAlchemy: "agate este objeto" |
| `db.session.commit()` | Ejecuto todo: el INSERT se envía a PostgreSQL |

**Analogía:** `db.session.add()` es como poner algo en la caja del supermercado. `db.session.commit()` es como pagar en la caja. Hasta que no pagues, el producto no es tuyo.

---

### 11B — Crear y acceder al ID generado

Cuando creás un registro, SQLAlchemy asigna un ID automáticamente. Podés acceder a él después del commit:

```python
nuevo_usuario = Usuario(
    nombre="Roberto",
    edad=28,
    correo="roberto@gmail.com",
    activo=True
)

db.session.add(nuevo_usuario)
db.session.commit()

# Ahora tiene el ID que le asignó la BD
print(nuevo_usuario.id)  # Por ejemplo: 11
```

**¿Por qué funciona?** Porque después del `commit()`, SQLAlchemy actualiza el objeto con los datos que la BD generó (como el ID automático).

---

### 11C — Crear varios registros de una vez

```python
usuarios_nuevos = [
    Usuario(nombre="Laura", edad=22, correo="laura@gmail.com", activo=True),
    Usuario(nombre="Pedro", edad=35, correo="pedro@gmail.com", activo=True),
    Usuario(nombre="Sofía", edad=19, correo="sofia@gmail.com", activo=False),
]

db.session.add_all(usuarios_nuevos)
db.session.commit()
```

**¿Para qué sirve?** Para cuando necesitás crear muchos registros de golpe. Es más eficiente que hacer un `add()` y `commit()` por cada uno.

---

### 11D — Reto: Creá un usuario

Creá una ruta `POST /usuarios` que reciba JSON con nombre, edad, correo y activo, y cree un usuario nuevo.

<details>
<summary><b>Solución (reto)</b></summary>

```python
from flask import request

@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    datos = request.json

    if not datos:
        return jsonify({"error": "Debes enviar datos en formato JSON"}), 400

    if "nombre" not in datos or not str(datos.get("nombre", "")).strip():
        return jsonify({"error": "Falta el campo: nombre"}), 400

    nuevo_usuario = Usuario(
        nombre=datos["nombre"],
        edad=datos.get("edad"),
        correo=datos.get("correo"),
        activo=datos.get("activo", True)
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "edad": nuevo_usuario.edad,
        "correo": nuevo_usuario.correo,
        "activo": nuevo_usuario.activo
    }), 201
```

**Probá en Postman:**
- Método: POST
- URL: `http://127.0.0.1:5000/usuarios`
- Body → raw → JSON:

```json
{
    "nombre": "Roberto",
    "edad": 28,
    "correo": "roberto@gmail.com",
    "activo": true
}
```

- Send → Deberías ver el usuario creado con código 201

</details>

---

## 12. UPDATE — Actualizar registros (20 min)

Actualizar es como modificar algo que ya existe. En vez de borrar y volver a crear, solo cambiamos lo que necesitamos.

### 12A — Actualizar un registro existente

```python
# 1. Buscar el usuario
usuario = Usuario.query.get(1)

# 2. Modificar los campos
usuario.nombre = "Juan Carlos"
usuario.edad = 21

# 3. Guardar cambios
db.session.commit()
```

**¿Qué hace?** SQLAlchemy detecta automáticamente qué cambió y genera el `UPDATE` correspondiente. No necesitás escribir SQL.

**Analogía:** Es como encontrar un archivo en tu escritorio y modificarlo. Solo cambias lo que necesitás y guardás.

---

### 12B — Actualizar con validación

```python
@app.route("/usuarios/<int:id>", methods=["PUT"])
def actualizar_usuario(id):
    usuario = Usuario.query.get(id)

    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    datos = request.json

    # Solo actualizo los campos que me manden
    usuario.nombre = datos.get("nombre", usuario.nombre)
    usuario.edad = datos.get("edad", usuario.edad)
    usuario.correo = datos.get("correo", usuario.correo)
    usuario.activo = datos.get("activo", usuario.activo)

    db.session.commit()

    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "edad": usuario.edad,
        "correo": usuario.correo,
        "activo": usuario.activo
    })
```

**¿Por qué `datos.get("nombre", usuario.nombre)`?** Porque si el usuario no manda el campo "nombre", mantengo el valor que ya tenía. Es como decir: "cambiá esto SOLO si me mandás un valor nuevo".

---

### 12C — Actualizar varios registros de una vez

```python
# Desactivar todos los usuarios mayores de 40
Usuario.query.filter(Usuario.edad > 40).update({"activo": False})
db.session.commit()
```

**¿Qué hace?** Actualiza **todos** los usuarios mayores de 40, poniendo `activo = False`. Es como hacer un UPDATE masivo sin necesidad de buscar uno por uno.

---

### 12D — Reto: Actualizá un usuario

Creá una ruta `PATCH /usuarios/<int:id>/edad` que reciba una nueva edad y actualice solo ese campo.

<details>
<summary><b>Solución (reto)</b></summary>

```python
@app.route("/usuarios/<int:id>/edad", methods=["PATCH"])
def actualizar_edad(id):
    usuario = Usuario.query.get(id)

    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    datos = request.json

    if "edad" not in datos:
        return jsonify({"error": "Debes enviar el campo 'edad'"}), 400

    usuario.edad = datos["edad"]
    db.session.commit()

    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "edad": usuario.edad
    })
```

**¿Por qué PATCH y no PUT?** Porque PUT reemplaza todo el recurso, y PATCH actualiza solo campos específicos. En la práctica, muchos usan PUT para ambos casos.

</details>

---

## 13. DELETE — Eliminar registros (20 min)

Eliminar es la operación más peligrosa: una vez que borras algo, no hay vuelta atrás (a menos que tengas backup). Es como quemar una receta: si no la tenés escrita en otro lado, se pierde para siempre.

### 13A — Eliminar un registro

```python
# 1. Buscar el usuario
usuario = Usuario.query.get(1)

# 2. Eliminarlo
db.session.delete(usuario)

# 3. Guardar cambios
db.session.commit()
```

**Analogía:** Primero encontrás el archivo (query), lo tirás a la papelera (delete), y vaciás la papelera (commit).

---

### 13B — Eliminar con verificación

```python
@app.route("/usuarios/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):
    usuario = Usuario.query.get(id)

    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    nombre = usuario.nombre  # Guardo el nombre antes de borrar

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({
        "mensaje": f"Usuario '{nombre}' eliminado correctamente"
    })
```

**¿Por qué guardo el nombre antes de borrar?** Porque después de `db.session.delete()`, el objeto ya no existe. Si intento acceder a `usuario.nombre` después del `commit()`, tendré un error.

---

### 13C — Eliminar varios registros de una vez

```python
# Eliminar todos los usuarios inactivos
Usuario.query.filter(Usuario.activo == False).delete()
db.session.commit()
```

**¿Qué hace?** Elimina **todos** los usuarios que estén inactivos. Es como hacer una limpieza masiva.

**⚠️ ¡Cuidado!** Esto elimina muchos registros de golpe. Siempre verificá cuántos registros van a afectarse antes de ejecutar:

```python
# Primero cuento
cantidad = Usuario.query.filter(Usuario.activo == False).count()
print(f"Se van a eliminar {cantidad} usuarios")

# Luego elimino (si estoy seguro)
Usuario.query.filter(Usuario.activo == False).delete()
db.session.commit()
```

---

### 13D — Reto: Eliminá un usuario

Creá una ruta `DELETE /usuarios/<int:id>` que elimine un usuario y devuelva un mensaje de confirmación.

<details>
<summary><b>Solución (reto)</b></summary>

```python
@app.route("/usuarios/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):
    usuario = Usuario.query.get(id)

    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    nombre = usuario.nombre

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({
        "mensaje": f"Usuario '{nombre}' eliminado correctamente"
    })
```

**Probá en Postman:**
- Método: DELETE
- URL: `http://127.0.0.1:5000/usuarios/1`
- Send → Deberías ver el mensaje de confirmación

</details>

---

## 14. Resumen del CRUD completo (10 min)

Ahora que sabemos SELECT, INSERT, UPDATE y DELETE, tenemos el **CRUD completo**. CRUD significa **C**reate, **R**ead, **U**pdate, **D**elete — las 4 operaciones básicas que todo sistema necesita.

### Comparación: psycopg2 vs Flask-SQLAlchemy

| Operación | psycopg2 (SQL manual) | Flask-SQLAlchemy (ORM) |
|-----------|----------------------|------------------------|
| **CREATE** | `cur.execute("INSERT INTO usuarios ...")` | `db.session.add(usuario)` |
| **READ** | `cur.execute("SELECT * FROM usuarios")` | `Usuario.query.all()` |
| **UPDATE** | `cur.execute("UPDATE usuarios SET ...")` | `usuario.nombre = "nuevo"` |
| **DELETE** | `cur.execute("DELETE FROM usuarios ...")` | `db.session.delete(usuario)` |
| **Guardar** | `conn.commit()` | `db.session.commit()` |

---

### Rutas del CRUD completo

Acá tenés todas las rutas juntas para tu app de usuarios:

```python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost:5432/musica_peruana"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    edad = db.Column(db.Integer)
    correo = db.Column(db.String(100))
    activo = db.Column(db.Boolean)


# =============================================================
# READ — Obtener todos
# =============================================================
@app.route("/usuarios", methods=["GET"])
def get_usuarios():
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    return jsonify([{
        "id": u.id,
        "nombre": u.nombre,
        "edad": u.edad,
        "correo": u.correo,
        "activo": u.activo
    } for u in usuarios])


# =============================================================
# READ — Obtener uno
# =============================================================
@app.route("/usuarios/<int:id>", methods=["GET"])
def get_usuario(id):
    usuario = Usuario.query.get(id)

    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "edad": usuario.edad,
        "correo": usuario.correo,
        "activo": usuario.activo
    })


# =============================================================
# CREATE — Crear uno
# =============================================================
@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    datos = request.json

    if not datos:
        return jsonify({"error": "Debes enviar datos en formato JSON"}), 400

    if "nombre" not in datos or not str(datos.get("nombre", "")).strip():
        return jsonify({"error": "Falta el campo: nombre"}), 400

    nuevo_usuario = Usuario(
        nombre=datos["nombre"],
        edad=datos.get("edad"),
        correo=datos.get("correo"),
        activo=datos.get("activo", True)
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "edad": nuevo_usuario.edad,
        "correo": nuevo_usuario.correo,
        "activo": nuevo_usuario.activo
    }), 201


# =============================================================
# UPDATE — Actualizar uno
# =============================================================
@app.route("/usuarios/<int:id>", methods=["PUT"])
def actualizar_usuario(id):
    usuario = Usuario.query.get(id)

    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    datos = request.json
    usuario.nombre = datos.get("nombre", usuario.nombre)
    usuario.edad = datos.get("edad", usuario.edad)
    usuario.correo = datos.get("correo", usuario.correo)
    usuario.activo = datos.get("activo", usuario.activo)

    db.session.commit()

    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "edad": usuario.edad,
        "correo": usuario.correo,
        "activo": usuario.activo
    })


# =============================================================
# DELETE — Eliminar uno
# =============================================================
@app.route("/usuarios/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):
    usuario = Usuario.query.get(id)

    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    nombre = usuario.nombre

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({
        "mensaje": f"Usuario '{nombre}' eliminado correctamente"
    })


if __name__ == "__main__":
    app.run(debug=True)
```

---

## ⚡ psycopg2 vs Flask-SQLAlchemy — ¿Cuándo usar cada uno?

| Situación | psycopg2 | Flask-SQLAlchemy |
|-----------|-----------|------------------|
| Queries simples | ✅ Funciona | ✅ Recomendado |
| Queries complejas con SQL | ✅ Ideal | ⚠️ A veces necesitás raw SQL |
| Velocidad pura | ✅ Más rápido | ⚠️ Un poco más lento |
| Seguridad (SQL injection) | ⚠️ Manual con `%s` | ✅ Automático |
| Legibilidad | ⚠️ Strings SQL largos | ✅ Código Python limpio |
| Portabilidad entre BDs | ❌ Solo PostgreSQL | ✅ Funciona con cualquier BD |
| Bootcamp / Proyectos reales | ⚠️ Solo para queries específicas | ✅ **Estándar de la industria** |

---

## ¿Qué sigue?

Mañana veremos:
- **Relaciones 1:N y N:M** — cómo modelar datos relacionados entre tablas
- **Validaciones avanzadas** — asegurar que los datos sean correctos antes de guardarlos
- **Manejo de errores** — qué pasa cuando algo sale mal en la BD

¡Nos vemos mañana! 🎵
