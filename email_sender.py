import os
import resend

class EmailSender:
    def __init__(self):
        # Configura tu API Key de Resend aquí o en Render Environment
        resend.api_key = os.environ.get("RESEND_API_KEY", "re_Tb8AWwzR_Q5f6HQTnpNPLyKbi3hEaZ4CZ")
        self.sender_email = "onboarding@resend.dev" # Luego puedes validar tu dominio

    def enviar_confirmacion(self, correo_cliente, nombre, fecha, hora, profesional):
        try:
            params = {
                "from": f"Blessed Barbershop <{self.sender_email}>",
                "to": [correo_cliente],
                "subject": "💈 Cita Confirmada - Blessed Barbershop",
                "html": f"""
                <div style="font-family: sans-serif; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #333;">¡Hola {nombre}!</h2>
                    <p>Tu cita ha sido agendada con éxito.</p>
                    <hr>
                    <p><strong>✂️ Barbero:</strong> {profesional}</p>
                    <p><strong>📅 Fecha:</strong> {fecha}</p>
                    <p><strong>⏰ Hora:</strong> {hora}</p>
                    <hr>
                    <p style="font-size: 0.8em; color: #666;">Te esperamos en Calle 38 sur 34-22 Envigado.</p>
                </div>
                """,
            }

            r = resend.Emails.send(params)
            print(f"✅ Correo enviado vía API Resend: {r}")
        except Exception as e:
            print(f"❌ Error con Resend: {str(e)}")
