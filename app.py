# ------------------------------ Importación de librerías ------------------------------
from flask import Flask
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask import session
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mysql import connector as sql
from werkzeug.utils import secure_filename
from datetime import date
import os

# ------------------------------ Configuración ------------------------------

# Se configura el Flask name como app
app = Flask(__name__)

# Se crea la secret key utilizada para cifrar los datos entregados a las cookies.
app.secret_key = "I5@G2HqM<K#{1]{RN=)bapgSzg1a2+d9?1Hhgx]4[?T~<T&S<]5bkBw{4R;hK+wcNEBVj#Bmy]tyW?i]"

# Se define la ruta para guardar los archivos y los tipos permitidos. 
upload_folder = "./static/imgs_productos"
allowed_extensions = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = upload_folder

# Variable que almacena la id del producto
ids = []

# Se hace la conexión con la base de datos.
config = {
  'user': 'root',
  'password': '',
  'host': 'localhost',
  'database': 'get_it',
  'raise_on_warnings': True
}

# ------------------------------ Creación de rutas ------------------------------
# Index
@app.route('/')
def index():
    i = request.args.get('i')
    db = sql.connect(**config)
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM productos""")
    productos = cursor.fetchall()
    db.close
    p = 0
    for i in range(len(productos)):
        if productos[i][6] == '1':
            p = 1
        else:
            p = 0
    largor = len(productos)
    tittle = "Get It"
    if "user" in session:
        return render_template('index.html', tittle=tittle, user=1, productos=productos, largor=largor, p=p)

    return render_template('index.html', tittle=tittle, productos=productos, largor=largor, i=i, p=p)

# Interfaz de registro.
@app.route('/interfazregistro')
def interfaz_registro():
    i = request.args.get('i')
    tittle = "Registro"
    contrasena = request.args.get('contrasena')
    email = request.args.get('email')
    if "user" in session:
        tittle = "No autorizado"
        return render_template('error.html', tittle=tittle)
    return render_template('registro.html', tittle=tittle, contrasena=contrasena, email=email, i=i)

# Interfaz de login.
@app.route('/interfazlogin')
def interfaz_login():
    tittle = "Ingreso"
    usuario = request.args.get('usuario')
    clave = request.args.get('clave')
    email = request.args.get('email')
    if "user" in session:
        tittle = "No autorizado"
        return render_template('error.html', tittle=tittle)
    return render_template('ingreso.html', tittle=tittle, usuario=usuario, clave=clave)

# Cambio de datos
@app.route('/actualizardatos')
def actualizar_datos():
    tittle = 'Actualizar datos.'
    if 'user' in session:
        return render_template('actualizar_datos.html', tittle=tittle, user=1)

    tittle = "No autorizado"
    return render_template('error.html', tittle=tittle)

# Interfaz de publicar. 
@app.route('/interfazpublicar')
def interfaz_publicar():
    tittle = "Publicar"
    if "user" in session:
        return render_template('publicar.html', tittle=tittle, user=1)

    tittle = "No autorizado"
    return render_template('error.html', tittle=tittle)


# ------------------------------ Creación de rutas lógicas ------------------------------
# Registro
@app.route('/registro', methods=['POST'])
def registro():
    try: 
        email = request.form.get('email')
        contrasena = request.form.get('contrasena')
        contrasena2 = request.form.get('contrasena2')
        nombre = request.form.get('nombre')
        documento = request.form.get('documento')
        direccion = request.form.get('direccion')
        referencia = request.form.get('referencia')
        celular = request.form.get('celular')

        db = sql.connect(**config)
        cursor = db.cursor()
        cursor.execute("""SELECT email from usuarios where email=%s""",[email])
        email_registrado = cursor.fetchall()
        

        if len(email_registrado) > 0:
            db.close()
            return redirect(url_for('interfaz_registro',email='invalid'))
        
        else:

            if contrasena == contrasena2:
                cursor.execute("""INSERT INTO usuarios(idusuarios,nombre,email,clave,celular,direccion,referencia, estado)
                VALUES (%s,%s, %s, %s, %s, %s,%s, "0")""",
                [documento, nombre, email, contrasena, celular,direccion, referencia])
                db.commit()
                db.close()
                mensaje = """
        <html>
            <body>
                <p style="text-align: center;"><span style="color: #ff0000;"><strong>Confirma tu correo para poder seguir</strong></span></p>
                <p style="text-align: center;"><strong></strong></p>
                <p><a href="http://127.0.0.1:5000/registrado/{}" rel="noopener">Confirma</a></p>
            </body>
        </html>
        """.format(documento)
                subject = "Confirmación de correo"
                envio_correo(mensaje,subject,email)
                return render_template('confirma.html', tittle='Confirma tu correo electrónico', confirma=1, user=1)

            db.close()
            return redirect(url_for('interfaz_registro',contrasena='invalid'))

    except:
        return redirect(url_for('interfaz_registro',i=1))

# Registro completado.
@app.route('/registrado/<id_usuario>')
def registrado(id_usuario):
    id_usuario = id_usuario
    db = sql.connect(**config)
    cursor = db.cursor()
    cursor.execute("""UPDATE usuarios SET estado=1 WHERE idusuarios=%s""",[id_usuario])
    db.commit()
    db.close()
    session["user"] = id_usuario
    return redirect(url_for('index'))

# Login
@app.route('/login', methods=['POST', 'GET'])
def login():
    correo = request.form.get('usuario')
    contrasena = request.form.get('contrasena')
    db = sql.connect(**config)
    cursor = db.cursor()
    cursor.execute("""SELECT email from usuarios where email=%s""",[correo])
    email = cursor.fetchone()

    if email:
        cursor.execute("""SELECT estado from usuarios where email=%s""",[correo])
        estado = cursor.fetchone()

        if estado[0] == '1':

            if email[0] == correo:
                cursor.execute("""SELECT clave from usuarios where email=%s""",[correo])
                contrasena_bdd = cursor.fetchone()

                if contrasena == contrasena_bdd[0]:
                    cursor.execute("""SELECT idusuarios from usuarios where email=%s""",[correo])
                    id_usuario = cursor.fetchone()
                    db.close()
                    session["user"] = id_usuario[0]
                    return redirect(url_for('index'))

                db.close()
                return redirect(url_for('interfaz_login',clave=0, email=correo))
                

        return render_template("confirma.html", confirma=1, user=1)

    db.close()
    return redirect(url_for('interfaz_login',usuario="Noregistrado"))
    


# Logout
@app.route('/logout')
def logout():
    if "user" in session:
        session.pop("user")
        return redirect(url_for("index"))
    
    else:
        tittle = "No autorizado"
        return render_template('error.html', tittle=tittle)

# Cuenta 
@app.route('/cuenta', methods=['GET'])
def interfaz_cuenta():
    if "user" in session:
        tittle = 'Cuenta'
        id_usuario = session["user"]
        db = sql.connect(**config)
        cursor = db.cursor()
        cursor.execute("""SELECT * from usuarios where idusuarios=%s""",[id_usuario])
        datos = cursor.fetchone()
        db.close()
        idusuarios = datos[0]
        nombre = datos[1]
        correo = datos[2]
        celular = datos[4]
        direccion = datos[5]
        referenciado = datos[6]
        return render_template('cuenta.html', user=1, tittle=tittle,idusuarios=idusuarios, nombre=nombre,correo=correo,celular=celular,referenciado=referenciado,direccion=direccion)

    tittle = 'No autorizado'
    return render_template('error.html', tittle=tittle)

@app.route('/publicar', methods=['POST'])
def publicar():
    categoria = request.form.get('PoS')
    nombre = request.form.get('encabezado')
    cambio = request.form.get('cambio')
    estado = 1
    descripcion = request.form.get('duser_message')
    f = request.files['file1']
    filename = secure_filename(f.filename)
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    fecha = date.today().strftime('%d/%m/%Y')
    db = sql.connect(**config)
    cursor = db.cursor()
    idusuario = session["user"]
    cursor.execute("""INSERT INTO productos(nombre, descripcion, idusuario, cambiarpor, estado, fecha_publ, categoria, img) values
    (%s, %s, %s, %s, %s, %s, %s, %s)""",[nombre, descripcion,idusuario,cambio, estado, fecha, categoria, filename])
    db.commit()
    db.close()
    return redirect(url_for('index'))

@app.route('/solicitudtrueque/<idproducto>')
def solicitud_truque(idproducto):
    if 'user' in session:
        tittle = "Solicitud de trueque"
        idproducto = idproducto
        ids.append(idproducto)
        db = sql.connect(**config)
        cursor = db.cursor()
        cursor.execute("""SELECT idusuario FROM productos WHERE idproducto=%s""",[idproducto])
        idusuario_dueno = cursor.fetchone()[0]
        db.close()
        idusuario_solicitante = session['user']

        if idusuario_solicitante == idusuario_dueno:
            return render_template('solicitud_trueque.html', tittle=tittle, mismo=1, user=1, solicitud=1)

        tittle = "Solicitud de treque"
        return render_template('solicitud_trueque.html', tittle=tittle, idproducto=idproducto, user=1)
        
    return redirect(url_for('index'))


@app.route('/trueque', methods=['POST'])
def trueque():
    producto = ids[0]
    solicitante = session['user']
    cambio = request.form.get('ofrezco')
    descripcion = request.form.get('descripcion')
    db = sql.connect(**config)
    cursor = db.cursor()
    cursor.execute("""SELECT idusuario FROM productos where idproducto=%s""",[producto])
    dueno = cursor.fetchone()[0]
    cursor.execute("""SELECT nombre, email FROM usuarios WHERE idusuarios=%s""",[dueno])
    datos_dueno = cursor.fetchall()
    nombre_dueno = datos_dueno[0][0]
    email_dueno = datos_dueno[0][1]

    cursor.execute("""SELECT nombre,email,celular FROM usuarios WHERE idusuarios=%s""",[solicitante])
    datos_ofrece = cursor.fetchall()
    nombre_ofrece = datos_ofrece[0][0]
    email_ofrece = datos_ofrece[0][1]
    celular_ofrece = datos_ofrece[0][2]


    cursor.execute("""SELECT nombre FROM productos WHERE idproducto=%s""",[producto])
    nombre_producto = cursor.fetchone()[0]

    cursor.execute("""INSERT INTO procesos_trueque(usuario_dueno, usuario_solicitante, producto, datos_cambio_descripcion, datos_cambio_ofrezco) VALUES(%s,%s,%s, %s, %s)""",[dueno, solicitante, producto, descripcion, cambio])
    db.commit()
    
    cursor.execute("""SELECT idproceso FROM procesos_trueque WHERE producto=%s""", [producto])
    id_proceso = cursor.fetchone()[0]

    db.close()
    subject = "Solicitud de trueque."
    mensaje = f"""
    <html>
        <body>
            <p style="text-align: center;"><span style="color: #ff0000;"><strong>Hola {nombre_dueno}</strong></span></p>
            <p"><b>{nombre_ofrece}</b> está interesado en cambiarte <b>{nombre_producto}</b> por
            <b>{cambio}</b>, con las siguientes especificaciones: <b>{descripcion}</b>.<br>
            Métodos de contacto:</p>
            <ul>
            <li>Correo: {email_ofrece}</li>
            <li>Celular: {celular_ofrece}</li>
            </ul>
            <p><a style="color:green;" href="http://127.0.0.1:5000/procesotrueque/{id_proceso}?status=acepted">Aceptar</a></p>
            <p><a style="color:red;" href="http://127.0.0.1:5000/procesotrueque/{id_proceso}?status=denied">Denegar</a></p>
        </body>
    </html>
    """
    envio_correo(mensaje, subject, email_dueno)
    return render_template("confirma.html", solicitud=1, user=1, tittle='Correo enviado')
# TODO Crear ruta para actualizar datos

@app.route('/procesotrueque/<id_proceso>', methods=['POST', 'GET'])
def proceso_trueque(id_proceso):
    id_proceso = id_proceso
    status = request.args.get('status')
    status = 1 if status=='acepted' else 0
    db = sql.connect(**config)
    cursor = db.cursor()
    cursor.execute("""SELECT usuario_dueno, usuario_solicitante, producto from procesos_trueque WHERE idproceso=%s""", [id_proceso])
    datos = cursor.fetchall()
    usuario_dueno = datos[0][0]
    usuario_solicitante = datos[0][1]
    producto = datos[0][2]

    cursor.execute("""SELECT nombre, descripcion, cambiarpor, img FROM productos WHERE idproducto=%s """,[producto])
    datos_producto = cursor.fetchall()

    cursor.execute("""SELECT datos_cambio_descripcion, datos_cambio_ofrezco FROM procesos_trueque WHERE idproceso = %s""",[id_proceso])
    datos_cambio = cursor.fetchall()

    cursor.execute("""SELECT nombre, email, celular, direccion FROM usuarios WHERE idusuarios=%s """,[usuario_solicitante])
    datos_solicitante = cursor.fetchall()

    cursor.execute("""SELECT nombre, email, celular, direccion FROM usuarios WHERE idusuarios=%s """,[usuario_dueno])
    datos_dueno = cursor.fetchall()
    
    db.close()
    if status == 0:
        mensaje = f"""
    <html>
        <body>
            <p style="text-align: center;"><span style="color: #ff0000;"><strong>Hola {datos_solicitante[0][0]}</strong></span></p>
            <p"><b>{datos_dueno[0][0]}</b> ha respondido a tu solicitud de trueque.
            <br>
            <p><a style="color:green;" href="http://127.0.0.1:5000/procesotrueque/{id_proceso}?status=denied"">Ver respuesta.</a></p>
        </body>
    </html>
    """
    elif status == 1:
        mensaje = f"""
    <html>
        <body>
            <p style="text-align: center;"><span style="color: #ff0000;"><strong>Hola {datos_solicitante[0][0]}</strong></span></p>
            <p"><b>{datos_dueno[0][0]}</b> ha respondido a tu solicitud de trueque.
            <br>
            <p><a style="color:green;" href="http://127.0.0.1:5000/procesotrueque/{id_proceso}?status=acepted"">Ver respuesta.</a></p>
        </body>
    </html>
    """
    envio_correo(mensaje, "Respuesta a solicitud dde trueque.", datos_solicitante[0][1])
    
    if status == 1:
        fecha = date.today().strftime('%d/%m/%Y')
        db = sql.connect(**config)
        cursor = db.cursor()
        cursor.execute("""UPDATE productos SET estado='0', canjeadopor=%s, fecha_canje=%s WHERE idproducto=%s""",[usuario_solicitante, fecha, producto])
        db.commit()
        db.close()

    tittle = "Proceso de trueque"
    usuario_sesion = str(session['user'])

    if usuario_sesion == str(usuario_dueno) or usuario_sesion == str(usuario_solicitante):    
        return render_template('procesos_trueque.html', tittle=tittle, status=status, datos_producto=datos_producto, datos_cambio=datos_cambio, datos_solicitante=datos_solicitante, datos_dueno=datos_dueno)
   
    tittle = 'No autorizado'
    return render_template('error.html', tittle=tittle)


def envio_correo(mensaje, subject, email):

    # Creamos objeto Multipart, quien será el recipiente que enviaremos
    msg = MIMEMultipart()
    msg['From'] = "getitjohguia@outlook.com"
    msg['To'] = email
    msg['Subject'] = subject

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



if __name__ == '__main__':
    app.run(debug=True, port=5000)