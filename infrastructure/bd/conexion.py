import psycopg2
from psycopg2.extras import RealDictCursor

def obtener_conexion():
    conexion = psycopg2.connect(
        host="localhost",
        port="5432",
        database="QCM",
        user="postgres",
        password="password"
    )
    
    # Configurar la zona horaria para la conexión
    cursor = conexion.cursor()
    cursor.execute("SET timezone = 'America/Lima';")
    cursor.execute("SET datestyle = 'ISO, DMY';")
    cursor.close()
    
    return conexion
