from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Aquí puedes agregar tu lógica de autenticación.
    # Por ahora, solo redirigiremos a una página de éxito si las credenciales son "admin/password"
    if username == 'admin' and password == 'password':
        return redirect(url_for('success_page'))
    else:
        # Puedes pasar un mensaje de error a la plantilla si lo deseas
        return render_template('login.html', error="Usuario o contraseña incorrectos")

@app.route('/success')
def success_page():
    return "¡Inicio de sesión exitoso! Bienvenido."

if __name__ == '__main__':
    app.run(debug=True)
