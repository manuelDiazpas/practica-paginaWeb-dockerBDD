from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import time

app = Flask(__name__)
app.secret_key = 'claveSecreta' #¡¡No eliminar!! Sirve para pruebas Flasks

MAX_INTENTOS_LOGIN   = 5    # intentos antes de bloquear
TIEMPO_BLOQUEO_LOGIN = 60   # segundos de espera


# Configuración de la base de datos (Docker)
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'LlamaA902-20_21_22',
    'database': 'paginaWebDB',
    'port': 5432 #¡¡No se puede cambiar el puerto!! Es el puerto asignado de docker
}

#Metodo para conectar a la base de datos
def get_db_connection():
    return mysql.connector.connect(**db_config)

#Dirección principal de pagina web
@app.route('/')
def main():
    if 'user_id' in session:
        return redirect(url_for('dashboard')) #Si está logueado, le lleva a la lista personal del usuario
    return render_template('main.html')

#Dirección y metodo para inicio de sesión de la pagina
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Inicializar contadores en sesión si no existen
    if 'login_intentos' not in session:
        session['login_intentos'] = 0
    if 'login_bloqueado_hasta' not in session:
        session['login_bloqueado_hasta'] = None

    # Comprobar si el usuario está bloqueado
    if session['login_bloqueado_hasta']:
        segundos_restantes = int(session['login_bloqueado_hasta'] - time.time())
        if segundos_restantes > 0:
            flash(f'🔒 Demasiados intentos fallidos. Espera {segundos_restantes} segundos antes de intentarlo de nuevo.')
            return render_template('login.html', bloqueado=True, segundos_restantes=segundos_restantes)
        else:
            # El tiempo de bloqueo ha terminado, resetear contadores
            session['login_intentos'] = 0
            session['login_bloqueado_hasta'] = None

    if request.method == 'POST':
        user_input = request.form.get('username')
        pass_input = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM Usuario WHERE nombreUsuario = %s AND contrasenyaUsuario = %s",
            (user_input, pass_input)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        # Funciones inicio sesión
        if user:
            # Login correcto: resetear contadores y crear sesión
            session['login_intentos'] = 0
            session['login_bloqueado_hasta'] = None
            session['user_id'] = user['ID_USUARIO']
            session['username'] = user['nombreUsuario']
            return redirect(url_for('dashboard'))
        else:
            # Login fallido: incrementar contador
            session['login_intentos'] += 1
            intentos_restantes = MAX_INTENTOS_LOGIN - session['login_intentos']

            if session['login_intentos'] >= MAX_INTENTOS_LOGIN:
                # Bloquear al usuario
                session['login_bloqueado_hasta'] = time.time() + TIEMPO_BLOQUEO_LOGIN
                flash(f'🔒 Has superado el límite de {MAX_INTENTOS_LOGIN} intentos fallidos. Espera {TIEMPO_BLOQUEO_LOGIN} segundos.')
                return render_template('login.html', bloqueado=True, segundos_restantes=TIEMPO_BLOQUEO_LOGIN)
            else:
                flash(f'Usuario o contraseña incorrectos. Te quedan {intentos_restantes} intento(s).')
                return redirect(url_for('login'))

    return render_template('login.html', bloqueado=False, segundos_restantes=0)

#Dirección para el dashboard
@app.route('/dashboard')
def dashboard():
    #Si no hay nadie logueado, vuelve atras
    if 'user_id' not in session: 
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Productos en la lista del usuario
    query = """
        SELECT p.ID_PRODUCTO, p.nombreProducto, l.cantidad, l.ID_LISTA_COMPRA
        FROM Productos p
        JOIN ListaDeLaCompra l ON p.ID_PRODUCTO = l.ID_PRODUCTO
        WHERE l.ID_USUARIO = %s
    """
    cursor.execute(query, (session['user_id'],))
    user_products = cursor.fetchall()

    # Todos los productos disponibles en la BD (para el modal de añadir)
    cursor.execute("SELECT ID_PRODUCTO, nombreProducto FROM Productos ORDER BY nombreProducto")
    all_products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('dashboard.html', products=user_products, all_products=all_products)

@app.route('/add_product', methods=['POST'])
def add_product():
    """Añade un producto a la lista de la compra del usuario."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'No autenticado'}), 401

    id_producto = request.form.get('id_producto')

    cantidad_raw = request.form.get('cantidad', '').strip()

    # No es un número entero (ej: "abc", "3.5")
    try:
        cantidad = int(cantidad_raw)
    except ValueError:
        flash(f'{(ValueError)} → La cantidad debe ser un número entero válido.')
        return redirect(url_for('dashboard'))

    # Es un número pero es 0 o negativo
    if cantidad <= 0:
        flash('⚠️ La cantidad debe ser mayor que cero. No se pueden añadir 0 o menos productos.')
        return redirect(url_for('dashboard'))

    if not id_producto:
        flash('Debes seleccionar un producto.')
        return redirect(url_for('dashboard'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Comprobar si ya está en la lista
        cursor.execute(
            "SELECT * FROM ListaDeLaCompra WHERE ID_USUARIO = %s AND ID_PRODUCTO = %s",
            (session['user_id'], id_producto)
        )
        existing = cursor.fetchone()

        if existing:
            # Actualizar cantidad sumando la nueva
            cursor.execute(
                "UPDATE ListaDeLaCompra SET cantidad = cantidad + %s WHERE ID_USUARIO = %s AND ID_PRODUCTO = %s",
                (cantidad, session['user_id'], id_producto)
            )
        else:
            # Insertar nuevo registro
            cursor.execute(
                "INSERT INTO ListaDeLaCompra (ID_USUARIO, ID_PRODUCTO, cantidad) VALUES (%s, %s, %s)",
                (session['user_id'], id_producto, cantidad)
            )

        conn.commit()
        cursor.close()
        conn.close()
        flash('Producto añadido correctamente.')
    except Exception as e:
        flash(f'Error al añadir producto: {str(e)}')

    return redirect(url_for('dashboard'))

@app.route('/delete_products', methods=['POST'])
def delete_products():
    """Elimina los productos seleccionados de la lista de la compra del usuario."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'No autenticado'}), 401

    ids_lista = request.form.getlist('ids_lista')

    if not ids_lista:
        flash('No has seleccionado ningún producto para eliminar.')
        return redirect(url_for('dashboard'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for id_lista in ids_lista:
            cursor.execute(
                "DELETE FROM ListaDeLaCompra WHERE ID_LISTA_COMPRA = %s AND ID_USUARIO = %s",
                (id_lista, session['user_id'])
            )

        conn.commit()
        cursor.close()
        conn.close()
        flash(f'{len(ids_lista)} producto(s) eliminado(s) correctamente.')
    except Exception as e:
        flash(f'Error al eliminar producto(s): {str(e)}')

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))

#Metodo para debuguear si es __main__ el nombre
if __name__ == '__main__':
    app.run(debug=True)