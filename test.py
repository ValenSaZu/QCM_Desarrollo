import psycopg2

def probar_conexion():
    try:
        conexion = psycopg2.connect(
            host="127.0.0.1",
            port="5433",
            database="QCM",
            user="postgres",
            password="1234",
            options="-c client_encoding=UTF8"
        )
        print("Conexión a PostgreSQL exitosa.")
        conexion.close()
    except Exception as e:
        print("Error al conectar a PostgreSQL:")
        print(e)

if __name__ == '__main__':
    probar_conexion()
