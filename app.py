from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Configuración de la base de datos (Docker)
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'LlamaA902-20_21_22',
    'database': 'paginaWebDB',
    'port': 5432 #¡¡No se puede cambiar el puerto!!
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def main():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
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

        if user:
            session['user_id'] = user['ID_USUARIO']
            session['username'] = user['nombreUsuario']
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
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
    cantidad = request.form.get('cantidad', 1)

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
            # Actualizar cantidad
            cursor.execute(
                "UPDATE ListaDeLaCompra SET cantidad = cantidad + %s WHERE ID_USUARIO = %s AND ID_PRODUCTO = %s",
                (cantidad, session['user_id'], id_producto)
            )
        else:
            # Insertar nuevo
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

if __name__ == '__main__':
    app.run(debug=True)