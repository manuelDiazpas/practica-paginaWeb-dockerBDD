# 🌿 MercadoVerde — Lista de Compra Personal

> Aplicación web full-stack desarrollada con **Flask** y **MySQL** desplegada mediante **Docker**, que permite a los usuarios gestionar su lista de la compra de forma personal, segura y organizada. Cada usuario accede con sus credenciales y visualiza únicamente sus propios productos.

---

## 📋 Tabla de Contenidos

- [Tecnologías utilizadas](#-tecnologías-utilizadas)
- [Arquitectura del proyecto](#-arquitectura-del-proyecto)
- [Requisitos](#-requisitos)
- [Instalación y Arranque](#-instalación-y-arranque)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Base de Datos](#-base-de-datos)
- [Funcionalidades](#-funcionalidades)
- [Rutas de la API Flask](#-rutas-de-la-api-flask)
- [Seguridad OWASP](#-seguridad-owasp)
- [Pruebas con Postman](#-pruebas-con-postman)
- [Integración Continua con GitHub Actions](#-integración-continua-con-github-actions)

---

## 🛠️ Tecnologías utilizadas

| Capa              | Tecnología                        |
| ----------------- | --------------------------------- |
| Backend           | Python 3.13 + Flask               |
| Base de datos     | MySQL 8                           |
| Administración BD | phpMyAdmin                        |
| Contenedores      | Docker                            |
| Frontend          | HTML5 + CSS3 + JavaScript vanilla |
| CI/CD             | GitHub Actions                    |
| Testing           | Postman                           |

---

## 🏗️ Arquitectura del proyecto

La aplicación sigue una arquitectura de **tres capas** desplegada completamente en Docker:

```
┌─────────────────────────────────────────────────────┐
│                   Red Docker                        │
│               mi-red-lista-compra                   │
│                                                     │
│  ┌──────────────┐    ┌─────────────────────────┐    │
│  │  flask-app   │    │    mysql-contenedor     │    │
│  │  :5000       │───►│    :5432 → 3306         │    │
│  │  (Frontend   │    │    (Base de datos)      │    │
│  │  + Backend)  │    └─────────────────────────┘    │
│  └──────────────┘                                   │
│                      ┌─────────────────────────┐    │
│                      │  contenedor-phpmyadmin  │    │
│                      │  :8080 → 80             │    │
│                      │  (Admin panel)          │    │
│                      └─────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

El usuario accede a través del navegador al puerto **5000** (Flask), que gestiona tanto la lógica de negocio como el renderizado de plantillas HTML mediante Jinja2. Flask se comunica internamente con MySQL a través de la red Docker compartida.

---

## 📦 Requisitos

- Python 3.13
- Docker Desktop
- Las dependencias listadas en `requirements.txt`:

```
Flask
mysql-connector-python
```

Instálalas con:

```bash
pip install -r requirements.txt
```

---

## 🚀 Instalación y Arranque

El proyecto utiliza **tres contenedores Docker** conectados entre sí a través de la red `mi-red-lista-compra`:

| Contenedor              | Imagen                      | Puerto externo → interno | Descripción                   |
| ----------------------- | --------------------------- | ------------------------ | ----------------------------- |
| `flask-app`             | `flask-lista-compra:latest` | `5000:5000`              | Aplicación Flask              |
| `mysql-contenedor`      | `mysql:latest`              | `5432:3306`              | Base de datos MySQL           |
| `contenedor-phpmyadmin` | `phpmyadmin:latest`         | `8080:80`                | Panel de administración de BD |

> ⚠️ El puerto externo de MySQL es el **5432** (mapeado al 3306 interno). Por eso en `app.py` el puerto está configurado como `5432` y **no debe modificarse**.

---

**1. Crear la red compartida** (solo la primera vez):

```bash
docker network create mi-red-lista-compra
```

**2. Levantar el contenedor MySQL:**

```bash
docker run -d \
  --name mysql-contenedor \
  --network mi-red-lista-compra \
  -p 5432:3306 \
  -e MYSQL_ROOT_PASSWORD=LlamaA902-20_21_22 \
  -e MYSQL_DATABASE=paginaWebDB \
  mysql:latest
```

**3. Levantar phpMyAdmin** (opcional, para administrar la BD visualmente):

```bash
docker run -d \
  --name contenedor-phpmyadmin \
  --network mi-red-lista-compra \
  -p 8080:80 \
  -e PMA_HOST=mysql-contenedor \
  phpmyadmin:latest
```

phpMyAdmin estará disponible en: `http://127.0.0.1:8080`

**4. Construir y levantar la aplicación Flask:**

```bash
docker build -t flask-lista-compra .

docker run -d \
  --name flask-app \
  --network mi-red-lista-compra \
  -p 5000:5000 \
  flask-lista-compra:latest
```

**5. Verificar que los tres contenedores están corriendo:**

```bash
docker ps
```

Deberías ver `flask-app`, `mysql-contenedor` y `contenedor-phpmyadmin` con estado activo.

La app estará disponible en: `http://127.0.0.1:5000`

---

**Para arrancar contenedores ya existentes** (si ya los creaste antes):

```bash
docker start mysql-contenedor
docker start contenedor-phpmyadmin
docker start flask-app
```

**Para detenerlos:**

```bash
docker stop flask-app contenedor-phpmyadmin mysql-contenedor
```

---

## 📁 Estructura del Proyecto

```
practica-paginaWeb-dockerBDD/
│
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline de GitHub Actions
│
├── app.py                      # Lógica principal de Flask (rutas y conexión a BD)
├── Dockerfile                  # Imagen Docker de la aplicación Flask
├── requirements.txt            # Dependencias Python
│
└── templates/
    ├── main.html               # Página de bienvenida
    ├── login.html              # Formulario de inicio de sesión
    └── dashboard.html          # Panel principal del usuario autenticado
```

---

## 🗄️ Base de Datos

La base de datos se llama `paginaWebDB` y contiene tres tablas relacionadas entre sí:

```
┌─────────────┐        ┌──────────────────┐        ┌──────────────┐
│  Productos  │        │  ListaDeLaCompra │        │   Usuario    │
│─────────────│        │──────────────────│        │──────────────│
│ ID_PRODUCTO │◄───────│ ID_PRODUCTO      │───────►│ ID_USUARIO   │
│ nombreProd. │        │ ID_USUARIO       │        │ nombreUsuario│
└─────────────┘        │ ID_LISTA_COMPRA  │        │ contrasenya  │
                       │ cantidad         │        └──────────────┘
                       └──────────────────┘
```

- **Usuario**: almacena las credenciales de cada usuario registrado en la plataforma.
- **Productos**: catálogo global de productos disponibles para añadir a cualquier lista.
- **ListaDeLaCompra**: tabla puente que asocia qué productos tiene cada usuario en su lista y en qué cantidad.

---

## ✨ Funcionalidades

### 🏠 Página Principal

**Ruta:** `GET /` — **Archivo:** `main.html`

Página de bienvenida de la aplicación. Presenta el nombre de la app y un botón para acceder al login. Si el usuario ya tiene una sesión activa, se le redirige automáticamente al dashboard sin necesidad de volver a identificarse.

---

### 🔐 Inicio de Sesión

**Rutas:** `GET /login` (formulario) — `POST /login` (procesado) — **Archivo:** `login.html`

El usuario introduce su nombre de usuario y contraseña. Flask consulta la tabla `Usuario` buscando coincidencia exacta de ambos campos:

- **Credenciales correctas:** se crea una sesión con el `ID_USUARIO` y el `nombreUsuario`, y se redirige al dashboard.
- **Credenciales incorrectas:** se muestra el mensaje de error `"Usuario o contraseña incorrectos"` mediante el sistema de flash de Flask y se recarga el formulario.

El mensaje de error es genérico y no revela si el fallo fue en el usuario o en la contraseña, dificultando ataques de enumeración de usuarios.

---

### 📋 Dashboard — Mi Lista

**Ruta:** `GET /dashboard` — **Archivo:** `dashboard.html`

Panel principal accesible únicamente por usuarios autenticados. Si se intenta acceder sin sesión activa, Flask redirige automáticamente al login. El dashboard presenta un **layout dividido en dos columnas**:

**Columna izquierda — Lista de productos:** muestra todos los productos que el usuario tiene actualmente en su lista, con un checkbox individual por producto, su nombre, cantidad asociada, y un checkbox maestro para seleccionar todos de una vez.

**Columna derecha — Acciones:** contiene las dos tarjetas de operación (añadir y eliminar). En la barra superior se muestran estadísticas en tiempo real: número de productos en la lista del usuario y total de productos disponibles en el catálogo.

---

### ➕ Añadir Producto

**Ruta:** `POST /add_product`

Una de las funciones de la lista.
Desde la columna derecha del dashboard, el usuario selecciona un producto del catálogo completo (ordenado alfabéticamente) e indica la cantidad. Flask aplica la siguiente lógica:

- **Si el producto ya está en la lista:** se suma la cantidad indicada a la existente, evitando duplicados.
- **Si el producto no está en la lista:** se inserta un nuevo registro en `ListaDeLaCompra`.

La cantidad debe ser un número entero mayor que cero. Si se envía una cantidad de `0` o negativa, la operación se rechaza y se muestra un mensaje de error sin modificar la base de datos.

---

### 🗑️ Eliminar Producto/s

**Ruta:** `POST /delete_products`

El usuario marca los checkboxes de los productos a eliminar. El botón "Eliminar seleccionados" permanece desactivado hasta que hay al menos un producto marcado, mostrando el conteo en tiempo real. Antes de enviar el formulario aparece un diálogo de confirmación.

Flask recibe los `ID_LISTA_COMPRA` seleccionados y ejecuta un `DELETE` filtrando siempre por el `ID_USUARIO` de la sesión activa, garantizando que un usuario nunca pueda borrar datos de otro. Si no se envía ningún ID, se devuelve el mensaje `"No has seleccionado ningún producto para eliminar."` sin ejecutar ninguna acción en la BD.

---

### 🚪 Cerrar Sesión

**Ruta:** `GET /logout`

Destruye completamente la sesión del usuario con `session.clear()` y redirige a la página principal. El botón de retroceso del navegador no permite volver al dashboard ya que Flask detecta la ausencia de sesión y redirige de nuevo al login.

---

## 🔗 Rutas de la API Flask

| Método | Ruta               | Acceso      | Descripción                                     |
| ------ | ------------------ | ----------- | ----------------------------------------------- |
| GET    | `/`                | Público     | Página de bienvenida                            |
| GET    | `/login`           | Público     | Muestra el formulario de login                  |
| POST   | `/login`           | Público     | Procesa las credenciales e inicia sesión        |
| GET    | `/dashboard`       | Autenticado | Muestra la lista de compra del usuario          |
| POST   | `/add_product`     | Autenticado | Añade un producto a la lista del usuario        |
| POST   | `/delete_products` | Autenticado | Elimina los productos seleccionados de la lista |
| GET    | `/logout`          | Autenticado | Cierra la sesión y redirige al inicio           |

---

## 🔒 Seguridad OWASP

La aplicación implementa varias medidas de seguridad alineadas con la guía **OWASP Top 10**:

**Control de acceso (OWASP A01):** todas las rutas que gestionan datos comprueban que existe una sesión activa antes de ejecutar cualquier operación.
Las operaciones de escritura en BD filtran siempre por el `ID_USUARIO` de la sesión, impidiendo el [acceso sin autorización](https://cwe.mitre.org/data/definitions/862.html).

**Prevención de inyección SQL (OWASP A05):** todas las consultas a la base de datos utilizan **parámetros preparados** (`%s`), nunca concatenación de strings.
Esto elimina la posibilidad de [Inyección SQL](https://cwe.mitre.org/data/definitions/89.html) independientemente del input del usuario.

**Gestión de sesión y autenticación (OWASP A07):** las sesiones se gestionan mediante la librería de sesiones seguras de Flask, protegidas con una `secret_key`.
El logout destruye la sesión por completo con `session.clear()`.
Además, se ha implementado un limite de intentos, para cubrir el uso de [Fuerza Bruta](https://cwe.mitre.org/data/definitions/307.html).

**Manejo de errores (OWASP A04):** los bloques `try/except` en las rutas de escritura capturan excepciones de base de datos y muestran mensajes genéricos al usuario,
sin exponer trazas de pila ni detalles internos del sistema. Asegurando que se [comprueben los valores antes de su uso](https://cwe.mitre.org/data/definitions/319.html).

**Modo debug controlado (OWASP A06):** el modo `debug=True` de Flask solo se activa cuando el script se ejecuta directamente (`if __name__ == '__main__'`),
no cuando se despliega a través de un [servidor en producción](https://cwe.mitre.org/data/definitions/602.html).
Esto permite que se pueda detectar de mejor forma los [errores](https://cwe.mitre.org/data/definitions/501.html) con un lanzamiento más meticuloso.

---

## 🧪 Pruebas con Postman

Las pruebas están definidas en la colección `PaginaWebPuestaProduccion` e incluyen **9 peticiones** que cubren los flujos principales y casos límite de la aplicación.

### Configuración previa

En todas las peticiones (excepto pruebas de acceso sin sesión) deben estar activados:

- **Automatically follow redirects** → para que Postman siga las redirecciones `302` de Flask hasta la página final.
- **Cookie jar** → para mantener la sesión activa entre peticiones y poder acceder al dashboard tras el login.

En el caso de querer realizar las pruebas sin tener todos los dockers bajados, es posible bajar la red directamente y usar las pruebas sin necesidad de los otros dockers.

No obstante, se deberá cambiar la url y sustituir la ip por la del dispositivo en el que se esté trabajando.

#### EJEMPLO:

Si hay una prueba con la url `http://127.0.0.1:5000/`, y la ip del nuevo equipo es `192.168.1.34`, se deberá cambiar a `http://192.168.1.34:5000/`.

---

### Petición 1 — `FuncionaLaPagina`

`GET http://127.0.0.1:5000/`

Prueba de humo básica que comprueba que la aplicación está levantada y responde en la ruta raíz. Si esta petición falla, el resto no tiene sentido ejecutarlas.

---

### Petición 2 — `IntentoCorrectoLogin`

`POST http://127.0.0.1:5000/login`

```
username = Rigoberto23
password = R1g0bert023
```

Incluye un **pre-request script** que limpia las cookies antes de cada ejecución (`pm.cookies.clear()`) para garantizar que el intento de login parte siempre desde un estado limpio. Verifica tres condiciones:

- La respuesta es `200`.
- El HTML resultante contiene `"Mi Lista de Compra"`, confirmando que se ha llegado al dashboard.
- El HTML contiene `"Rigoberto23"`, confirmando que el nombre de usuario aparece en la cabecera de la sesión activa.

---

### Petición 3 — `IntentoFallidoLogin`

`POST http://127.0.0.1:5000/login`

```
username = admin
password = contrasenyaMala
```

Verifica tres condiciones de seguridad ante credenciales incorrectas:

- La respuesta es `200` (Flask recarga el login, no devuelve un error `401`).
- El HTML contiene `"Iniciar Sesión"` y **no** contiene `"products-grid"`, confirmando que el usuario no ha accedido al dashboard.
- El HTML contiene el mensaje `"Usuario o contraseña incorrectos"` generado por Flask.

---

### Petición 4 — `DirecciónListaCompra`

`GET http://127.0.0.1:5000/dashboard`

Acceso directo a la ruta del dashboard. Con la sesión activa establecida por el login correcto previo, verifica que el dashboard carga correctamente sin redirigir al login.

---

### Petición 5 — `AñadirProductosEnLaLista`

`POST http://127.0.0.1:5000/add_product`

```
id_producto = 1
cantidad    = 3
```

Verifica cuatro condiciones tras añadir un producto con datos válidos:

- La respuesta es `200`.
- El HTML contiene `"Mi Lista de Compra"`, confirmando la redirección correcta al dashboard.
- El HTML contiene `"añadido correctamente"`, confirmando que el mensaje flash de éxito aparece.
- El HTML contiene `"Añadir a la lista"`, confirmando que el formulario de acciones sigue disponible tras la operación.

---

### Petición 6 — `Añadir0ProductosEnLaLista`

`POST http://127.0.0.1:5000/add_product`

```
id_producto = 1
cantidad    = 0
```

Prueba de validación con cantidad igual a cero. Verifica que:

- La respuesta es `200` (la app no crashea ante una entrada inválida).
- El HTML **no** contiene `"añadido correctamente"`, confirmando que la operación fue rechazada.
- El HTML contiene `"Mi Lista de Compra"`, confirmando que la app sigue funcionando con normalidad.

---

### Petición 7 — `AñadirProductosNegativosEnLaLista`

`POST http://127.0.0.1:5000/add_product`

```
id_producto = 0
cantidad    = -8
```

Prueba de validación con cantidad negativa. Verifica las mismas tres condiciones que la prueba anterior: la app no acepta la operación, no muestra mensaje de éxito y sigue mostrando el dashboard correctamente, sin errores ni datos corruptos en la BD.

---

### Petición 8 — `BorradoProductosLista`

`POST http://127.0.0.1:5000/delete_products`

```
id_producto = 1
```

Verifica el borrado de un único producto. Comprueba que:

- La respuesta es `200`.
- El HTML contiene `"Mi Lista de Compra"`, confirmando la redirección al dashboard.
- El HTML no contiene `"DatabaseError"` ni `"Traceback"`, confirmando que no se expone ningún error de servidor al usuario.

---

### Petición 9 — `BorradoProductosMultiplesLista`

`POST http://127.0.0.1:5000/delete_products`

```
id_producto = 1
id_producto = 2
```

Verifica el borrado de múltiples productos en una sola petición, enviando el mismo campo `id_producto` varias veces para simular la selección múltiple por checkboxes. Comprueba las mismas condiciones de éxito y ausencia de errores de servidor que la prueba anterior.

---

### Orden de ejecución recomendado

```
1. FuncionaLaPagina                   → Prueba de humo: app levantada
2. IntentoFallidoLogin                → Seguridad: credenciales incorrectas
3. IntentoCorrectoLogin               → Establece la sesión activa
4. DirecciónListaCompra               → Acceso al dashboard con sesión
5. AñadirProductosEnLaLista           → Añadir con datos válidos
6. Añadir0ProductosEnLaLista          → Validación: cantidad = 0
7. AñadirProductosNegativosEnLaLista  → Validación: cantidad negativa
8. BorradoProductosLista              → Eliminar un producto
9. BorradoProductosMultiplesLista     → Eliminar varios productos
```

---

## ⚙️ Integración Continua con GitHub Actions

El proyecto está integrado con **GitHub Actions** mediante un pipeline de CI definido en `.github/workflows/ci.yml`. Cada vez que se realiza un `push` o se abre un `pull request` sobre la rama `main`, GitHub ejecuta automáticamente los siguientes trabajos en cadena:

```
✅ build  ──►  ✅ lint
                ✅ security
                    └──►  ✅ docker
```

Cada sección depende del anterior mediante el atributo `needs`, de forma que si uno falla los siguientes no se ejecutan, ahorrando tiempo y recursos.

---

### Secciones del pipeline

**`build` — Instalar dependencias**

Configura Python 3.13, instala todo lo definido en `requirements.txt` y verifica que `app.py` no tiene errores de sintaxis con `py_compile`. Es la puerta de entrada al resto del pipeline: si las dependencias no instalan o el fichero tiene un error de sintaxis, el resto de comprobaciones no se ejecuta.

**`lint` — Análisis de código**

Ejecuta `flake8` sobre `app.py` filtrando únicamente errores graves de sintaxis y código muerto (categorías `E9`, `F63`, `F7`, `F82`). No falla por cuestiones de estilo de formato, solo por errores reales que podrían romper la aplicación en tiempo de ejecución.

**`security` — Análisis de seguridad**

Ejecuta `bandit`, una herramienta de análisis estático de seguridad para Python, sobre `app.py`. Reporta únicamente vulnerabilidades de severidad media o alta (`-ll`), ignorando advertencias leves.

**`docker` — Build de imagen**

Construye la imagen Docker completa a partir del `Dockerfile` del proyecto para verificar que la imagen es válida y se construye sin errores. Solo se ejecuta si `build` y `lint` han pasado previamente.

---

### Ver los resultados

Los resultados de cada ejecución del pipeline están disponibles en la pestaña **Actions** del repositorio:

```
https://github.com/manuelDiazpas/practica-paginaWeb-dockerBD/actions
```

Cada apartado muestra un log detallado de su ejecución. Si alguno falla aparece una ❌ con el error exacto que lo ha provocado, permitiendo identificar y corregir el problema antes de que llegue a producción. Esto, no se tiene en cuenta con el primero que aparece, puesto que fue comenzado en una rama ajena al `main`

---

_🌱 2025 MercadoVerde — Compra consciente, vida sostenible 🌱_
