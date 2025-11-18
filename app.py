from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash # Para contraseñas seguras

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
# Si estamos en Render, toma la URL de la variable de entorno DATABASE_URL
# Si estamos en local, puedes poner una SQLite temporal (útil para pruebas)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Necesario para usar flash messages (mensajes que aparecen y desaparecen)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'una_clave_secreta_por_defecto') # ¡CAMBIA ESTO EN PRODUCCIÓN!

# --- MODELO DE BASE DE DATOS: Usuario ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(10), unique=True, nullable=False)
    celular = db.Column(db.String(15), nullable=False)
    institucion_deportiva = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(50), nullable=False, default='Ecuador')
    provincia = db.Column(db.String(50), nullable=False, default='Cotopaxi')
    canton = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) # Guardaremos la contraseña hasheada
    recuperacion_email = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='Invitado') # 'Administrador' o 'Invitado'

    def __repr__(self):
        return f'<User {self.username}>'

# --- RUTAS DE LA APLICACIÓN ---

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        flash('Inicio de sesión exitoso!', 'success')
        return redirect(url_for('dashboard')) # Redirige a un dashboard que aún no existe
    else:
        flash('Usuario o contraseña incorrectos', 'danger')
        return redirect(url_for('home'))

@app.route('/create_account')
def create_account():
    return render_template('account_type.html')

# --- RUTA PARA EL REGISTRO DE ADMINISTRADOR (CON LÓGICA) ---
@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    # --- LÓGICA: SOLO UN ADMINISTRADOR PERMITIDO ---
    existing_admin = User.query.filter_by(role='Administrador').first()
    if existing_admin:
        flash('Ya existe un administrador registrado. No se puede crear otro.', 'danger')
        return redirect(url_for('home')) # O a otra página de error/información

    if request.method == 'POST':
        # Recopilar datos del formulario
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        cedula = request.form.get('cedula')
        celular = request.form.get('celular')
        institucion_deportiva = request.form.get('institucion_deportiva')
        pais = request.form.get('pais')
        provincia = request.form.get('provincia')
        canton = request.form.get('canton')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        recuperacion_email = request.form.get('recuperacion_email')

        # Validaciones básicas
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('register_admin.html',
                                   nombres=nombres, apellidos=apellidos, cedula=cedula,
                                   celular=celular, institucion_deportiva=institucion_deportiva,
                                   pais=pais, provincia=provincia, canton=canton,
                                   email=email, username=username, recuperacion_email=recuperacion_email)
        
        # Hashear la contraseña para seguridad
        hashed_password = generate_password_hash(password)

        # Crear nuevo usuario (Administrador)
        new_admin = User(
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            celular=celular,
            institucion_deportiva=institucion_deportiva,
            pais=pais,
            provincia=provincia,
            canton=canton,
            email=email,
            username=username,
            password_hash=hashed_password,
            recuperacion_email=recuperacion_email,
            role='Administrador' # Asignamos el rol de Administrador
        )

        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Administrador registrado exitosamente!', 'success')
            return redirect(url_for('home')) # Redirige al login después de registrar
        except Exception as e:
            db.session.rollback()
            # Validar si ya existe cédula o email o username
            if "UNIQUE constraint failed: user.cedula" in str(e):
                flash('La cédula ya está registrada.', 'danger')
            elif "UNIQUE constraint failed: user.email" in str(e):
                flash('El correo electrónico ya está registrado.', 'danger')
            elif "UNIQUE constraint failed: user.username" in str(e):
                flash('El nombre de usuario ya está en uso.', 'danger')
            else:
                flash(f'Error al registrar el administrador: {e}', 'danger')
            
            return render_template('register_admin.html',
                                   nombres=nombres, apellidos=apellidos, cedula=cedula,
                                   celular=celular, institucion_deportiva=institucion_deportiva,
                                   pais=pais, provincia=provincia, canton=canton,
                                   email=email, username=username, recuperacion_email=recuperacion_email)

    # Si es un GET request o si hay errores y se vuelve a renderizar el formulario
    cantones = ["Latacunga", "La Maná", "Pujilí", "Salcedo", "Saquisilí", "Sigchos", "Pangua"]
    return render_template('register_admin.html', cantones=cantones)

# --- RUTA PARA UN DASHBOARD BÁSICO (aún no existe la interfaz) ---
@app.route('/dashboard')
def dashboard():
    return "Bienvenido al Dashboard del Administrador!"

# Comando para crear las tablas de la base de datos (Ejecutar solo una vez)
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    # Para ejecutar en local con variables de entorno si existe un .env
    from dotenv import load_dotenv
    load_dotenv()
    with app.app_context():
        db.create_all() # Crear tablas si no existen al iniciar localmente
    app.run(debug=True)
