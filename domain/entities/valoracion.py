from infrastructure.bd.conexion import obtener_conexion

# BD-016: Entidad para gestionar valoraciones de contenido
class Valoracion:
    def __init__(self, id_valoracion, id_usuario, id_contenido, puntuacion, fecha):
        self.id_valoracion = id_valoracion
        self.id_usuario = id_usuario
        self.id_contenido = id_contenido
        self.puntuacion = puntuacion
        self.fecha = fecha

    # ENT-VAL-001: Obtiene la valoración de un usuario para un contenido específico
    @classmethod
    def obtener_valoracion_usuario(cls, id_usuario, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT puntuacion
                           FROM VALORACION
                           WHERE id_usuario = %s
                             AND id_contenido = %s
                           """, (id_usuario, id_contenido))

            resultado = cursor.fetchone()
            return float(resultado[0]) * 10 if resultado else 0

        except Exception:
            return 0
        finally:
            cursor.close()
            conexion.close()

    # ENT-VAL-002: Obtiene el promedio de valoraciones para un contenido
    @classmethod
    def obtener_promedio_valoracion(cls, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT AVG(puntuacion)
                           FROM VALORACION
                           WHERE id_contenido = %s
                           """, (id_contenido,))

            resultado = cursor.fetchone()
            return float(resultado[0]) * 10 if resultado and resultado[0] else 0

        except Exception:
            return 0
        finally:
            cursor.close()
            conexion.close()

    # ENT-VAL-003: Verifica si un usuario ha adquirido un contenido
    @classmethod
    def verificar_adquisicion_contenido(cls, id_usuario, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            # Solo puede valorar si ha descargado al menos una vez
            cursor.execute("""
                SELECT 1 FROM DESCARGA WHERE id_usuario = %s AND id_contenido = %s
            """, (id_usuario, id_contenido))
            return cursor.fetchone() is not None
        except Exception:
            return False
        finally:
            cursor.close()
            conexion.close()

    # ENT-VAL-004: Verifica si existe una valoración previa
    @classmethod
    def existe_valoracion(cls, id_usuario, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT id_valoracion
                           FROM VALORACION
                           WHERE id_usuario = %s
                             AND id_contenido = %s
                           """, (id_usuario, id_contenido))

            return cursor.fetchone() is not None

        except Exception:
            return False
        finally:
            cursor.close()
            conexion.close()

    # ENT-VAL-005: Actualiza una valoración existente
    @classmethod
    def actualizar_valoracion(cls, id_usuario, id_contenido, puntuacion_normalizada):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           UPDATE VALORACION
                           SET puntuacion = %s,
                               fecha      = CURRENT_TIMESTAMP
                           WHERE id_usuario = %s
                             AND id_contenido = %s
                           """, (puntuacion_normalizada, id_usuario, id_contenido))

            conexion.commit()

            if cursor.rowcount > 0:
                return {"success": True, "message": "Valoración actualizada correctamente"}
            return {"success": False, "error": "No se pudo actualizar la valoración"}

        except Exception:
            conexion.rollback()
            return {"success": False, "error": "Error al actualizar valoración"}
        finally:
            cursor.close()
            conexion.close()

    # ENT-VAL-006: Crea una nueva valoración
    @classmethod
    def crear_valoracion(cls, id_usuario, id_contenido, puntuacion_normalizada):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           INSERT INTO VALORACION
                               (id_usuario, id_contenido, puntuacion, fecha)
                           VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                           """, (id_usuario, id_contenido, puntuacion_normalizada))

            conexion.commit()

            if cursor.rowcount > 0:
                return {"success": True, "message": "Valoración creada correctamente"}
            return {"success": False, "error": "No se pudo crear la valoración"}

        except Exception:
            conexion.rollback()
            return {"success": False, "error": "Error al crear valoración"}
        finally:
            cursor.close()
            conexion.close()

    # Obtiene las descargas de un usuario para un contenido
    @classmethod
    def obtener_descargas_no_valoradas(cls, id_usuario, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute('''
                SELECT d.id_descarga, d.fecha_y_hora
                FROM DESCARGA d
                LEFT JOIN VALORACION v ON d.id_descarga = v.id_descarga
                WHERE d.id_usuario = %s AND d.id_contenido = %s AND v.id_valoracion IS NULL
                ORDER BY d.fecha_y_hora
            ''', (id_usuario, id_contenido))
            return cursor.fetchall()  # [(id_descarga, fecha_y_hora), ...]
        except Exception:
            return []
        finally:
            cursor.close()
            conexion.close()

    # Obtiene la cantidad de valoraciones hechas por descarga
    @classmethod
    def obtener_valoraciones_por_descarga(cls, id_usuario, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute('''
                SELECT d.id_descarga, v.puntuacion, v.fecha
                FROM DESCARGA d
                LEFT JOIN VALORACION v ON d.id_descarga = v.id_descarga
                WHERE d.id_usuario = %s AND d.id_contenido = %s
                ORDER BY d.fecha_y_hora
            ''', (id_usuario, id_contenido))
            return cursor.fetchall()  # [(id_descarga, puntuacion, fecha), ...]
        except Exception:
            return []
        finally:
            cursor.close()
            conexion.close()

    # Crea una valoración asociada a una descarga específica
    @classmethod
    def crear_valoracion_por_descarga(cls, id_usuario, id_contenido, id_descarga, puntuacion_normalizada):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute('''
                INSERT INTO VALORACION (id_usuario, id_contenido, id_descarga, puntuacion, fecha)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ''', (id_usuario, id_contenido, id_descarga, puntuacion_normalizada))
            conexion.commit()
            if cursor.rowcount > 0:
                return {"success": True, "message": "Valoración creada correctamente"}
            return {"success": False, "error": "No se pudo crear la valoración"}
        except Exception as e:
            conexion.rollback()
            return {"success": False, "error": f"Error al crear valoración: {str(e)}"}
        finally:
            cursor.close()
            conexion.close()