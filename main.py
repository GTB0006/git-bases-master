from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import get_connection
from datetime import datetime, time
import pyodbc
import os

from whatsapp_sender import WhatsAppSender

app = FastAPI(title="API Barbería")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# INICIAR WHATSAPP UNA SOLA VEZ
# ======================================================

whatsapp = None

@app.on_event("startup")
def startup_event():
    global whatsapp
    print("Iniciando servicio de WhatsApp...")
    whatsapp = WhatsAppSender()

@app.on_event("shutdown")
def shutdown_event():
    global whatsapp
    if whatsapp:
        whatsapp.cerrar()

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
# CLIENTES
# ======================================================

@app.post("/clientes")
def crear_o_obtener_cliente(nombre: str, telefono: str, cedula: str):

    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT ClienteId FROM Clientes WHERE Cedula = ?",
            (cedula,)
        )
        row = cursor.fetchone()

        if row:
            return {"cliente_id": row[0]}

        cursor.execute("""
            INSERT INTO Clientes (Nombre, Telefono, Cedula)
            OUTPUT INSERTED.ClienteId
            VALUES (?, ?, ?)
        """, (nombre, telefono, cedula))

        cliente_id = cursor.fetchone()[0]
        conn.commit()

        return {"cliente_id": cliente_id}

    finally:
        conn.close()

# ======================================================
# PROFESIONALES
# ======================================================

@app.get("/profesionales")
def listar_profesionales():

    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ProfesionalId, Nombre, Imagen
            FROM Profesionales
            WHERE Activo = 1
        """)

        return [
            {
                "profesional_id": r[0],
                "nombre": r[1],
                "imagen": r[2]
            }
            for r in cursor.fetchall()
        ]

    finally:
        conn.close()

# ======================================================
# RESERVAS
# ======================================================

@app.post("/reservas")
def crear_reserva(cliente_id: int, profesional_id: int, fecha: str, hora: str):

    conn = get_connection()
    try:
        cursor = conn.cursor()

        hora_inicio = datetime.strptime(hora, "%H:%M").time()

        if not (HORA_APERTURA <= hora_inicio < HORA_CIERRE):
            raise HTTPException(
                status_code=400,
                detail="Horario fuera del rango permitido"
            )

        try:
            cursor.execute("""
                INSERT INTO Reservas (ClienteId, ProfesionalId, Fecha, Hora)
                VALUES (?, ?, ?, ?)
            """, (cliente_id, profesional_id, fecha, hora_inicio))

            conn.commit()

        except pyodbc.IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Horario ya ocupado"
            )

        # Obtener datos
        cursor.execute("""
            SELECT C.Nombre, C.Telefono, P.Nombre
            FROM Clientes C
            JOIN Profesionales P ON P.ProfesionalId = ?
            WHERE C.ClienteId = ?
        """, (profesional_id, cliente_id))

        cliente, telefono, profesional = cursor.fetchone()

        mensaje = (
            f"Hola {cliente} 👋\n"
            f"Tu reserva fue confirmada\n"
            f"Barbero: {profesional}\n"
            f"Fecha: {fecha}\n"
            f"Hora: {hora}\n"
            f"Te esperamos 💈"
        )

        # 🔥 ENVÍA WHATSAPP DESDE EL PORTÁTIL
        if whatsapp:
            whatsapp.enviar_mensaje(telefono, mensaje)

        return {"mensaje": "Reserva creada correctamente"}

    finally:
        conn.close()

# ======================================================
# LISTAR RESERVAS
# ======================================================

@app.get("/reservas")
def listar_reservas():

    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT C.Nombre, C.Telefono, P.Nombre, R.Fecha, R.Hora
            FROM Reservas R
            JOIN Clientes C ON R.ClienteId = C.ClienteId
            JOIN Profesionales P ON R.ProfesionalId = P.ProfesionalId
            ORDER BY R.Fecha, R.Hora
        """)

        return [
            {
                "cliente": r[0],
                "telefono": r[1],
                "profesional": r[2],
                "fecha": str(r[3]),
                "hora": str(r[4])
            }
            for r in cursor.fetchall()
        ]

    finally:
        conn.close()


