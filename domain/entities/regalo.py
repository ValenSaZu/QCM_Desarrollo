import psycopg2
from infrastructure.bd.conexion import obtener_conexion
from datetime import datetime

# BD-005: Entidad para gestionar operaciones de regalos entre usuarios que incluye:
# - Creación y envío de regalos entre clientes
# - Consulta de regalos recibidos
# - Gestión de estado de regalos (abiertos/no abiertos)
# - Validación de saldo y permisos
# - Operaciones de actualización de estado
class Regalo:
    # ENT-REG-001: Crea un nuevo regalo entre usuarios
    # Parámetros:
    #   id_usuario_envia (int): ID del usuario que envía el regalo
    #   id_usuario_recibe (int): ID del usuario que recibe el regalo
    #   id_contenido (int): ID del contenido a regalar
    # Retorna:
    #   dict: Diccionario con resultado de la operación (success, message, id_regalo, id_compra)
    # Excepciones:
    #   - Lanza excepción si hay error en la base de datos
    # Características:
    #   - Valida que ambos usuarios sean clientes
    #   - Verifica existencia del contenido
    #   - Comprueba saldo suficiente
    #   - Impide auto-regalos
    #   - Transacción atómica con múltiples operaciones
    #   - Actualiza saldo del remitente
    @staticmethod
    def crear_regalo(id_usuario_envia, id_usuario_recibe, id_contenido):
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                           SELECT id_usuario
                           FROM CLIENTE
                           WHERE id_usuario = %s
                           """, (id_usuario_envia,))

            if not cursor.fetchone():
                return {"success": False, "error": "El usuario que envía no existe o no es un cliente"}

            cursor.execute("""
                           SELECT id_usuario
                           FROM CLIENTE
                           WHERE id_usuario = %s
                           """, (id_usuario_recibe,))

            if not cursor.fetchone():
                return {"success": False, "error": "El usuario que recibe no existe o no es un cliente"}

            cursor.execute("""
                           SELECT id_contenido, precio
                           FROM CONTENIDO
                           WHERE id_contenido = %s
                           """, (id_contenido,))

            contenido = cursor.fetchone()
            if not contenido:
                return {"success": False, "error": "El contenido no existe"}

            precio_contenido = contenido[1]

            cursor.execute("""
                           SELECT saldo
                           FROM CLIENTE
                           WHERE id_usuario = %s
                           """, (id_usuario_envia,))

            saldo_result = cursor.fetchone()
            if not saldo_result:
                return {"success": False, "error": "No se pudo obtener el saldo del usuario"}

            saldo_actual = saldo_result[0]
            if saldo_actual < precio_contenido:
                return {"success": False, "error": "Saldo insuficiente para enviar el regalo"}

            if id_usuario_envia == id_usuario_recibe:
                return {"success": False, "error": "No puedes regalarte contenido a ti mismo"}

            cursor.execute("""
                           INSERT INTO COMPRA (id_usuario, id_contenido, fecha_y_hora)
                           VALUES (%s, %s, CURRENT_TIMESTAMP) RETURNING id_compra
                           """, (id_usuario_envia, id_contenido))

            compra_result = cursor.fetchone()
            if not compra_result:
                return {"success": False, "error": "Error al crear la compra"}

            id_compra = compra_result[0]

            cursor.execute("""
                           INSERT INTO REGALO (id_compra, id_usuario_envia, id_usuario_recibe, id_contenido, abierto)
                           VALUES (%s, %s, %s, %s, FALSE) RETURNING id_regalo
                           """, (id_compra, id_usuario_envia, id_usuario_recibe, id_contenido))

            regalo_result = cursor.fetchone()
            if not regalo_result:
                return {"success": False, "error": "Error al crear el regalo"}

            id_regalo = regalo_result[0]

            cursor.execute("""
                           UPDATE CLIENTE
                           SET saldo = saldo - %s
                           WHERE id_usuario = %s
                           """, (precio_contenido, id_usuario_envia))

            conexion.commit()
            cursor.close()
            conexion.close()

            return {
                "success": True,
                "message": "Regalo enviado exitosamente",
                "id_regalo": id_regalo,
                "id_compra": id_compra
            }

        except psycopg2.Error as e:
            if conexion:
                conexion.rollback()
            return {"success": False, "error": f"Error de base de datos: {str(e)}"}
        except Exception as e:
            if conexion:
                conexion.rollback()
            return {"success": False, "error": f"Error inesperado: {str(e)}"}
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    # ENT-REG-002: Obtiene todos los regalos recibidos por un usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario receptor
    # Retorna:
    #   list[dict]: Lista de diccionarios con información completa de los regalos
    # Excepciones:
    #   - Retorna lista vacía si hay error
    # Características:
    #   - Ordena por fecha descendente
    #   - Incluye información del remitente y contenido
    #   - Muestra estado (abierto/cerrado)
    #   - Formatea fechas como ISO
    @staticmethod
    def obtener_regalos_recibidos(id_usuario):
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                           SELECT r.id_regalo,
                                  r.abierto,
                                  r.id_compra,
                                  r.id_usuario_envia,
                                  r.id_usuario_recibe,
                                  r.id_contenido,
                                  c.nombre          as nombre_contenido,
                                  c.autor,
                                  c.precio,
                                  c.descripcion,
                                  ta.formato,
                                  u_envia.username  as username_envia,
                                  u_envia.nombre    as nombre_envia,
                                  u_envia.apellido  as apellido_envia,
                                  comp.fecha_y_hora as fecha_regalo
                           FROM REGALO r
                                    JOIN COMPRA comp ON r.id_compra = comp.id_compra
                                    JOIN CONTENIDO c ON r.id_contenido = c.id_contenido
                                    JOIN TIPO_ARCHIVO ta ON c.id_tipo_archivo = ta.id_tipo_archivo
                                    JOIN USUARIO u_envia ON r.id_usuario_envia = u_envia.id_usuario
                           WHERE r.id_usuario_recibe = %s
                           ORDER BY comp.fecha_y_hora DESC
                           """, (id_usuario,))

            regalos = []
            for row in cursor.fetchall():
                regalos.append({
                    "id_regalo": row[0],
                    "abierto": row[1],
                    "id_compra": row[2],
                    "id_usuario_envia": row[3],
                    "id_usuario_recibe": row[4],
                    "id_contenido": row[5],
                    "nombre_contenido": row[6],
                    "autor": row[7],
                    "precio": row[8],
                    "descripcion": row[9],
                    "formato": row[10],
                    "username_envia": row[11],
                    "nombre_envia": row[12],
                    "apellido_envia": row[13],
                    "fecha_regalo": row[14].isoformat() if row[14] else None
                })

            cursor.close()
            conexion.close()

            return regalos

        except psycopg2.Error as e:
            return []
        except Exception as e:
            return []
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    # ENT-REG-003: Obtiene los regalos sin abrir de un usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario receptor
    # Retorna:
    #   list[dict]: Lista de diccionarios con información básica de regalos no abiertos
    # Excepciones:
    #   - Retorna lista vacía si hay error
    # Características:
    #   - Filtra solo regalos con abierto=False
    #   - Ordena por fecha descendente
    #   - Incluye información básica del contenido y remitente
    @staticmethod
    def obtener_regalos_sin_abrir(id_usuario):
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                           SELECT r.id_regalo,
                                  r.id_contenido,
                                  c.nombre          as nombre_contenido,
                                  c.autor,
                                  c.precio,
                                  ta.formato,
                                  u_envia.username  as username_envia,
                                  u_envia.nombre    as nombre_envia,
                                  u_envia.apellido  as apellido_envia,
                                  comp.fecha_y_hora as fecha_regalo
                           FROM REGALO r
                                    JOIN COMPRA comp ON r.id_compra = comp.id_compra
                                    JOIN CONTENIDO c ON r.id_contenido = c.id_contenido
                                    JOIN TIPO_ARCHIVO ta ON c.id_tipo_archivo = ta.id_tipo_archivo
                                    JOIN USUARIO u_envia ON r.id_usuario_envia = u_envia.id_usuario
                           WHERE r.id_usuario_recibe = %s
                             AND r.abierto = FALSE
                           ORDER BY comp.fecha_y_hora DESC
                           """, (id_usuario,))

            regalos = []
            for row in cursor.fetchall():
                regalos.append({
                    "id_regalo": row[0],
                    "id_contenido": row[1],
                    "nombre_contenido": row[2],
                    "autor": row[3],
                    "precio": row[4],
                    "formato": row[5],
                    "username_envia": row[6],
                    "nombre_envia": row[7],
                    "apellido_envia": row[8],
                    "fecha_regalo": row[9].isoformat() if row[9] else None
                })

            cursor.close()
            conexion.close()

            return regalos

        except psycopg2.Error as e:
            return []
        except Exception as e:
            return []
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    # ENT-REG-004: Marca un regalo específico como abierto
    # Parámetros:
    #   id_regalo (int): ID del regalo a marcar
    #   id_usuario (int): ID del usuario receptor (para validación)
    # Retorna:
    #   dict: Diccionario con resultado de la operación
    # Excepciones:
    #   - Lanza excepción si hay error en la base de datos
    # Características:
    #   - Valida que el usuario sea el receptor
    #   - Transacción atómica
    #   - Retorna mensaje descriptivo
    @staticmethod
    def abrir_regalo(id_regalo, id_usuario):
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                           SELECT id_regalo
                           FROM REGALO
                           WHERE id_regalo = %s
                             AND id_usuario_recibe = %s
                           """, (id_regalo, id_usuario))

            if not cursor.fetchone():
                return {"success": False, "error": "Regalo no encontrado o no tienes permisos para abrirlo"}

            cursor.execute("""
                           UPDATE REGALO
                           SET abierto = TRUE
                           WHERE id_regalo = %s
                           """, (id_regalo,))

            conexion.commit()
            cursor.close()
            conexion.close()

            return {"success": True, "message": "Regalo marcado como abierto"}

        except psycopg2.Error as e:
            if conexion:
                conexion.rollback()
            return {"success": False, "error": f"Error de base de datos: {str(e)}"}
        except Exception as e:
            if conexion:
                conexion.rollback()
            return {"success": False, "error": f"Error inesperado: {str(e)}"}
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    # ENT-REG-005: Marca todos los regalos de un usuario como abiertos
    # Parámetros:
    #   id_usuario (int): ID del usuario receptor
    # Retorna:
    #   dict: Diccionario con resultado y conteo de regalos actualizados
    # Excepciones:
    #   - Lanza excepción si hay error en la base de datos
    # Características:
    #   - Actualiza múltiples registros en una operación
    #   - Retorna cantidad de regalos afectados
    #   - Transacción atómica
    @staticmethod
    def marcar_todos_regalos_abiertos(id_usuario):
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                           UPDATE REGALO
                           SET abierto = TRUE
                           WHERE id_usuario_recibe = %s
                             AND abierto = FALSE
                           """, (id_usuario,))

            filas_afectadas = cursor.rowcount
            conexion.commit()
            cursor.close()
            conexion.close()

            return {
                "success": True,
                "message": f"{filas_afectadas} regalo(s) marcado(s) como abierto(s)"
            }

        except psycopg2.Error as e:
            if conexion:
                conexion.rollback()
            return {"success": False, "error": f"Error de base de datos: {str(e)}"}
        except Exception as e:
            if conexion:
                conexion.rollback()
            return {"success": False, "error": f"Error inesperado: {str(e)}"}
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()