from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Configuración de la base de datos (Docker)
db_config = {
    'host': '127.0.0.1', 
    'user': 'root',
    'password': 'LlamaA902-20_21_22',
    'database': 'paginaWebDB',
    'port': 5432
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
        # Estos nombres 'username' y 'password' deben ser iguales al 'name' del HTML
        user_input = request.form.get('username')
        pass_input = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Consulta a tu tabla 'Usuario'
        cursor.execute("SELECT * FROM Usuario WHERE nombreUsuario = %s AND contrasenyaUsuario = %s", (user_input, pass_input))
        user = cursor.fetchone()
        
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
    
    # Consulta SQL para obtener los productos de la lista del usuario logueado
    query = """
        SELECT p.nombreProducto, l.cantidad 
        FROM Productos p
        JOIN ListaDeLaCompra l ON p.ID_PRODUCTO = l.ID_PRODUCTO
        WHERE l.ID_USUARIO = %s
    """
    cursor.execute(query, (session['user_id'],))
    user_products = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('dashboard.html', products=user_products)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)