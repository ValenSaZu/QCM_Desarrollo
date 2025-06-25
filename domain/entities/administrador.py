from infrastructure.bd.conexion import obtener_conexion

# BD-002: Entidad para gestionar administradores del sistema que incluye:
# - Representación de la entidad administrador en la base de datos
# - Búsqueda de administradores por credenciales
# - Obtención de administradores por identificador
# - Manejo seguro de conexiones a base de datos
class Administrador:
    def __init__(self, id_usuario, username, nombre, apellido, contrasena, acceso):
        self.id_usuario = id_usuario
        self.username = username
        self.nombre = nombre
        self.apellido = apellido
        self.contrasena = contrasena
        self.acceso = acceso

    # ENT-ADMIN-001: Busca administradores por nombre de usuario
    # Parámetros:
    #   username (str): Nombre de usuario a buscar
    # Retorna:
    #   list[Administrador]: Lista de administradores coincidentes
    # Excepciones:
    #   - Captura y relanza excepciones de base de datos
    # Características:
    #   - Consulta JOIN entre tablas administrador y usuario
    #   - Manejo seguro de conexiones con try-finally
    #   - Retorna lista de objetos Administrador
    # Dependencias:
    #   - Requiere conexión a base de datos válida
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

            return [
                cls(
                    id_usuario=row[0],
                    username=row[1],
                    nombre=row[2],
                    apellido=row[3],
                    contrasena=row[4],
                    acceso=row[5]
                ) for row in cursor.fetchall()
            ]
        except Exception as e:
            raise Exception("Error al buscar administrador")
        finally:
            cursor.close()
            conexion.close()

    # ENT-ADMIN-002: Obtiene un administrador por ID de usuario
    # Parámetros:
    #   id_usuario (int): Identificador único del usuario
    # Retorna:
    #   Administrador: Objeto administrador encontrado | None si no existe
    # Excepciones:
    #   - Captura y relanza excepciones de base de datos
    # Características:
    #   - Consulta JOIN entre tablas administrador y usuario
    #   - Manejo seguro de conexiones con try-finally
    #   - Retorna objeto Administrador o None
    # Dependencias:
    #   - Requiere conexión a base de datos válida
    @classmethod
    def obtener_por_id(cls, id_usuario):
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

            return cls(*row) if row else None
        except Exception:
            raise Exception("Error al obtener administrador")
        finally:
            cursor.close()
            conexion.close()