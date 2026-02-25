import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class CalendarSender:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        
        # En local usa el archivo, en Render lo leerá del Secret File
        self.credentials = service_account.Credentials.from_service_account_file(
            'credentials.json',
            scopes=self.SCOPES
        )
        self.service = build('calendar', 'v3', credentials=self.credentials)
        
        # ID del calendario dinámico
        self.calendar_id = os.getenv("CALENDAR_ID", "blessedbarbershopenv@gmail.com")
        self.timezone = ZoneInfo("America/Bogota")


    def crear_evento(self, correo, cliente, fecha, hora, profesional):

        # 1️⃣ Crear datetime con zona horaria
        inicio = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        inicio = inicio.replace(tzinfo=self.timezone)

        fin = inicio + timedelta(hours=1)

        # 2️⃣ Convertir a formato ISO 8601 correcto (con timezone real)
        time_min = inicio.isoformat()
        time_max = fin.isoformat()

        # 3️⃣ Buscar si ya existe evento en ese rango
        eventos_existentes = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True
        ).execute()

        if eventos_existentes.get('items'):
            print("⚠️ Ya existe un evento en ese horario")
            return "Horario ocupado"

        # 4️⃣ Crear evento
        evento = {
            'summary': f'Corte - {cliente}',
            'description': f'Barbero: {profesional}\nCliente: {correo}',
            'start': {
                'dateTime': inicio.isoformat(),
                'timeZone': 'America/Bogota',
            },
            'end': {
                'dateTime': fin.isoformat(),
                'timeZone': 'America/Bogota',
            }
        }

        # 5️⃣ Insertar evento
        evento_creado = self.service.events().insert(
            calendarId=self.calendar_id,
            body=evento
        ).execute()

        print("✅ Evento creado:", evento_creado.get("htmlLink"))

        return "Evento creado correctamente"