from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
db_url = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_secreta_por_defecto')

db = SQLAlchemy(app)

# --- MODELO DE BASE DE DATOS: Usuario ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(10), unique=True, nullable=False)
    # CELULAR ELIMINADO del formulario, pero podría seguir en DB si se quisiera guardar
    # pais = db.Column(db.String(50), nullable=False, default='Ecuador')
    # provincia = db.Column(db.String(50), nullable=False, default='Cotopaxi')
    institucion_deportiva = db.Column(db.String(100), nullable=False)
    canton = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    recuperacion_email = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='Invitado')

    def __repr__(self):
        return f'<User {self.username}>'

# --- CREAR TABLAS AUTOMÁTICAMENTE ---
with app.app_context():
    db.create_all()

# --- RUTAS ---

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        flash(f'¡Bienvenido {user.nombres}!', 'success')
        return redirect(url_for('home')) 
    else:
        flash('Usuario o contraseña incorrectos.', 'danger')
        return redirect(url_for('home'))

@app.route('/create_account')
def create_account():
    return render_template('account_type.html')

@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    opciones_institucion = ["Latacunga", "La Maná", "Pujilí", "Salcedo", "Saquisilí", "Sigchos", "Pangua", "Todos"]
    
    if request.method == 'POST':
        existing_admin = User.query.filter_by(role='Administrador').first()
        
        if existing_admin:
            flash('El sistema ya tiene un administrador.', 'danger')
            return render_template('register_admin.html', opciones=opciones_institucion)

        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        cedula = request.form.get('cedula')
        # celular = request.form.get('celular') # ELIMINADO
        institucion = request.form.get('institucion_deportiva')
        # pais = "Ecuador" # ELIMINADO (se puede reintroducir si es necesario en la DB)
        # provincia = "Cotopaxi" # ELIMINADO (se puede reintroducir si es necesario en la DB)
        canton = request.form.get('canton')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        recuperacion_email = request.form.get('recuperacion_email')

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('register_admin.html', opciones=opciones_institucion,
                                   nombres=nombres, apellidos=apellidos, cedula=cedula,
                                   institucion_deportiva=institucion, canton=canton,
                                   email=email, username=username, recuperacion_email=recuperacion_email)

        # Validar si usuario, email o cédula ya existen
        if User.query.filter((User.email == email) | (User.username == username) | (User.cedula == cedula)).first():
             flash('El usuario, correo o cédula ya están registrados.', 'danger')
             return render_template('register_admin.html', opciones=opciones_institucion,
                                    nombres=nombres, apellidos=apellidos, cedula=cedula,
                                    institucion_deportiva=institucion, canton=canton,
                                    email=email, username=username, recuperacion_email=recuperacion_email)


        hashed_password = generate_password_hash(password)
        
        new_admin = User(
            nombres=nombres, apellidos=apellidos, cedula=cedula, 
            # celular=celular, # Si se elimina del HTML, debe eliminarse de aquí o asignarle un valor por defecto
            institucion_deportiva=institucion, pais="Ecuador", provincia="Cotopaxi", # Estos se mantienen con valores por defecto
            canton=canton, email=email, username=username, password_hash=hashed_password,
            recuperacion_email=recuperacion_email, role='Administrador'
        )

        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Administrador registrado exitosamente en la Base de Datos.', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {str(e)}', 'danger')
            return render_template('register_admin.html', opciones=opciones_institucion,
                                   nombres=nombres, apellidos=apellidos, cedula=cedula,
                                   institucion_deportiva=institucion, canton=canton,
                                   email=email, username=username, recuperacion_email=recuperacion_email)

    return render_template('register_admin.html', opciones=opciones_institucion)

if __name__ == '__main__':
    app.run(debug=True)
