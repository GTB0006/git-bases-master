import os
import smtplib
from email.message import EmailMessage

class EmailSender:
    def __init__(self):
        self.email = os.getenv("EMAIL_USER", "blessedbarbershopenv@gmail.com")
        # Asegúrate de que no haya espacios en el password
        self.password = os.getenv("EMAIL_PASSWORD", "dkkgsqhzizbyifyi").strip()

    def enviar_confirmacion(self, correo_cliente, nombre, fecha, hora, profesional):
        try:
            msg = EmailMessage()
            msg["Subject"] = "Confirmación de Reserva - Blessed Barbershop"
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

            # CAMBIO CLAVE: Usar SMTP_SSL y puerto 465
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            
            print(f"✅ Correo enviado exitosamente a {correo_cliente}")
        except Exception as e:
            print(f"❌ Error real enviando correo: {str(e)}")
            raise e
