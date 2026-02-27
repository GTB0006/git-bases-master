from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import get_connection
from datetime import datetime, time
import os
from dotenv import load_dotenv

load_dotenv()

from email_sender import EmailSender
from calendar_sender import CalendarSender

app = FastAPI(title="API Barbería SaaS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

email_sender = EmailSender()
calendar_sender = CalendarSender()

HORA_APERTURA = time(9, 0)
HORA_CIERRE = time(22, 0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/frontend", StaticFiles(directory=os.path.join(BASE_DIR, "frontend")), name="frontend")

@app.get("/")
def index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))

# ======================================================
# LISTAR BARBEROS
# ======================================================
@app.get("/barberos/{barberia_id}")
def listar_barberos(barberia_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT id, nombre, foto_url FROM barberos WHERE barberia_id = %s AND activo = TRUE"
        cursor.execute(query, (barberia_id,))
        return [{"id": r[0], "nombre": r[1], "foto_url": r[2]} for r in cursor.fetchall()]
    finally:
        conn.close()

# ======================================================
# CREAR RESERVA
# ======================================================
@app.post("/reservas")
def crear_reserva(
    barberia_id: int,
    barbero_id: int,
    cliente_nombre: str,
    cliente_email: str,
    cliente_telefono: str,
    servicio: str,
    fecha: str,
    hora: str,
    background_tasks: BackgroundTasks
):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # 1. Validaciones
        hora_obj = datetime.strptime(hora, "%H:%M").time()
        if not (HORA_APERTURA <= hora_obj < HORA_CIERRE):
            raise HTTPException(status_code=400, detail="La barbería está cerrada")

        # 2. Verificar disponibilidad (Rango de 1 hora)
        # Buscamos si existe alguna cita entre (hora solicitada - 59 min) y (hora solicitada + 59 min)
        cursor.execute("""
            SELECT id FROM reservas 
            WHERE barberia_id = %s 
            AND barbero_id = %s 
            AND fecha = %s 
            AND (hora::time, interval '1 hour') OVERLAPS (%s::time, interval '1 hour')
        """, (barberia_id, barbero_id, fecha, hora))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El barbero ya tiene una cita en este rango de tiempo.")
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Horario no disponible")

        # 3. Guardar en Base de Datos
        cursor.execute("""
            INSERT INTO reservas (barberia_id, barbero_id, cliente_nombre, cliente_email, cliente_telefono, servicio, fecha, hora)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (barberia_id, barbero_id, cliente_nombre, cliente_email, cliente_telefono, servicio, fecha, hora))
        
        conn.commit()

        # 4. Datos para notificaciones
        cursor.execute("SELECT nombre FROM barberos WHERE id = %s", (barbero_id,))
        res = cursor.fetchone()
        profesional = res[0] if res else "Barbero"

        # 5. Envíos
        try:
            email_sender.enviar_confirmacion(cliente_email, cliente_nombre, fecha, hora, profesional)
        except Exception as e:
            print(f"❌ Error email: {e}")

        background_tasks.add_task(calendar_sender.crear_evento, cliente_email, cliente_nombre, fecha, hora, profesional)

        return {"mensaje": "¡Reserva creada con éxito!"}

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ======================================================
# LISTAR RESERVAS
# ======================================================
@app.get("/reservas/{barberia_id}")
def listar_reservas(barberia_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.cliente_nombre, r.servicio, r.fecha, r.hora, b.nombre
            FROM reservas r
            JOIN barberos b ON r.barbero_id = b.id
            WHERE r.barberia_id = %s
            ORDER BY r.fecha DESC LIMIT 10
        """, (barberia_id,))
        return [
            {
                "cliente": r[0], 
                "servicio": r[1], 
                "fecha": str(r[2]), 
                "hora": str(r[3]), 
                "barbero": r[4]
            } for r in cursor.fetchall()
        ]
    finally:
        conn.close()
