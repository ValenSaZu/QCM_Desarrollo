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
            cursor.execute("""
                           SELECT 1
                           FROM COMPRA
                           WHERE id_usuario = %s
                             AND id_contenido = %s
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