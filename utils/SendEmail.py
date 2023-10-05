from email.message import EmailMessage
import smtplib
from email.mime.text import MIMEText

from ecommerceHardcoregamesBack import settings


# Create the base text message.
class SendEmail:
    def __int__(self, email_text, subject_email, to):
        remitente = settings.FROM_EMAIL
        destinatario = to
        mensaje = email_text
        email = EmailMessage()
        email["From"] = remitente
        email["To"] = destinatario
        email["Subject"] = subject_email
        email.set_content(mensaje, subtype="html")
        smtp = smtplib.SMTP_SSL("smtp.gmail.com")
        smtp.login(remitente, settings.PASS_SMTP)
        smtp.sendmail(remitente, destinatario, email.as_string())
        smtp.quit()