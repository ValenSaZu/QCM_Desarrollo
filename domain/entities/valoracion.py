from infrastructure.bd.conexion import obtener_conexion

#BD-016: Entidad para gestionar valoraciones de contenido que incluye:
#- Registro y actualización de valoraciones
#- Cálculo de promedios y estadísticas
#- Verificación de adquisiciones previas
#- Asociación con descargas específicas
#- Manejo de historial de valoraciones
class Valoracion:
    def __init__(self, id_valoracion, id_usuario, id_contenido, puntuacion, fecha):
        self.id_valoracion = id_valoracion
        self.id_usuario = id_usuario
        self.id_contenido = id_contenido
        self.puntuacion = puntuacion
        self.fecha = fecha

    # ENT-VAL-001: Obtiene la valoración de un usuario para un contenido específico
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   id_contenido (int): ID del contenido
    # Retorna:
    #   float: Puntuación (0-100) | 0 si no existe valoración
    # Características:
    #   - Escala la puntuación de 0-10 a 0-100
    #   - Maneja errores devolviendo 0 por defecto
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
    # Parámetros:
    #   id_contenido (int): ID del contenido
    # Retorna:
    #   float: Promedio de puntuaciones (0-100) | 0 si no hay valoraciones
    # Características:
    #   - Usa función AVG de SQL
    #   - Escala el resultado a rango 0-100
    #   - Maneja casos NULL devolviendo 0
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
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   id_contenido (int): ID del contenido
    # Retorna:
    #   bool: True si existe adquisición, False si no
    # Características:
    #   - Consulta tabla DESCARGA
    #   - Maneja errores devolviendo False
    @classmethod
    def verificar_adquisicion_contenido(cls, id_usuario, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
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
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   id_contenido (int): ID del contenido
    # Retorna:
    #   bool: True si existe valoración, False si no
    # Características:
    #   - Consulta directa por usuario y contenido
    #   - Maneja errores devolviendo False
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
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   id_contenido (int): ID del contenido
    #   puntuacion_normalizada (float): Puntuación (0-1)
    # Retorna:
    #   dict: {success: bool, message/error: str}
    # Características:
    #   - Actualiza fecha automáticamente
    #   - Transacción atómica con rollback
    #   - Verifica filas afectadas
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
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   id_contenido (int): ID del contenido
    #   puntuacion_normalizada (float): Puntuación (0-1)
    # Retorna:
    #   dict: {success: bool, message/error: str}
    # Características:
    #   - Registra fecha actual automáticamente
    #   - Transacción atómica con rollback
    #   - Verifica filas afectadas
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

    # ENT-VAL-007: Obtiene descargas no valoradas de un usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   id_contenido (int): ID del contenido
    # Retorna:
    #   list: Tuplas con (id_descarga, fecha) | lista vacía en error
    # Características:
    #   - LEFT JOIN con tabla VALORACION
    #   - Filtra por valoraciones NULL
    #   - Ordena por fecha descendente
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
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            cursor.close()
            conexion.close()

    # ENT-VAL-008: Obtiene valoraciones asociadas a descargas
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   id_contenido (int): ID del contenido
    # Retorna:
    #   list: Tuplas con (id_descarga, puntuacion, fecha) | lista vacía en error
    # Características:
    #   - LEFT JOIN entre DESCARGA y VALORACION
    #   - Ordena por fecha de descarga
    #   - Incluye todas las descargas con/sin valoración
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
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            cursor.close()
            conexion.close()

    # ENT-VAL-009: Crea valoración asociada a descarga específica
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   id_contenido (int): ID del contenido
    #   id_descarga (int): ID de la descarga
    #   puntuacion_normalizada (float): Puntuación (0-1)
    # Retorna:
    #   dict: {success: bool, message/error: str}
    # Características:
    #   - Asocia valoración con descarga específica
    #   - Registra fecha actual automáticamente
    #   - Transacción atómica con rollback
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

    # ENT-VAL-010: Obtiene la última valoración de un usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   id_contenido (int): ID del contenido
    # Retorna:
    #   dict: {'puntuacion': int, 'fecha': datetime} | None si no existe
    # Características:
    #   - Ordena por fecha descendente
    #   - Limita a 1 resultado
    #   - Escala puntuación a 0-100
    @classmethod
    def obtener_ultima_valoracion_usuario(cls, id_usuario, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute('''
                SELECT puntuacion, fecha
                FROM VALORACION
                WHERE id_usuario = %s AND id_contenido = %s
                ORDER BY fecha DESC
                LIMIT 1
            ''', (id_usuario, id_contenido))
            resultado = cursor.fetchone()
            if resultado:
                return {'puntuacion': int(resultado[0] * 10), 'fecha': resultado[1]}
            return None
        except Exception:
            return None
        finally:
            cursor.close()
            conexion.close()

    # ENT-VAL-011: Obtiene valoración específica por descarga
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   id_contenido (int): ID del contenido
    #   id_descarga (int): ID de la descarga
    # Retorna:
    #   int: Puntuación (0-100) | 0 si no existe
    # Características:
    #   - Consulta directa por triple clave
    #   - Escala resultado a 0-100
    #   - Maneja errores devolviendo 0
    @classmethod
    def obtener_valoracion_por_descarga(cls, id_usuario, id_contenido, id_descarga):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute('''
                SELECT puntuacion
                FROM VALORACION
                WHERE id_usuario = %s AND id_contenido = %s AND id_descarga = %s
            ''', (id_usuario, id_contenido, id_descarga))
            resultado = cursor.fetchone()
            return int(resultado[0] * 10) if resultado and resultado[0] is not None else 0
        except Exception:
            return 0
        finally:
            cursor.close()
            conexion.close()