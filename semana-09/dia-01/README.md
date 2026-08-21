# Guía — Día 1 (Semana 9): Levantando el proyecto de Django 🎬

## Objetivo de la sesión

Cambiar de framework: después de 4 semanas de Flask, hoy los alumnos crean su primer proyecto Django y comprueban que muchas cosas que construyeron a mano ahora vienen incluidas:

- Crear el proyecto y entender la anatomía (`manage.py`, `settings.py`)
- Tour por `settings.py`: qué controla cada clave — partimos con **SQLite**
- Modelos con el ORM de Django: **tipos de campo**, opciones de columna y el método `__str__`
- Relaciones: `ForeignKey` y `ManyToMany` (`Categoria`, `Etiqueta`, `Producto`)
- Primera migración: `makemigrations`, `migrate`, `sqlmigrate`, `showmigrations` (revertir solo mencionado)
- Panel de administración nativo + **Jazzmin** como cierre motivador

## Mapa de la sesión

| Bloque | Contenido | Tiempo |
|--------|-----------|--------|
| 0 | De Flask a Django: el cambio de filosofía | 10 min |
| 1 | Creación del proyecto: venv, `startproject`, anatomía | 20 min |
| 2 | `settings.py` por dentro (SQLite incluido) | 25 min |
| 3 | La app `tienda`: `startapp` + `INSTALLED_APPS` | 10 min |
| 4 | Modelos: tipos de campo, opciones, `__str__` y relaciones | 45 min |
| 5 | Migraciones: crear, ver SQL, listar, revertir | 20 min |
| 6 | Admin + superuser + Jazzmin | 25 min |

---

## 0. De Flask a Django (10 min)

Arrancar con la comparación — ellos ya saben Flask, eso es una ventaja:

| Concepto | En Flask (semanas 6-8) | En Django |
|----------|------------------------|-----------|
| Filosofía | Microframework: vos armás todo | "Batteries included": trae casi todo |
| Configuración | Dispersa (`.env`, `app.py`) | Centralizada en `settings.py` |
| ORM | SQLAlchemy (externo) | Incluido y acoplado al framework |
| Migraciones | Flask-Migrate (Alembic) | Sistema propio integrado |
| Panel admin | No existe — lo hubiéramos escrito a mano | **Incluido**, gratis |
| Serialización | Pydantic | Serializers (mañana en DRF) |

**Mensaje clave del día:** en Flask nosotros construimos el e-commerce pieza por pieza. Django ya trae varias de esas piezas de fábrica. Hoy vamos a comprobarlo.

---

## 1. Creación del proyecto (20 min)

### Preparar el entorno

```bash
mkdir django-tienda
cd django-tienda
python -m venv venv
venv\Scripts\activate
```

`requirements.txt`:

```
Django~=5.2.0
django-jazzmin==3.0.5
```

```bash
pip install -r requirements.txt
```

> `~=5.2.0` significa "cualquier parche de la serie 5.2" — es la versión LTS, con soporte hasta 2028. No usamos Django 6 porque LTS = estabilidad para aprender.

### Crear el proyecto

```bash
django-admin startproject config .
```

**El punto final importa**: sin él, Django crea una carpeta doble `config/config`. Con el punto, todo queda en la raíz.

### Qué generó

```
django-tienda/
├── config/
│   ├── __init__.py      → marca config como paquete Python
│   ├── settings.py      → configuración central del proyecto
│   ├── urls.py          → rutas de entrada del proyecto
│   ├── asgi.py          → entrada async (deploy moderno)
│   └── wsgi.py          → entrada sync (deploy clásico)
└── manage.py            → CLI de tareas del proyecto
```

Aclarar: `config` es solo un nombre — se llama así por convención para dejar claro que es configuración, no lógica de negocio.

---

## 2. settings.py por dentro (25 min)

Analogía sugerida: `settings.py` es el **cuadro eléctrico de la casa**. No lo abrís todos los días, pero todo lo que la casa hace pasa por ahí.

Recorrer la tabla completa en vivo, abriendo el archivo real:

| Clave | Qué controla | ¿La tocamos hoy? |
|-------|--------------|------------------|
| `DEBUG` | Mostrar errores detallados. NUNCA en producción | Solo la comentamos |
| `ALLOWED_HOSTS` | Qué dominios pueden servir la app | No (con DEBUG=True basta localhost) |
| `INSTALLED_APPS` | Las apps activas del proyecto | **SÍ** — agregamos `jazzmin` y `tienda` |
| `MIDDLEWARE` | Filtros por los que pasa cada request | No (solo nombrar) |
| `ROOT_URLCONF` | Dónde está el urls.py raíz | No |
| `TEMPLATES` | Motor de plantillas HTML | No |
| `DATABASES` | Conexión a la base de datos | **La miramos** — ya viene con SQLite |
| `AUTH_PASSWORD_VALIDATORS` | Reglas de contraseñas del admin | No |
| `STATIC_URL` | Ruta de archivos estáticos | No |
| `DEFAULT_AUTO_FIELD` | Tipo de ID automático (BigAutoField) | No |
| `LANGUAGE_CODE` | Idioma de la interfaz admin | **SÍ** — `'es'` |
| `TIME_ZONE` | Zona horaria | **SÍ** — `'America/Lima'` |

### La base de datos: SQLite por defecto

Mostrar el bloque que ya viene en `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Puntos a explicar:

1. **SQLite es una base de datos en UN archivo** (`db.sqlite3`, aparecerá en la raíz cuando migremos). Cero instalación, cero credenciales, cero servidor. Perfecta para aprender y desarrollar.
2. Cambiar de motor en Django es editar ESTE diccionario y nada más. Adelantar el bloque que usaremos más adelante con PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_tienda',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

> Mensaje para la clase: hoy aprendemos Django sin fricción con SQLite. El día que necesitemos PostgreSQL, el cambio es solo este bloque — el resto del código NO se toca. Esa es la ventaja del ORM.

Y arriba del todo, ponerlo en español:

```python
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Lima'
```

---

## 3. La app tienda (10 min)

Concepto nuevo: **proyecto vs app**. El proyecto es el centro comercial; las apps son las tiendas. Una app agrupa modelos, vistas y rutas de UN dominio de negocio.

```bash
python manage.py startapp tienda
```

Genera:

```
tienda/
├── __init__.py
├── admin.py       → registro de modelos para el panel admin
├── apps.py        → configuración de la app
├── migrations/    → historial de migraciones de ESTA app
├── models.py      → los modelos del ORM
├── tests.py
└── views.py       → las vistas (la lógica)
```

Registrarla en `INSTALLED_APPS` (y de paso Jazzmin, que usaremos al final):

```python
INSTALLED_APPS = [
    'jazzmin',                  # SIEMPRE antes de django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'tienda',                   # nuestra app
]
```

> Si `jazzmin` no va primero, el admin carga pero sin el tema. Es el error clásico.

---

## 4. Modelos: tipos de campo, opciones, __str__ y relaciones (45 min)

Bloque central del día. Ir construyendo el archivo por partes, explicando CADA tipo de campo antes de escribirlo.

### 4A — Anatomía de un modelo

Un modelo es una clase Python que hereda de `models.Model`. Cada atributo de clase = una columna de la tabla. Django genera además el `id` automáticamente (BigAutoField) — no se escribe.

### 4B — Los tipos de campo

Tabla para explicar ANTES de codificar. Conectar cada uno con lo que ya usaron en SQLAlchemy:

| Campo | Para qué | Equivalente SQLAlchemy |
|-------|----------|------------------------|
| `CharField(max_length=80)` | Texto corto con límite: nombres, códigos | `String(80)` |
| `TextField()` | Texto largo sin límite fijo: descripciones | `Text` |
| `IntegerField()` | Enteros con signo | `Integer` |
| `PositiveIntegerField()` | Enteros ≥ 0 | `Integer` + check |
| `DecimalField(max_digits=10, decimal_places=2)` | Números EXACTOS con decimales: **dinero** | `Numeric` |
| `FloatField()` | Decimales aproximados: medidas, ciencia — NUNCA dinero | `Float` |
| `BooleanField()` | Verdadero / Falso | `Boolean` |
| `DateTimeField(auto_now_add=True)` | Fecha y hora automática AL CREAR | `server_default=func.now()` |
| `DateTimeField(auto_now=True)` | Fecha y hora automática AL MODIFICAR | `onupdate=func.now()` |
| `URLField(blank=True)` | Texto que valida ser URL | `String` + validación |
| `EmailField()` | Texto que valida email | `String` + validación |
| `SlugField()` | texto-con-guiones para URLs | `String` |

Regla de oro que refuerza la semana 8: **el dinero va en `DecimalField`**. En Flask usamos `Float` para el precio; acá corregimos la mala costumbre — float tiene errores de redondeo.

### 4C — Las opciones de columna

Todo campo acepta opciones. Las que usaremos hoy:

| Opción | Qué hace |
|--------|----------|
| `max_length=80` | Límite de caracteres — OBLIGATORIO en CharField |
| `unique=True` | No se repite en toda la tabla |
| `default=True` | Valor si nadie indica uno |
| `blank=True` | Permite vacío en la VALIDACIÓN (formularios/serializers) |
| `null=True` | Acepta NULL en la BASE DE DATOS |
| `auto_now_add=True` | Estampa fecha/hora al crear, no se puede editar |

> **Nota `null` vs `blank`** (pregunta típica de examen): `null=True` afecta la BD; `blank=True` afecta la validación. Para textos opcionales lo idiomático es `blank=True` sin `null` — Django guarda `''`.

### 4D — Construir Categoria, línea por línea

```python
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
```

Narrar cada línea: nombre corto con límite y único; descripción larga opcional; flag de estado con default; fecha automática de creación.

### 4E — __str__: la credencial del objeto

```python
    def __str__(self):
        return self.nombre
```

Explicar el problema que resuelve: sin `__str__`, cualquier objeto se imprime como `<Categoria: Categoria object (1)>` — técnicamente cierto, humanamente inútil. Con `__str__`, se muestra `Lácteos`.

¿Dónde aparece?

- **En el admin**: listados y desplegables (al elegir categoría de un producto verás nombres, no "object (3)")
- **En el shell**: `python manage.py shell` e imprimir objetos
- **En logs y prints**

Regla: TODO modelo lleva `__str__` devolviendo algo legible.

### 4F — Relaciones

Primero la app simple, `Etiqueta`:

```python
class Etiqueta(models.Model):
    nombre = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.nombre
```

Luego `Producto` con las dos relaciones:

```python
class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    codigo = models.CharField(max_length=12, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos',
    )
    etiquetas = models.ManyToManyField(
        Etiqueta,
        blank=True,
        related_name='productos',
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'
```

**ForeignKey (uno a muchos)**: un producto pertenece a UNA categoría; una categoría tiene MUCHOS productos.

- `on_delete`: qué pasa con los productos si alguien borra la categoría —

| Opción | Qué pasa | Cuándo usarla |
|--------|----------|---------------|
| `CASCADE` | Borra TODOS sus productos | Datos verdaderamente dependientes |
| `PROTECT` | **Bloquea** el borrado con error | Historial que no se puede romper |
| `SET_NULL` | Pone `categoria_id = NULL` (requiere `null=True`) | El producto sigue existiendo sin categoría |

Elegimos `PROTECT`: misma filosofía del borrado lógico de la semana 8.

- `related_name='productos'`: permite navegar del padre a los hijos: `categoria.productos.all()`. Es el backref de SQLAlchemy.

**ManyToMany (muchos a muchos)**: un producto puede tener muchas etiquetas y una etiqueta vive en muchos productos. Django crea la TABLA INTERMEDIA solo — en Flask la armábamos a mano. `blank=True` = opcional.

**class Meta**: metadatos del modelo — `ordering` define el orden por defecto de los listados; `verbose_name_plural` corrige plurales en el admin (agregarlo en Categoria: `'categorías'`).

### Archivo completo final

`tienda/models.py` debe quedar con los tres modelos en ese orden: `Categoria`, `Etiqueta`, `Producto`.

---

## 5. Migraciones (20 min)

### Generar y aplicar

```bash
python manage.py makemigrations tienda
python manage.py migrate
```

Dos comandos, dos momentos distintos (igual que Flask-Migrate, pero aquí son nativos):

| Comando | Qué hace | Toca la BD? |
|---------|----------|-------------|
| `makemigrations` | Genera archivos de migración en `tienda/migrations/` | NO |
| `migrate` | Ejecuta esas migraciones contra la BD | SÍ |

Después de `migrate` van a ver MUCHAS tablas creadas — no solo las nuestras. Son las apps builtin (`auth`, `sessions`, `admin`...) que también tienen modelos. Buen momento para conectar con `INSTALLED_APPS`. Y en la raíz apareció el archivo `db.sqlite3` — nuestra base de datos entera vive ahí.

### Anatomía de una migración

Abrir `tienda/migrations/0001_initial.py` y mostrar (versión resumida):

```python
class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=80, unique=True)),
                ...
            ],
        ),
        migrations.AddField(
            model_name='producto',
            name='categoria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, ...),
        ),
    ]
```

Concepto clave: una migración es código Python versionado, como un commit de git pero para la estructura de la BD.

### Ver el SQL real

```bash
python manage.py sqlmigrate tienda 0001
```

Imprime el `CREATE TABLE ...` que se ejecutó (sintaxis SQLite). Ideal para conectar con la semana de SQL puro.

### Listar y revertir (mención rápida)

```bash
python manage.py showmigrations tienda
```

```
 [X] 0001_initial
```

Revertir (SOLO demostrarlo, no como práctica de hoy):

```bash
python manage.py migrate tienda 0001   # retrocede a la 0001
python manage.py migrate tienda zero   # deshace TODO
```

> Advertencia para la clase: revertir borra datos de las columnas/tablas afectadas. Es la "máquina del tiempo" de la estructura, no de los datos.

---

## 6. Admin + superuser + Jazzmin (25 min)

### El momento que Flask nunca nos dio

En Flask, un panel de administración habría sido OTRO proyecto. Django lo trae. Solo necesita usuarios y tablas — que ya tenemos.

```bash
python manage.py createsuperuser
```

Pedir usuario, email y contraseña. Entrar a `http://127.0.0.1:8000/admin/` y mostrar el panel pelado (en inglés si aún no guardaron settings).

### Registrar los modelos

En `tienda/admin.py`:

```python
from django.contrib import admin
from .models import Categoria, Etiqueta, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    list_per_page = 20


@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'precio', 'stock', 'categoria', 'activo')
    list_filter = ('activo', 'categoria')
    search_fields = ('nombre', 'codigo')
    filter_horizontal = ('etiquetas',)
```

Desglose rápido:

- `list_display`: columnas visibles en el listado
- `list_filter`: filtros laterales
- `search_fields`: casilla de búsqueda
- `filter_horizontal`: la relación M2M con selector doble (sin esto sería un multiselect feo)

Crear 2 categorías y 3 productos DESDE EL ADMIN. Fijarse cómo el listado muestra el `__str__` de cada modelo — la credencial que definimos en el bloque anterior. CRUD completo sin escribir una línea.

### Jazzmin: el traje nuevo

Ya está instalado y registrado (bloque 3). Agregar al FINAL de `settings.py`:

```python
JAZZMIN_SETTINGS = {
    "site_title": "Tienda Admin",
    "site_header": "Tienda",
    "site_brand": "E-commerce Django",
    "welcome_sig": "Panel de administración",
    "copyright": "Curso Python 2026",
    "show_theme_chooser": True,
}
```

Refrescar `/admin/`. Mismo panel, otro planeta. Dejar que prueben temas con el selector.

**Cierre de la sesión:** en Flask tardamos DOS SEMANAS en tener modelos + migraciones + panel de gestión. Hoy lo hicieron en una clase. ESE es el valor de Django.

---

## Comandos del día

| Comando | Para qué |
|---------|----------|
| `django-admin startproject config .` | Crear el proyecto |
| `python manage.py startapp tienda` | Crear una app |
| `python manage.py runserver` | Levantar el servidor |
| `python manage.py makemigrations tienda` | Generar migraciones |
| `python manage.py migrate` | Aplicar migraciones |
| `python manage.py sqlmigrate tienda 0001` | Ver el SQL de una migración |
| `python manage.py showmigrations` | Listar migraciones aplicadas |
| `python manage.py createsuperuser` | Crear usuario admin |

## Resumen de conceptos

| Tema | Conceptos clave |
|------|-----------------|
| Proyecto vs App | Proyecto = centro comercial, app = tienda. `startproject` una vez, `startapp` por dominio |
| settings.py | Cuadro eléctrico: INSTALLED_APPS, DATABASES, LANGUAGE_CODE/TIME_ZONE |
| SQLite | BD en un archivo (`db.sqlite3`); cambiar a PostgreSQL = editar el dict DATABASES |
| Tipos de campo | CharField corto, TextField largo, DecimalField para dinero, DateTimeField fechas |
| Opciones de columna | max_length, unique, default, blank (validación) vs null (BD) |
| `__str__` | La credencial del objeto; sin ella: "Categoria object (1)" |
| ForeignKey | 1 a muchos; `on_delete=PROTECT`, `related_name` para navegar al revés |
| ManyToMany | Muchos a muchos; Django crea la tabla intermedia solo |
| Migraciones | makemigrations genera, migrate aplica, sqlmigrate muestra SQL |
| Admin | `createsuperuser` + `@admin.register` + ModelAdmin options |
| Jazzmin | Va ANTES de `django.contrib.admin` en INSTALLED_APPS |
