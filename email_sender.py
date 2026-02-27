import os
import smtplib
import ssl
from email.message import EmailMessage

class EmailSender:
    def __init__(self):
        # Usamos las variables de Render. Si no están, usamos los valores que pusiste
        self.email = os.getenv("EMAIL_USER", "blessedbarbershopenv@gmail.com")
        self.password = os.getenv("EMAIL_PASSWORD", "szpmoziwisyyodav").strip()

    def enviar_confirmacion(self, correo_cliente, nombre, fecha, hora, profesional):
        msg = EmailMessage()
        msg["Subject"] = "Confirmación de Reserva - Blessed Barbershop"
        msg["From"] = self.email
        msg["To"] = correo_cliente

        msg.set_content(f"""
Hola {nombre},

Tu reserva ha sido confirmada con éxito.

Detalles:
Barbero: {profesional}
Fecha: {fecha}
Hora: {hora}

¡Te esperamos! 💈
""")

        try:
            # Usamos la configuración de puerto 587 que te funcionaba antes
            context = ssl.create_default_context()
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                server.send_message(msg)
            print(f"✅ Correo enviado correctamente a {correo_cliente}")
        except Exception as e:
            print(f"❌ ERROR ENVIANDO CORREO: {str(e)}")
