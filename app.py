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
from werkzeug.utils import append_slash_redirect, secure_filename
from datetime import date
from os import path
import bcrypt

# ------------------------------ Configuración ------------------------------

# Se configura el Flask name como app
app = Flask(__name__)

# Se crea la secret key utilizada para cifrar los datos entregados a las cookies.
app.secret_key = "I5@G2HqM<K#{1]{RN=)bapgSzg1a2+d9?1Hhgx]4[?T~<T&S<]5bkBw{4R;hK+wcNEBVj#Bmy]tyW?i]"

# Se define la ruta para guardar los archivos y los tipos permitidos. 
upload_folder = "./static/imgs_productos"
allowed_extensions = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = upload_folder

# Se hace la conexión con la base de datos.
config = {
  'user': 'root',
  'password': '',
  'host': 'localhost',
  'database': 'get_it',
  'raise_on_warnings': True
}

# ------------------------------ Creación de rutas ------------------------------
def recoger_nombre(idusuarios):
    """Funcion que recoge el nombre de usuario de la base de datos y lo devuelve"""
    db = sql.connect(**config)
    cursor = db.cursor()
    cursor.execute("""SELECT nombre FROM usuarios WHERE idusuarios=%s""",[idusuarios])
    dato = cursor.fetchone()[0]
    db.close
    nombre = ''
    for i in dato:
        if i != ' ':
            nombre += i

        elif i == ' ':
            break
    print(nombre)
    return nombre

def cerrar_sesion_link(idusuarios, id_session):
    """Funcion que cierra sesion si la redireccion del link esta con otro usuario"""
    if idusuarios == id_session:
        pass

    else:
        session.pop('user')
        session['user'] = idusuarios

# Index
@app.route('/')
def index():
    i = request.args.get('i')
    db = sql.connect(**config)
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM productos""")
    productos = cursor.fetchall()
    db.close
    contador = 0
    for x in range(len(productos)):
        if int(productos[x][6]) == 1:
            contador += 1

        else:
            contador -= 1

    if contador < 1:
        permitir = False

    else:
        permitir = True

    largor = len(productos)
    tittle = "Get It"
    if "user" in session:
        nombre_cuenta = recoger_nombre(session['user'])
        return render_template('index.html', tittle=tittle, user=True, productos=productos, largor=largor, nombre_cuenta=nombre_cuenta, permitir=permitir)

    return render_template('index.html', tittle=tittle, productos=productos, largor=largor, mismo=i,permitir=permitir)

# Interfaz de registro.
@app.route('/interfazregistro')
def interfaz_registro():
    error = request.args.get('i')
    tittle = "Registro"
    contrasena = request.args.get('contrasena')
    email = request.args.get('email')
    if "user" in session:
        tittle = "No autorizado"
        return render_template('error.html', error=True,tittle=tittle)
    return render_template('registro.html', tittle=tittle, contrasena=contrasena, email=email, i=error)

# Interfaz de login.
@app.route('/interfazlogin')
def interfaz_login():
    tittle = "Ingreso"
    usuario = request.args.get('usuario')
    clave = request.args.get('clave')
    email = request.args.get('email')
    if "user" in session:
        tittle = "No autorizado"
        return render_template('error.html', error=True,tittle=tittle)
    return render_template('ingreso.html', tittle=tittle, usuario=usuario, clave=clave)

# Interfaz de publicar. 
@app.route('/interfazpublicar')
def interfaz_publicar():
    tittle = "Publicar"
    if "user" in session:
        nombre_cuenta = recoger_nombre(session['user'])
        return render_template('publicar.html', tittle=tittle, user=1, nombre_cuenta=nombre_cuenta)

    tittle = "No autorizado"
    return render_template('error.html', error=True,tittle=tittle)


# ------------------------------ Creación de rutas lógicas ------------------------------
# Registro
@app.route('/registro', methods=['POST'])
def registro():
    
    if 'user' in session:
        tittle = "No autorizado"
        return render_template('error.html', error=True,tittle=tittle)
    
    else:
        email = request.form.get('email')
        contrasena = request.form.get('contrasena')
        contrasena2 = request.form.get('contrasena2')
        salt = bcrypt.gensalt()
        hash_password1 = bcrypt.hashpw(bytes(str(contrasena), encoding= 'utf-8'), salt)
        hash_password2 = bcrypt.hashpw(bytes(str(contrasena2), encoding= 'utf-8'), salt)
        nombre = request.form.get('nombre')
        documento = request.form.get('documento')
        direccion = request.form.get('direccion')
        celular = request.form.get('celular')

        db = sql.connect(**config)
        cursor = db.cursor()
        cursor.execute("""SELECT email from usuarios where email=%s""",[email])
        email_registrado = cursor.fetchall()
        
        if len(email_registrado) > 0:
            db.close()
            return redirect(url_for('interfaz_registro',email='invalid'))
        
        else:

            if hash_password1 == hash_password2:
                cursor.execute("""INSERT INTO usuarios(idusuarios,nombre,email,clave,celular,direccion, estado)
                VALUES (%s,%s, %s, %s, %s,%s, "0")""",
                [documento, nombre, email, hash_password1, celular,direccion])
                db.commit()
                db.close()
                mensaje = """
        <html>
        <body style="background-color:rgb(192, 192, 240);">
            <p style="text-align: center;color: #000000;font-weight: bold;font-size: 40px;">Confirma tu correo para poder seguir</p>
            <div style="display: flex;justify-content: center;">
                <div style="font-size: 30px;text-align: justify;">
                    <p>
                        Hola <b>{}</b>, gracias por registrarte en <b>Get It.</b>
                        <br>
                        Para tener acceso a nuestra página, dale click
                        <a style="text-decoration: none;color: blue;" href="http://127.0.0.1:5000/registrado/{}" rel="noopener">AQUI</a>
                        para confirmar tu usuario.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """.format(nombre, documento)
                subject = "Confirmación de correo"
                envio_correo(mensaje,subject,email)
                return render_template('confirma.html', tittle='Confirma tu correo electrónico', confirma=True, user=True)

            db.close()
            return redirect(url_for('interfaz_registro',contrasena='invalid'))


# Registro completado.
@app.route('/registrado/<id_usuario>')
def registrado(id_usuario):
    id_usuario = id_usuario
    db = sql.connect(**config)
    cursor = db.cursor()
    cursor.execute("""UPDATE usuarios SET estado=1 WHERE idusuarios=%s""",[id_usuario])
    db.commit()
    db.close()
    if 'user' in session:
        cerrar_sesion_link(id_usuario, session['user'])
    
    else:
        session["user"] = id_usuario

    return redirect(url_for('index'))

# Login
@app.route('/login', methods=['POST'])
def login():
    if 'user' in session:
        tittle = "No autorizado"
        return render_template('error.html', error=True,tittle=tittle)

    else:
        correo = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        try:
            db = sql.connect(**config)
            cursor = db.cursor()
            cursor.execute("""SELECT email, estado, clave, idusuarios from usuarios where email=%s""",[correo])
            datos = cursor.fetchone()
            email = datos[0]
            estado = datos[1]
            contrasena_bdd = datos[2]
            id_usuario = datos[3]
            db.close()

            if email:

                if estado == '1':

                    if email == correo:

                        if bcrypt.checkpw(contrasena.encode('utf8'), contrasena_bdd.encode('utf8')):
                            session["user"] = id_usuario
                            return redirect(url_for('index'))

                        db.close()
                        return redirect(url_for('interfaz_login',clave=0))
                        

                return render_template("confirma.html", confirma=1, user=1)

            db.close()
            return redirect(url_for('interfaz_login',usuario="Noregistrado"))

        except:
            return redirect(url_for('interfaz_login',usuario="Noregistrado"))
    
# Logout
@app.route('/logout')
def logout():
    if "user" in session:
        session.pop("user")
        return render_template('cerrar_sesion.html')
    
    else:
        tittle = "No autorizado"
        return render_template('error.html', error=True,tittle=tittle)

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
        nombre_cuenta = recoger_nombre(session['user'])
        return render_template('cuenta.html', user=True, tittle=tittle,idusuarios=idusuarios, nombre=nombre,correo=correo,celular=celular, direccion=direccion, nombre_cuenta=nombre_cuenta)

    tittle = 'No autorizado'
    return render_template('error.html', error=True,tittle=tittle)

@app.route('/publicar', methods=['POST'])
def publicar():
    if 'user' in session:
        categoria = request.form.get('PoS')
        nombre = request.form.get('encabezado')
        cambio = request.form.get('cambio')
        estado = 1
        descripcion = request.form.get('duser_message')
        f = request.files['file1']
        filename = secure_filename(f.filename)
        try:
            f.save(path.join(app.config['UPLOAD_FOLDER'], filename))
        except:
            pass
        fecha = date.today().strftime('%d/%m/%Y')
        db = sql.connect(**config)
        cursor = db.cursor()
        idusuario = session["user"]
        cursor.execute("""INSERT INTO productos(nombre, descripcion, idusuario, cambiarpor, estado, fecha_publ, categoria, img) values
        (%s, %s, %s, %s, %s, %s, %s, %s)""",[nombre, descripcion,idusuario,cambio, estado, fecha, categoria, filename])
        db.commit()
        db.close()
        return redirect(url_for('index'))

    else:
        tittle = "No autorizado"
        return render_template('error.html', error=True,tittle=tittle) 

@app.route('/solicitudtrueque/<idproducto>')
def solicitud_truque(idproducto):
    if 'user' in session:
        nombre_cuenta = recoger_nombre(session['user'])
        tittle = "Solicitud de trueque"
        idproducto = idproducto
        db = sql.connect(**config)
        cursor = db.cursor()
        cursor.execute("""SELECT idusuario FROM productos WHERE idproducto=%s""",[idproducto])
        idusuario_dueno = cursor.fetchone()[0]
        db.close()
        idusuario_solicitante = session['user']

        if idusuario_solicitante == idusuario_dueno:
            return render_template('solicitud_trueque.html', tittle=tittle, mismo=True, user=True, solicitud=True, nombre_cuenta=nombre_cuenta)

        return render_template('solicitud_trueque.html', tittle=tittle, idproducto=idproducto, user=True, nombre_cuenta=nombre_cuenta)
        
    return redirect(url_for('index',i=0))


@app.route('/trueque/<idpro>', methods=['POST'])
def trueque(idpro):
    idpro = idpro
    solicitante = session['user']
    cambio = request.form.get('ofrezco')
    descripcion = request.form.get('descripcion')
    db = sql.connect(**config)
    cursor = db.cursor()
    cursor.execute("""SELECT idusuario FROM productos where idproducto=%s""",[idpro])
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


    cursor.execute("""SELECT nombre FROM productos WHERE idproducto=%s""",[idpro])
    nombre_producto = cursor.fetchone()[0]

    cursor.execute("""INSERT INTO procesos_trueque(usuario_dueno, usuario_solicitante, producto, datos_cambio_descripcion, datos_cambio_ofrezco) VALUES(%s,%s,%s, %s, %s)""",[dueno, solicitante, idpro, descripcion, cambio])
    db.commit()
    
    cursor.execute("""SELECT idproceso FROM procesos_trueque WHERE producto=%s""", [idpro])
    id_proceso = cursor.fetchone()[0]

    db.close()
    subject = "Solicitud de trueque."
    mensaje = f"""
    <html>
    <body style="background-color:rgb(192, 192, 240);font-size: 20px;">
        <p style="text-align: center; font-weight: bold; font-size: 40px;">Hola {nombre_dueno}</strong></span></p>
        <p><strong>{nombre_ofrece}</strong> est&aacute; interesado en cambiarte <strong>{nombre_producto}</strong> por <strong>{cambio}</strong>, con las siguientes especificaciones: <br> <strong>{descripcion}</strong>.<br />M&eacute;todos de contacto:</p>
        <ul style="list-style-type:none;">
        <li><b>Correo:</b> {email_ofrece}</li>
        <li><b>Celular:</b> {celular_ofrece}</li>
        </ul>
        <center>
        <p><button style="position: absolute;text-decoration: none;padding-left: 10px;padding-right: 10px;font-weight: 300;color: #000000;background-color: #67b919;border-radius: 15px;padding:5px 10px 5px 10px;border: 3px solid #67b919;left:40%;"><a style="color:rgb(0, 0, 0); text-decoration:none; font-size: 15px;" href="http://127.0.0.1:5000/procesotrueque/{id_proceso}?status=acepted">Aceptar</a></button></p>
        <p><button style="position: absolute;text-decoration: none;padding-left: 10px;padding-right: 10px;font-weight: 300;color: #000000;background-color: #da4133;border-radius: 15px;padding:5px 10px 5px 10px;border: 3px solid #da4133;"><a style="color:rgb(0, 0, 0); text-decoration:none; font-size: 15px;" href="http://127.0.0.1:5000/procesotrueque/{id_proceso}?status=denied">Denegar</a></button></p>
        </center>
    </body>
</html>
    """
    envio_correo(mensaje, subject, email_dueno)
    return render_template("confirma.html", solicitud=1, user=1, tittle='Correo enviado')

@app.route('/actualizar')
def actualizar():
    if 'user' in session:
        nombre_cuenta = recoger_nombre(session['user'])
        idusuario = session['user']
        db = sql.connect(**config)
        cursor = db.cursor()
        cursor.execute("""SELECT nombre, email, celular, direccion FROM usuarios where idusuarios = %s""",[idusuario])
        datos = cursor.fetchone()
        db.close
        tittle = "Actualizar Datos"
        return render_template('actualizar_datos.html', tittle=tittle, idusuario=idusuario, datos=datos, user=True,nombre_cuenta=nombre_cuenta)

    tittle = 'No autorizado'
    return render_template('error.html', error=True,tittle=tittle)

@app.route('/actualizar_datos/<idusuario>', methods=['POST'])
def actualizar_datos(idusuario):

    if 'user' in session:
        idusuario = idusuario
        if int(session['user']) == int(idusuario):
            nombre = request.form.get('nombre')
            email = request.form.get('email')
            celular = request.form.get('celular')
            direccion = request.form.get('direccion')
            db = sql.connect(**config)
            cursor = db.cursor()
            cursor.execute("""UPDATE usuarios SET nombre=%s, email=%s, celular=%s, direccion=%s WHERE idusuarios=%s""",[nombre, email, celular, direccion, idusuario])
            db.commit()
            db.close()
            return render_template("cuenta.html", actualizacion=True)

    tittle = 'No autorizado'
    return render_template('error.html', error=True,tittle=tittle)


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
        <body style="background-color:rgb(192, 192, 240);">
            <p style="text-align: center;color: #000000;font-weight: bold;font-size: 40px;">Hola {datos_solicitante[0][0]}</p>
            <br>
            <div style="display: flex;justify-content: center;">
                <div style="font-size: 30px;text-align: justify;">
                    <p><b>{datos_dueno[0][0]}</b> ha respondido a tu solicitud de trueque.
                </div>
            </div>
            
            <br>
            <p style="text-align:center;"><button style="position: absolute;text-decoration: none;padding-left: 10px;padding-right: 10px;font-weight: 300;color: #000000;background-color: #67b919;border-radius: 15px;padding:5px 10px 5px 10px;border: 3px solid #67b919;left:40%;"><a style="color:rgb(0, 0, 0); text-decoration:none; font-size: 15px;" href="http://127.0.0.1:5000/procesotrueque/{id_proceso}?status=denied"">Ver respuesta.</a></button></p>
        </body>
    </html>
    """
    elif status == 1:
        mensaje = f"""
    <html>
        <body style="background-color:rgb(192, 192, 240);">
            <p style="text-align: center;color: #000000;font-weight: bold;font-size: 40px;">Hola {datos_solicitante[0][0]}</p>
            <br>
            <div style="display: flex;justify-content: center;">
                <div style="font-size: 30px;text-align: justify;">
                    <p><b>{datos_dueno[0][0]}</b> ha respondido a tu solicitud de trueque.
                </div>
            </div>
            
            <br>
            <p style="text-align:center;"><button style="position: absolute;text-decoration: none;padding-left: 10px;padding-right: 10px;font-weight: 300;color: #000000;background-color: #67b919;border-radius: 15px;padding:5px 10px 5px 10px;border: 3px solid #67b919;left:40%;"><a style="color:rgb(0, 0, 0); text-decoration:none; font-size: 15px;" href="http://127.0.0.1:5000/procesotrueque/{id_proceso}?status=acepted"">Ver respuesta.</a></button></p>
        </body>
    </html>
    """
    envio_correo(mensaje, "Respuesta a solicitud de trueque.", datos_solicitante[0][1])
    
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
        return render_template('procesos_trueque.html',solicitud=True, tittle=tittle, status=status, datos_producto=datos_producto, datos_cambio=datos_cambio, datos_solicitante=datos_solicitante, datos_dueno=datos_dueno)
   
    tittle = 'No autorizado'
    return render_template('error.html', error=True,tittle=tittle)

@app.route("/misproductos", methods=["GET"])
def ver_productos():
    if 'user' in session:
        idusuarios = session['user']
        db = sql.connect(**config)
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM productos WHERE idusuario=%s""",[idusuarios])
        productos = cursor.fetchall()
        db.close
        contador = 0
        for x in range(len(productos)):
            if int(productos[x][6]) == 1:
                contador += 1

            else:
                contador -= 1

        if contador < 1:
            permitir = False

        else:
            permitir = True

        largor = len(productos)
        tittle = "Mis productos"
        
        nombre_cuenta = recoger_nombre(session['user'])
        return render_template('mis_productos.html', tittle=tittle, user=True, productos=productos, largor=largor, nombre_cuenta=nombre_cuenta, permitir=permitir)
    
    tittle = 'No autorizado'
    return render_template('error.html', error=True,tittle=tittle)

@app.route("/eliminar_producto/<idproducto>")
def eliminar_producto(idproducto):
    if 'user' in session:
        idproducto = idproducto
        db = sql.connect(**config)
        cursor = db.cursor()
        cursor.execute("""DELETE FROM productos WHERE idproducto=%s""",[idproducto])
        db.commit()
        db.close()
        return redirect(url_for('ver_productos'))

    else:
        tittle = 'No autorizado'
        return render_template('error.html', error=True,tittle=tittle)

@app.route("/editar_producto/<idproducto>")
def editar_producto(idproducto):
    if 'user' in session:
        nombre_cuenta = recoger_nombre(session['user'])
        idproducto = idproducto
        db = sql.connect(**config)
        cursor = db.cursor()
        cursor.execute("""SELECT nombre, descripcion, cambiarpor FROM productos WHERE idproducto=%s""",[idproducto])
        datos = cursor.fetchone()
        db.close()
        nombre = datos[0]
        descripcion = datos[1]
        cambiarpor = datos[2]
        tittle = 'Editar producto'
        return render_template('editar_producto.html', idproducto=idproducto, tittle=tittle, nombre_cuenta=nombre_cuenta, nombre=nombre, descripcion=descripcion,cambiarpor=cambiarpor)

    tittle = 'No autorizado'
    return render_template('error.html', error=True,tittle=tittle)

@app.route("/actualizar_producto/<idproducto>", methods=['POST'])
def actualizar_producto(idproducto):
    idproducto = idproducto
    nombre = request.form.get("encabezado")
    cambio = request.form.get("cambio")
    descripcion = request.form.get("duser_message")
    categoria = request.form.get("PoS")
    db = sql.connect(**config)
    cursor = db.cursor()
    cursor.execute("""UPDATE productos SET nombre=%s, descripcion=%s, cambiarpor=%s, categoria=%s WHERE idproducto=%s""",[nombre,descripcion, cambio, categoria, idproducto])
    db.commit()
    db.close()
    return redirect(url_for('ver_productos'))


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