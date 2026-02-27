import os
import resend

class EmailSender:
    def __init__(self):
        # RESEND_API_KEY debe estar configurada en el panel de Render -> Environment
        self.api_key = os.environ.get("RESEND_API_KEY")
        resend.api_key = self.api_key
        
        # Una vez verifiques tu dominio, cambia 'onboarding@resend.dev' 
        # por algo como 'citas@tu-dominio.com'
        self.sender_email = "onboarding@resend.dev"

    def enviar_confirmacion(self, correo_cliente, nombre, fecha, hora, profesional):
        if not self.api_key:
            print("❌ ERROR: No se encontró RESEND_API_KEY en las variables de entorno.")
            return

        try:
            params = {
                "from": f"Blessed Barbershop <{self.sender_email}>",
                "to": [correo_cliente],
                "subject": "💈 Cita Confirmada - Blessed Barbershop",
                "html": f"""
                <div style="font-family: sans-serif; border: 1px solid #ddd; padding: 20px; border-radius: 10px; max-width: 500px;">
                    <h2 style="color: #333; text-align: center;">¡Hola {nombre}!</h2>
                    <p style="text-align: center;">Tu cita ha sido agendada con éxito en <strong>Blessed Barbershop</strong>.</p>
                    <hr style="border: 0; border-top: 1px solid #eee;">
                    <p><strong>✂️ Barbero:</strong> {profesional}</p>
                    <p><strong>📅 Fecha:</strong> {fecha}</p>
                    <p><strong>⏰ Hora:</strong> {hora}</p>
                    <p><strong>📍 Ubicación:</strong> Calle 38 sur 34-22 Envigado</p>
                    <hr style="border: 0; border-top: 1px solid #eee;">
                    <p style="font-size: 0.8em; color: #666; text-align: center;">Si necesitas reprogramar, por favor avísanos con tiempo. ¡Te esperamos!</p>
                </div>
                """,
            }

            r = resend.Emails.send(params)
            print(f"✅ Correo enviado exitosamente vía Resend.")
        except Exception as e:
            print(f"❌ Error al enviar con Resend: {str(e)}")
