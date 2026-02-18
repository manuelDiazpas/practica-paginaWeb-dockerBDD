# 🌿 MercadoVerde — Lista de Compra Personal

Aplicación web desarrollada con **Flask** y **MySQL** que permite a los usuarios gestionar su lista de la compra de forma personal, segura y organizada. Cada usuario accede con sus credenciales y visualiza únicamente sus propios productos.

---

## 📋 Tabla de Contenidos

- [🌿 MercadoVerde — Lista de Compra Personal](#-mercadoverde--lista-de-compra-personal)
  - [📋 Tabla de Contenidos](#-tabla-de-contenidos)
  - [Requisitos](#requisitos)
  - [Instalación y Arranque](#instalación-y-arranque)
  - [Estructura del Proyecto](#estructura-del-proyecto)
  - [Base de Datos](#base-de-datos)
  - [Funcionalidades](#funcionalidades)
    - [🏠 Página Principal](#-página-principal)
    - [🔐 Inicio de Sesión](#-inicio-de-sesión)
    - [📋 Dashboard — Mi Lista](#-dashboard--mi-lista)
    - [➕ Añadir Producto](#-añadir-producto)
    - [🗑️ Eliminar Producto/s](#️-eliminar-productos)
    - [🚪 Cerrar Sesión](#-cerrar-sesión)
  - [Rutas de la API Flask](#rutas-de-la-api-flask)
  - [Seguridad](#seguridad)
  - [Pruebas con Postman](#pruebas-con-postman)

---

## Requisitos

- Python 3.10+
- Docker (para la base de datos MySQL)
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

## Instalación y Arranque

El proyecto utiliza **tres contenedores Docker** conectados entre sí a través de la red `mi-red-lista-compra`:

| Contenedor              | Imagen                   | Puerto externo → interno | Descripción                   |
| ----------------------- | ------------------------ | ------------------------ | ----------------------------- |
| `flask-app`             | `flask-lista-cor:latest` | `5000:5000`              | Aplicación Flask              |
| `mysql-contenedor`      | `mysql:latest`           | `5432:3306`              | Base de datos MySQL           |
| `contenedor-phpmyadmin` | `phpmyadmin:latest`      | `8080:80`                | Panel de administración de BD |

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
docker build -t flask-lista-cor .

docker run -d \
  --name flask-app \
  --network mi-red-lista-compra \
  -p 5000:5000 \
  flask-lista-cor:latest
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

## Estructura del Proyecto

```
practica-paginaWeb-dockerBDD/
│
├── app.py                  # Lógica principal de Flask (rutas y conexión a BD)
├── Dockerfile              # Imagen Docker con la base de datos MySQL
├── requirements.txt        # Dependencias Python
│
└── templates/
    ├── main.html           # Página de bienvenida
    ├── login.html          # Formulario de inicio de sesión
    └── dashboard.html      # Panel principal del usuario autenticado
```

---

## Base de Datos

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

- **Usuario**: almacena las credenciales de cada usuario.
- **Productos**: catálogo global de productos disponibles para añadir a la lista.
- **ListaDeLaCompra**: tabla puente que asocia qué productos tiene cada usuario en su lista, junto con la cantidad deseada.

---

## Funcionalidades

### 🏠 Página Principal

**Ruta:** `GET /`  
**Archivo:** `main.html`

Página de bienvenida de la aplicación. Presenta el nombre de la app y un botón para acceder al login. Si el usuario ya tiene una sesión activa, se le redirige automáticamente al dashboard sin necesidad de volver a identificarse.

---

### 🔐 Inicio de Sesión

**Ruta:** `GET /login` — muestra el formulario  
**Ruta:** `POST /login` — procesa las credenciales  
**Archivo:** `login.html`

El usuario introduce su **nombre de usuario** y **contraseña**. Flask consulta la tabla `Usuario` de la base de datos buscando una coincidencia exacta de ambos campos. Hay dos posibles resultados:

- **Credenciales correctas:** se crea una sesión con el `ID_USUARIO` y el `nombreUsuario`, y se redirige al dashboard.
- **Credenciales incorrectas:** se muestra un mensaje de error mediante el sistema de flash de Flask (`"Usuario o contraseña incorrectos"`) y se recarga el formulario.

Si el login falla, **no se revela** si el error fue en el usuario o en la contraseña, lo que dificulta ataques de enumeración de usuarios.

---

### 📋 Dashboard — Mi Lista

**Ruta:** `GET /dashboard`  
**Archivo:** `dashboard.html`

Panel principal al que solo puede acceder un usuario autenticado. Si se intenta acceder sin sesión activa, Flask redirige automáticamente al login.

El dashboard tiene un **layout dividido en dos columnas**:

**Columna izquierda — Lista de productos:**
Muestra todos los productos que el usuario tiene actualmente en su lista de la compra. Cada producto aparece como una fila con:

- Un **checkbox** para seleccionarlo individualmente.
- El **nombre del producto**.
- La **cantidad** asociada.
- Un checkbox maestro en la barra inferior para **seleccionar todos** de una vez.

**Columna derecha — Acciones:**
Contiene las dos operaciones principales que el usuario puede realizar sobre su lista (añadir y eliminar, descritas en las siguientes secciones).

En la parte superior de la página, una barra de estadísticas muestra cuántos productos hay en la lista del usuario y cuántos están disponibles en el catálogo general.

---

### ➕ Añadir Producto

**Ruta:** `POST /add_product`

Desde el panel derecho del dashboard, el usuario puede añadir un producto a su lista mediante un formulario con dos campos:

- **Desplegable de producto:** muestra todos los productos disponibles en la tabla `Productos`, ordenados alfabéticamente.
- **Campo de cantidad:** número entero, mínimo 1.

Al enviar el formulario, Flask comprueba si ese producto **ya existe en la lista del usuario**:

- **Si ya existe:** en lugar de duplicarlo, se **suma la cantidad** indicada a la que ya tenía.
- **Si no existe:** se inserta un nuevo registro en `ListaDeLaCompra`.

En ambos casos, al terminar se muestra un mensaje de confirmación (`"Producto añadido correctamente."`) y se recarga el dashboard con la lista actualizada. Si ocurre algún error de base de datos, se captura la excepción y se muestra un mensaje de error sin exponer detalles técnicos al usuario.

---

### 🗑️ Eliminar Producto/s

**Ruta:** `POST /delete_products`

Desde el panel derecho del dashboard, el usuario puede eliminar uno o varios productos de su lista. El flujo es el siguiente:

1. El usuario marca los **checkboxes** de los productos que quiere eliminar en la columna izquierda.
2. El botón "Eliminar seleccionados" en la columna derecha se activa solo cuando hay al menos un producto marcado, mostrando el conteo en tiempo real.
3. Al pulsar el botón, aparece un **diálogo de confirmación** en el navegador antes de enviar el formulario.
4. Flask recibe los `ID_LISTA_COMPRA` seleccionados y ejecuta un `DELETE` por cada uno, **filtrando siempre por el `ID_USUARIO` de la sesión activa** para garantizar que un usuario nunca pueda borrar datos de otro.

Si no se selecciona ningún producto y se intenta eliminar de todos modos (por ejemplo, manipulando la petición), Flask devuelve el mensaje `"No has seleccionado ningún producto para eliminar."` sin realizar ninguna acción en la BD.

Al terminar correctamente, se muestra cuántos productos se han eliminado (`"X producto(s) eliminado(s) correctamente."`).

---

### 🚪 Cerrar Sesión

**Ruta:** `GET /logout`

Destruye completamente la sesión del usuario con `session.clear()` y redirige a la página principal. Tras cerrar sesión, el botón de retroceso del navegador no permite volver al dashboard porque Flask detecta que no hay sesión activa y redirige de nuevo al login.

---

## Rutas de la API Flask

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

## Seguridad

La aplicación implementa varias medidas de seguridad alineadas con la guía **OWASP Top 10**:

**Control de acceso (OWASP A01):** todas las rutas que gestionan datos comprueban que existe una sesión activa antes de ejecutar cualquier operación. Además, las operaciones de escritura en BD filtran siempre por el `ID_USUARIO` de la sesión, impidiendo que un usuario acceda o modifique datos de otro.

**Prevención de inyección SQL (OWASP A05):** todas las consultas a la base de datos utilizan **parámetros preparados** (`%s`), nunca concatenación de strings. Esto elimina la posibilidad de inyección SQL independientemente de lo que el usuario introduzca.

**Gestión de sesión/Autenticación (OWASP A07 | OWASP A09):** las sesiones se gestionan mediante la librería de sesiones seguras de Flask, protegidas con una `secret_key`. El logout destruye la sesión por completo con `session.clear()`.

**Manejo de errores criptográficos (OWASP A04):** los bloques `try/except` en las rutas de escritura capturan excepciones de base de datos y muestran mensajes genéricos al usuario, sin exponer trazas de pila ni detalles internos del sistema.

---

## Pruebas con Postman

Para ejecutar las pruebas de la aplicación con Postman es necesario configurar:

- **Automatically follow redirects:** activado en todas las peticiones (Flask responde con redirecciones `302`).
- **Cookie jar:** activado para mantener la sesión entre peticiones.

El flujo de pruebas recomendado es:

1. `POST /login` con credenciales válidas → verifica que se llega al dashboard.
2. `POST /login` con credenciales inválidas → verifica el mensaje de error y que no se accede al dashboard.
3. `POST /add_product` con un `id_producto` válido → verifica el mensaje de confirmación.
4. `POST /delete_products` con uno o varios `ids_lista` → verifica la eliminación correcta.
5. `POST /delete_products` sin `ids_lista` → verifica el mensaje de advertencia.
6. `POST /add_product` sin sesión activa → verifica que devuelve `401`.

---

_🌱 2025 MercadoVerde — Compra consciente, vida sostenible 🌱_
