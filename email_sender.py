import os
import smtplib
import ssl
from email.message import EmailMessage

class EmailSender:
    def __init__(self):
        # Render prioriza el panel de Environment
        self.email = os.environ.get("EMAIL_USER", "blessedbarbershopenv@gmail.com")
        self.password = os.environ.get("EMAIL_PASSWORD", "szpmoziwisyyodav").strip()

    def enviar_confirmacion(self, correo_cliente, nombre, fecha, hora, profesional):
        if not self.password:
            print("❌ ERROR: Contraseña no configurada")
            return

        msg = EmailMessage()
        msg["Subject"] = "💈 Confirmación de tu Cita - Blessed Barbershop"
        msg["From"] = self.email
        msg["To"] = correo_cliente
        
        # Cuerpo del mensaje
        cuerpo = f"""
Hola {nombre},

¡Tu cita ha sido agendada con éxito!

📍 Lugar: Calle 38 sur 34-22 Envigado
✂️ Barbero: {profesional}
📅 Fecha: {fecha}
⏰ Hora: {hora}

Si necesitas cancelar o reprogramar, por favor contáctanos con anticipación.
¡Te esperamos!
"""
        msg.set_content(cuerpo)

        try:
            # Usamos SSL directo en el puerto 465
            context = ssl.create_default_context()
            # Timeout añadido para evitar que se quede colgado
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=15) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            print(f"✅ Correo enviado con éxito a {correo_cliente}")
        except Exception as e:
            print(f"❌ Fallo al enviar correo: {str(e)}")
