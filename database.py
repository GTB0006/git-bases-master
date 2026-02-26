import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    # Obtenemos el valor de la variable de entorno
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        raise ValueError("No se encontró la variable DATABASE_URL en el entorno")

    # Limpieza: Si por error la cadena trae comillas o la palabra DATABASE_URL= al inicio, la quitamos
    db_url = db_url.replace("DATABASE_URL=", "").replace('"', '').replace("'", "").strip()

    # Corrección de protocolo para Render
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    try:
        return psycopg2.connect(db_url)
    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")
        raise e
