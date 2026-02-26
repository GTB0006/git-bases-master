from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import get_connection
from datetime import datetime, time
import os
from dotenv import load_dotenv

load_dotenv()

#from whatsapp_sender import WhatsAppSender
from email_sender import EmailSender
from calendar_sender import CalendarSender

app = FastAPI(title="API Barbería SaaS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# TEST CONEXION BD
# ======================================================

@app.get("/test-db")
def test_db():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "Conectado correctamente a PostgreSQL"}
    except Exception as e:
        return {"error": str(e)}

# ======================================================
# INICIAR SERVICIOS
# ======================================================

#whatsapp = None
email_sender = EmailSender()
calendar_sender = CalendarSender()

#@app.on_event("startup")
#def startup_event():
 #   global whatsapp
  #  whatsapp = WhatsAppSender()

#@app.on_event("shutdown")
#def shutdown_event():
 #   global whatsapp
  #  if whatsapp:
   #     whatsapp.cerrar()

# ======================================================
# ESTÁTICOS
# ======================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/frontend",
    StaticFiles(directory=os.path.join(BASE_DIR, "frontend")),
    name="frontend"
)

@app.get("/")
def index():
    return FileResponse(
        os.path.join(BASE_DIR, "frontend", "index.html")
    )

# ======================================================
# HORARIOS
# ======================================================

HORA_APERTURA = time(9, 0)
HORA_CIERRE = time(22, 0)

# ======================================================
# LISTAR BARBEROS POR BARBERIA
# ======================================================

@app.get("/barberos/{barberia_id}")
def listar_barberos(barberia_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre, horario_inicio, horario_fin, foto_url
            FROM barberos
            WHERE barberia_id = %s AND activo = TRUE
        """, (barberia_id,))

        return [
            {
                "barbero_id": r[0],
                "nombre": r[1],
                "horario_inicio": str(r[2]),
                "horario_fin": str(r[3]),
                "foto_url": r[4] # <-- Nueva línea
            }
            for r in cursor.fetchall()
        ]
    finally:
        conn.close()
# ======================================================
# CREAR RESERVA (SaaS Multi-tenant)
# ======================================================

@app.post("/reservas")
def crear_reserva(
    barberia_id: int,
    barbero_id: int,
    cliente_nombre: str,
    cliente_email: str,
    fecha: str,
    hora: str
):

    conn = get_connection()
    try:
        cursor = conn.cursor()

        hora_inicio = datetime.strptime(hora, "%H:%M").time()

        if not (HORA_APERTURA <= hora_inicio < HORA_CIERRE):
            raise HTTPException(
                status_code=400,
                detail="Horario fuera del rango permitido"
            )

        # Verificar si ya está ocupado
        cursor.execute("""
            SELECT id FROM reservas
            WHERE barberia_id = %s
            AND barbero_id = %s
            AND fecha = %s
            AND hora = %s
        """, (barberia_id, barbero_id, fecha, hora))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Horario ya ocupado"
            )

        # Insertar reserva
        cursor.execute("""
            INSERT INTO reservas
            (barberia_id, barbero_id, cliente_nombre, cliente_email, fecha, hora)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            barberia_id,
            barbero_id,
            cliente_nombre,
            cliente_email,
            fecha,
            hora
        ))

        conn.commit()

        # Obtener nombre del barbero
        cursor.execute("""
            SELECT nombre FROM barberos
            WHERE id = %s
        """, (barbero_id,))

        profesional = cursor.fetchone()[0]

        mensaje = (
            f"Hola {cliente_nombre} 👋\n"
            f"Tu reserva fue confirmada\n"
            f"Barbero: {profesional}\n"
            f"Fecha: {fecha}\n"
            f"Hora: {hora}\n"
            f"Te esperamos 💈"
        )

        # WhatsApp
        #if whatsapp:
            # aquí deberías pedir teléfono si lo quieres usar
         #   pass

        # Email
        email_sender.enviar_confirmacion(
            cliente_email,
            cliente_nombre,
            fecha,
            hora,
            profesional
        )

        # Calendar
        calendar_sender.crear_evento(
            cliente_email,
            cliente_nombre,
            fecha,
            hora,
            profesional
        )

        return {"mensaje": "Reserva creada correctamente"}

    finally:
        conn.close()

# ======================================================
# LISTAR RESERVAS POR BARBERIA
# ======================================================

@app.get("/reservas/{barberia_id}")
def listar_reservas(barberia_id: int):

    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT cliente_nombre, cliente_email, fecha, hora
            FROM reservas
            WHERE barberia_id = %s
            ORDER BY fecha, hora
        """, (barberia_id,))

        return [
            {
                "cliente": r[0],
                "correo": r[1],
                "fecha": str(r[2]),
                "hora": str(r[3])
            }
            for r in cursor.fetchall()
        ]

    finally:
        conn.close()
