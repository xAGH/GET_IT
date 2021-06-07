# ------------------------------ Importación de librerías ------------------------------
from flask import Flask, request, jsonify, redirect, url_for, render_template
from werkzeug.utils import redirect
from envio_correo import confirmar_correo

usuarios = []

# ------------------------------ Configuración ------------------------------
app = Flask(__name__)

# ------------------------------ Creación de rutas ------------------------------
# Index
@app.route('/')
def index():
    tittle = "Get It"
    return render_template('index.html', tittle=tittle)

# Registro
@app.route('/registro', methods=['POST'])
def registro():
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    contrasena = request.form.get('contrasena')
    contrasena2 = request.form.get('contrasena2')
    if contrasena == contrasena2:
        confirmar_correo(email)
        return "200"

@app.route('/login', methods=['GET'])
def login():
    return "Ok"

app.run(debug=True, port=5000)