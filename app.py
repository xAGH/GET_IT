# ------------------------------ Importación de librerías ------------------------------
from flask import Flask
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask import session
from flask import flash
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

usuarios = {}

# ------------------------------ Configuración ------------------------------
app = Flask(__name__)
app.secret_key = "I5@G2HqM<K#{1]{RN=)bapgSzg1a2+d9?1Hhgx]4[?T~<T&S<]5bkBw{4R;hK+wcNEBVj#Bmy]tyW?i]"

# ------------------------------ Creación de rutas ------------------------------
# Index
@app.route('/')
def index():
    tittle = "Get It"
    return render_template('index.html', tittle=tittle)

# Interfaz de registro.
@app.route('/interfazregistro')
def interfaz_registro():
 tittle = "Registro"
 return render_template('registro.html', tittle=tittle)

# Interfaz de login.
@app.route('/interfazlogin', methods=['GET'])
def interfaz_login():
    tittle = "Ingreso"
    return render_template('ingreso.html', tittle=tittle)

# Registro completado.
@app.route('/registrado', methods={'POST'})
def registrado():
    tittle = "Registrado correctamente"
    return render_template('registrado.html', tittle=tittle)


# ------------------------------ Creación de rutas lógicas ------------------------------
# Registro
@app.route('/registro', methods=['POST'])
def registro():
    email = request.form.get('email')
    contrasena = request.form.get('contrasena')
    contrasena2 = request.form.get('contrasena2')
    nombre = request.form.get('nombre')
    documento = request.form.get('documento')
    referencia = request.form.get('referencia')
    celular = request.form.get('celular')
    facebook = request.form.get('facebook')
    lista = [email, contrasena, nombre, documento, referencia, celular, facebook]

    if usuarios.get(email):
        flash("El email ya se encuentra registrado.")
        return redirect(url_for('interfaz_registro'))
    
    else:

        if contrasena == contrasena2:
            confirmar_correo(email)
            return render_template('confirma.html', tittle='Confirma tu correo electrónico')

        flash("Las contraseñas no coinciden1.")


        
        return redirect(url_for('interfaz_registro'))

# Login
@app.route('/login', methods=['POST'])
def login():
    # usuarios[email] = {"contrasena":contrasena, "nombre":nombre, "documento":documento, "referencia":referencia, "celular":celular, "facebook":facebook}
    return "200"

def confirmar_correo(email):

    # Plantilla del mensaje

    mensaje = f"""
    <html>
        <body>
            <p style="text-align: center;"><span style="color: #ff0000;"><strong>Confirma tu correo para poder seguir</strong></span></p>
            <p style="text-align: center;"><strong></strong></p>
            <p><a href="{redirect(url_for('registrado'))}" target="_blank" rel="noopener">Confirma</a></p>
        </body>
    </html>
    """

    # Creamos objeto Multipart, quien será el recipiente que enviaremos
    msg = MIMEMultipart()
    msg['From'] = "getitjohguia@outlook.com"
    msg['To'] = email
    msg['Subject'] = "Confirmación de correo"

    # Adjuntamos mensaje
    msg.attach(MIMEText(mensaje, 'html'))

    # Autenticamos
    mailServer = smtplib.SMTP('smtp.live.com',587)
    mailServer.starttls()
    mailServer.login("getitjohguia@outlook.com","getit123")

    # Enviamos
    mailServer.sendmail("getitjohguia@outlook.com", email, msg.as_string())

    # Cerramos conexión
    mailServer.close()


app.run(debug=True, port=5000)