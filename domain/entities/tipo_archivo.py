from infrastructure.bd.conexion import obtener_conexion

class TipoArchivo:
    def __init__(self, id_tipo_archivo, extension, mime_type, formato):
        self.id_tipo_archivo = id_tipo_archivo
        self.extension = extension
        self.mime_type = mime_type
        self.formato = formato

    @classmethod
    def obtener_por_extension(cls, extension):
        """Obtiene un tipo de archivo por su extensión"""
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
        except Exception as e:
            raise Exception(f"Error al obtener tipo de archivo: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_todos(cls):
        """Obtiene todos los tipos de archivo"""
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
        except Exception as e:
            raise Exception(f"Error al obtener tipos de archivo: {str(e)}")
        finally:
            cursor.close()
            conexion.close() 