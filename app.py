from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ---------------- CONFIGURACIÓN ----------------
db_url = os.environ.get('DATABASE_URL')

if not db_url:
    raise RuntimeError("DATABASE_URL no está configurada")

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_segura')

db = SQLAlchemy(app)

# ---------------- MODELO ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(10), unique=True, nullable=False)
    institucion_deportiva = db.Column(db.String(100), nullable=False)
    canton = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    recuperacion_email = db.Column(db.String(120))
    role = db.Column(db.String(20), nullable=False, default='Invitado')

# ---------------- CREAR TABLAS ----------------
with app.app_context():
    db.create_all()

# ---------------- RUTAS ----------------
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_name'] = f"{user.nombres} {user.apellidos}"
        return redirect(url_for('menu_principal'))
    else:
        flash('Usuario o contraseña incorrectos', 'danger')
        return redirect(url_for('home'))

@app.route('/menu-principal')
def menu_principal():
    if 'user_name' not in session:
        return redirect(url_for('home'))
    return render_template('menu_principal.html', nombre_usuario=session['user_name'])

@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    opciones_institucion = ["Latacunga", "La Maná", "Pujilí", "Salcedo", "Saquisilí", "Sigchos", "Pangua", "Todos"]

    if request.method == 'POST':
        if User.query.filter_by(role='Administrador').first():
            flash('Ya existe un administrador', 'danger')
            return render_template('register_admin.html', opciones=opciones_institucion)

        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('register_admin.html', opciones=opciones_institucion)

        new_admin = User(
            nombres=request.form['nombres'],
            apellidos=request.form['apellidos'],
            cedula=request.form['cedula'],
            institucion_deportiva=request.form['institucion_deportiva'],
            canton=request.form['canton'],
            email=request.form['email'],
            username=request.form['username'],
            password_hash=generate_password_hash(password),
            recuperacion_email=request.form['recuperacion_email'],
            role='Administrador'
        )

        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Administrador creado correctamente', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')

    return render_template('register_admin.html', opciones=opciones_institucion)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run()

