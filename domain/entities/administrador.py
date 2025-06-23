from infrastructure.bd.conexion import obtener_conexion

class Administrador:
    def __init__(self, id_usuario, username, nombre, apellido, contrasena, acceso):
        self.id_usuario = id_usuario
        self.username = username
        self.nombre = nombre
        self.apellido = apellido
        self.contrasena = contrasena
        self.acceso = acceso

    @classmethod
    def buscar_por_username(cls, username):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
            SELECT a.id_usuario, u.username, u.nombre, u.apellido, u.contrasena, a.acceso 
            FROM administrador AS a 
            JOIN usuario AS u ON u.id_usuario = a.id_usuario 
            WHERE u.username = %s;
                """
            cursor.execute(query, (username,))

            administradores = []
            for row in cursor.fetchall():
                administrador = cls(
                    id_usuario=row[0],
                    username=row[1],
                    nombre=row[2],
                    apellido=row[3],
                    contrasena=row[4],
                    acceso=row[5]
                )
                administradores.append(administrador)
            return administradores

        except Exception as e:
            raise Exception(f"Error al obtener administrador: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_por_id(cls, id_usuario):
        """Obtiene un administrador por su ID de usuario"""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
            SELECT a.id_usuario, u.username, u.nombre, u.apellido, u.contrasena, a.acceso 
            FROM administrador AS a 
            JOIN usuario AS u ON u.id_usuario = a.id_usuario 
            WHERE a.id_usuario = %s;
                """
            cursor.execute(query, (id_usuario,))
            row = cursor.fetchone()

            if row:
                return cls(
                    id_usuario=row[0],
                    username=row[1],
                    nombre=row[2],
                    apellido=row[3],
                    contrasena=row[4],
                    acceso=row[5]
                )
            return None

        except Exception as e:
            raise Exception(f"Error al obtener administrador por ID: {str(e)}")
        finally:
            cursor.close()
            conexion.close()