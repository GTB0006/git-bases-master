import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables desde el archivo .env (solo para local)
load_dotenv()

def get_connection():
    # Buscamos la URL en las variables de entorno de Render
    url = os.getenv("DATABASE_URL")
    
    if not url:
        raise ValueError("La variable DATABASE_URL no está configurada en Render")
    
    # Si la URL empieza por 'postgres://', corregimos a 'postgresql://' 
    # (Render/Heroku a veces necesitan este ajuste para psycopg2)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    return psycopg2.connect(url)
