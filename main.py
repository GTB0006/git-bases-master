from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
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

# ======================================================
# INICIAR SERVICIOS
# ======================================================

email_sender = EmailSender()
calendar_sender = CalendarSender()

HORA_APERTURA = time(9, 0)
HORA_CIERRE = time(22, 0)

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
# LISTAR BARBEROS
# ======================================================

@app.get("/barberos/{barberia_id}")
def listar_barberos(barberia_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT id, nombre, horario_inicio, horario_fin, foto_url 
            FROM barberos 
            WHERE barberia_id = %s AND activo = TRUE
        """
        cursor.execute(query, (barberia_id,))
        rows = cursor.fetchall()
        
        return [
            {
                "id": r[0],
                "nombre": r[1],
                "horario_inicio": str(r[2]),
                "horario_fin": str(r[3]),
                "foto_url": r[4]
            }
            for r in rows
        ]
    except Exception as e:
        print(f"ERROR CRÍTICO DB: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ======================================================
# CREAR RESERVA (FORZANDO LOGS DE EMAIL)
# ======================================================

@app.post("/reservas")
def crear_reserva(
    barberia_id: int,
    barbero_id: int,
    cliente_nombre: str,
    cliente_email: str,
    fecha: str,
    hora: str,
    background_tasks: BackgroundTasks
):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # 1. Validaciones de horario
        hora_obj = datetime.strptime(hora, "%H:%M").time()
        if not (HORA_APERTURA <= hora_obj < HORA_CIERRE):
            raise HTTPException(status_code=400, detail="La barbería está cerrada")

        # 2. Verificar disponibilidad
        cursor.execute("""
            SELECT id FROM reservas
            WHERE barberia_id = %s AND barbero_id = %s AND fecha = %s AND hora = %s
        """, (barberia_id, barbero_id, fecha, hora))

        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Horario no disponible")

        # 3. Guardar en Base de Datos (Supabase)
        cursor.execute("""
            INSERT INTO reservas (barberia_id, barbero_id, cliente_nombre, cliente_email, fecha, hora)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (barberia_id, barbero_id, cliente_nombre, cliente_email, fecha, hora))
        
        conn.commit()

        # 4. Obtener datos para notificaciones
        cursor.execute("SELECT nombre FROM barberos WHERE id = %s", (barbero_id,))
        res = cursor.fetchone()
        profesional = res[0] if res else "Barbero"

        # --- PRUEBA DE FUEGO: ENVÍO DIRECTO ---
        print(f"--- Iniciando intento de envío de email para {cliente_email} ---")
        try:
            email_sender.enviar_confirmacion(cliente_email, cliente_nombre, fecha, hora, profesional)
            print(f"✅ Email procesado en el flujo principal")
        except Exception as e:
            print(f"❌ Error capturado en main.py al enviar email: {e}")

        # El calendario se queda en background porque ya vimos que sí funciona
        background_tasks.add_task(calendar_sender.crear_evento, cliente_email, cliente_nombre, fecha, hora, profesional)

        return {"mensaje": "¡Reserva creada con éxito!"}

    except Exception as e:
        print(f"ERROR EN PROCESO DE RESERVA: {str(e)}")
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
            SELECT r.cliente_nombre, r.cliente_email, r.fecha, r.hora, b.nombre
            FROM reservas r
            JOIN barberos b ON r.barbero_id = b.id
            WHERE r.barberia_id = %s
            ORDER BY r.fecha DESC, r.hora DESC
            LIMIT 10
        """, (barberia_id,))

        return [
            {
                "cliente": r[0],
                "correo": r[1],
                "fecha": str(r[2]),
                "hora": str(r[3]),
                "profesional": r[4]
            }
            for r in cursor.fetchall()
        ]
    except Exception as e:
        return []
    finally:
        conn.close()
