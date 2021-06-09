import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def confirmar_correo(email):

    # Plantilla del mensaje

    mensaje = """
<html>
    <body>
        <p style="text-align: center;"><span style="color: #ff0000;"><strong>Confirma tu correo para poder seguir</strong></span></p>
        <p style="text-align: center;"><strong></strong></p>
        <p><a href="http://127.0.0.1:5000/login" target="_blank" rel="noopener">Confirma</a></p>
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