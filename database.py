import pyodbc

def get_connection():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=CJMPINEDA\\SQLEXPRESS;"
        "Database=BarberiaDB;"
        "Trusted_Connection=yes;"
    )
