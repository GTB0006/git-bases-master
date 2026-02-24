import os
import smtplib
from email.message import EmailMessage


class EmailSender:

    def __init__(self):
        self.email = "cristiancrjm19@gmail.com"
        self.password = "lkwhorhekctfqvqm"  # SIN espacios
        

    def enviar_confirmacion(self, correo_cliente, nombre, fecha, hora, profesional):

        msg = EmailMessage()
        msg["Subject"] = "Confirmación de Reserva - Barbería"
        msg["From"] = self.email
        msg["To"] = correo_cliente

        msg.set_content(f"""
Hola {nombre},

Tu reserva fue confirmada.

Barbero: {profesional}
Fecha: {fecha}
Hora: {hora}

Te esperamos 💈
""")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)

        print("Correo enviado correctamente")