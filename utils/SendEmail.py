from email.message import EmailMessage
import smtplib


# Create the base text message.
class SendEmail:
    def __int__(self, ):
        remitente = "jhoan0498@gmail.com"
        destinatario = "jhoanma0498@gmail.com"
        mensaje = "¡Hola, mundo!"
        email = EmailMessage()
        email["From"] = remitente
        email["To"] = destinatario
        email["Subject"] = "Correo de prueba"
        email.set_content(mensaje)
        smtp = smtplib.SMTP_SSL("smtp.gmail.com")
        smtp.login(remitente, "bbcg cluw zlia hhui ")
        smtp.sendmail(remitente, destinatario, email.as_string())
        smtp.quit()