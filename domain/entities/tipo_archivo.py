from infrastructure.bd.conexion import obtener_conexion

# BD-014: Entidad para gestionar tipos de archivo que incluye:
# - Consulta de tipos de archivo por extensión
# - Obtención de todos los formatos soportados
# - Manejo de metadatos de formatos (MIME types, extensiones)
# - Operaciones básicas de consulta
class TipoArchivo:
    def __init__(self, id_tipo_archivo, extension, mime_type, formato):
        self.id_tipo_archivo = id_tipo_archivo
        self.extension = extension
        self.mime_type = mime_type
        self.formato = formato

    # ENT-TARCH-001: Obtiene un tipo de archivo por su extensión
    # Parámetros:
    #   extension (str): Extensión del archivo (ej. 'pdf', 'mp3')
    # Retorna:
    #   TipoArchivo: Objeto con los datos del tipo de archivo | None si no existe
    # Excepciones:
    #   - Lanza excepción si hay error en la consulta
    # Características:
    #   - Búsqueda exacta por extensión
    #   - Retorna objeto completo con todos los metadatos
    @classmethod
    def obtener_por_extension(cls, extension):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                SELECT id_tipo_archivo, extension, mime_type, formato
                FROM TIPO_ARCHIVO
                WHERE extension = %s
                """, (extension,))

            tipo_archivo = cursor.fetchone()
            if not tipo_archivo:
                return None

            return cls(
                id_tipo_archivo=tipo_archivo[0],
                extension=tipo_archivo[1],
                mime_type=tipo_archivo[2],
                formato=tipo_archivo[3]
            )
        except Exception:
            raise Exception("Error al obtener tipo de archivo")
        finally:
            cursor.close()
            conexion.close()

    # ENT-TARCH-002: Obtiene todos los tipos de archivo disponibles
    # Retorna:
    #   list[TipoArchivo]: Lista de todos los tipos de archivo registrados
    # Excepciones:
    #   - Lanza excepción si hay error en la consulta
    # Características:
    #   - Ordena resultados alfabéticamente por extensión
    #   - Retorna objetos completos con todos los metadatos
    @classmethod
    def obtener_todos(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                SELECT id_tipo_archivo, extension, mime_type, formato
                FROM TIPO_ARCHIVO
                ORDER BY extension
                """)

            tipos_archivo = []
            for row in cursor.fetchall():
                tipo_archivo = cls(
                    id_tipo_archivo=row[0],
                    extension=row[1],
                    mime_type=row[2],
                    formato=row[3]
                )
                tipos_archivo.append(tipo_archivo)
            return tipos_archivo
        except Exception:
            raise Exception("Error al obtener tipos de archivo")
        finally:
            cursor.close()
            conexion.close()