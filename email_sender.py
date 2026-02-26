import os
import smtplib
from email.message import EmailMessage

class EmailSender:
    def __init__(self):
        # Lee de la variable de entorno, si no existe usa el valor por defecto
        self.email = os.getenv("EMAIL_USER", "blessedbarbershopenv@gmail.com")
        self.password = os.getenv("EMAIL_PASSWORD", "dkkgsqhzizbyifyi") 

    def enviar_confirmacion(self, correo_cliente, nombre, fecha, hora, profesional):
        msg = EmailMessage()
        msg["Subject"] = "Confirmación de Reserva - Blessed Barbershop" # Nombre más profesional
        msg["From"] = self.email
        msg["To"] = correo_cliente

        msg.set_content(f"""
Hola {nombre},

Tu reserva en Blessed Barbershop ha sido confirmada con éxito.

Detalles de la cita:
---------------------------
Barbero: {profesional}
Fecha: {fecha}
Hora: {hora}
---------------------------

¡Te esperamos para brindarte el mejor servicio! 💈
""")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)

        print(f"✅ Correo de confirmación enviado a {correo_cliente}")
