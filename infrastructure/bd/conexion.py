import psycopg2

def obtener_conexion():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="QCM",
        user="postgres",
        password="password"
    )
