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
from mysql import connector as sql


# ------------------------------ Configuración ------------------------------

# Se configura el Flask name como app
app = Flask(__name__)
# Se crea la secret key utilizada para cifrar los datos entregados a las cookies.

app.secret_key = "I5@G2HqM<K#{1]{RN=)bapgSzg1a2+d9?1Hhgx]4[?T~<T&S<]5bkBw{4R;hK+wcNEBVj#Bmy]tyW?i]"

# Se hace la conexión con la base de datos.
db = sql.connect(
    host = 'localhost',
    user = 'root',
    passwd = '',
    database = 'get_it'
)
# Creación del cursor para las consultas SQL
cursor = db.cursor()

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
    contrasena = request.args.get('contrasena')
    email = request.args.get('email')
    return render_template('registro.html', tittle=tittle, contrasena=contrasena, email=email)

# Interfaz de login.
@app.route('/interfazlogin')
def interfaz_login():
    tittle = "Ingreso"
    return render_template('ingreso.html', tittle=tittle)

# Registro completado.
@app.route('/registrado/<id>')
def registrado(id):
    id = id
    cursor.execute("""UPDATE usuarios set estado=1 where idusuarios=%s""",[id])
    db.commit()
    tittle = "Registrado correctamente"
    return "200"


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
    cursor.execute("""SELECT email from usuarios where email=%s""",[email])
    email_registrado = cursor.fetchall()
    if len(email_registrado) > 0:
        return redirect(url_for('interfaz_registro',email='invalid'))
    
    else:

        if contrasena == contrasena2:
            cursor.execute("""INSERT INTO usuarios(idusuarios,nombre,email,clave,whatsapp,facebook,referencia, estado)
            VALUES (%s,%s, %s, %s, %s, %s, %s, "0")""",
            [documento, nombre, email, contrasena, celular, facebook, referencia])
            db.commit()
            confirmar_correo(email, documento)
            return render_template('confirma.html', tittle='Confirma tu correo electrónico')

        return redirect(url_for('interfaz_registro',contrasena='invalid'))

# Login
@app.route('/login', methods=['POST'])
def login():
    # usuarios[email] = {"contrasena":contrasena, "nombre":nombre, "documento":documento, "referencia":referencia, "celular":celular, "facebook":facebook}
    return "200"

def confirmar_correo(email, documento):

    # Plantilla del mensaje
    mensaje = """
    <html>
        <body>
            <p style="text-align: center;"><span style="color: #ff0000;"><strong>Confirma tu correo para poder seguir</strong></span></p>
            <p style="text-align: center;"><strong></strong></p>
            <p><a href="http://127.0.0.1:5000/registrado/{}" target="_blank" rel="noopener">Confirma</a></p>
        </body>
    </html>
    """.format(documento)

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