class CalendarSender:
    def __init__(self):
        pass

    def crear_evento(self, correo, cliente, fecha, hora, profesional):
        # Ahora el calendario se envía por correo como adjunto .ics
        # No hace falta usar la API de Google
        print("INFO: El calendario se gestiona vía adjunto en EmailSender")
        return True
