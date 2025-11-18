from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
# Toma la URL de Render, si falla usa una local temporal
db_url = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_por_defecto_insegura')

db = SQLAlchemy(app)

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
    password_hash = db.Column(db.String(128), nullable=False)
    recuperacion_email = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='Invitado')

    def __repr__(self):
        return f'<User {self.username}>'

# --- CREACIÓN DE TABLAS (ESTO CORRIGE EL ERROR) ---
# Esto se ejecuta una sola vez al iniciar la aplicación para asegurar que la BD exista
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
        flash('Inicio de sesión exitoso!', 'success')
        # Por ahora redirige al home, luego haremos el dashboard
        return redirect(url_for('home')) 
    else:
        flash('Usuario o contraseña incorrectos', 'danger')
        return redirect(url_for('home'))

@app.route('/create_account')
def create_account():
    return render_template('account_type.html')

@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    # Solo 1 administrador permitido
    existing_admin = User.query.filter_by(role='Administrador').first()
    if existing_admin:
        flash('Ya existe un administrador registrado. No se puede crear otro.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        cedula = request.form.get('cedula')
        celular = request.form.get('celular')
        institucion_deportiva = request.form.get('institucion_deportiva')
        pais = "Ecuador"
        provincia = "Cotopaxi"
        canton = request.form.get('canton')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        recuperacion_email = request.form.get('recuperacion_email')

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('register_admin.html', cantones=["Latacunga", "La Maná", "Pujilí", "Salcedo", "Saquisilí", "Sigchos", "Pangua"])
        
        hashed_password = generate_password_hash(password)

        new_admin = User(
            nombres=nombres, apellidos=apellidos, cedula=cedula, celular=celular,
            institucion_deportiva=institucion_deportiva, pais=pais, provincia=provincia,
            canton=canton, email=email, username=username, password_hash=hashed_password,
            recuperacion_email=recuperacion_email, role='Administrador'
        )

        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Administrador registrado exitosamente!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar: {str(e)}', 'danger')
            return render_template('register_admin.html', cantones=["Latacunga", "La Maná", "Pujilí", "Salcedo", "Saquisilí", "Sigchos", "Pangua"])

    cantones = ["Latacunga", "La Maná", "Pujilí", "Salcedo", "Saquisilí", "Sigchos", "Pangua"]
    return render_template('register_admin.html', cantones=cantones)

if __name__ == '__main__':
    app.run(debug=True)
