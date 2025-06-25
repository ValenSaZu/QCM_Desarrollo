from infrastructure.bd.conexion import obtener_conexion

# BD-001: Entidad para gestionar operaciones de clientes que incluye:
# - Gestión de información básica de clientes (activos e inactivos)
# - Manejo de saldos y transacciones
# - Consulta de historial de compras/descargas
# - Operaciones CRUD para clientes
class Cliente:
    def __init__(self, id_usuario, username, nombre, apellido, saldo, excliente):
        self.id_usuario = id_usuario
        self.username = username
        self.nombre = nombre
        self.apellido = apellido
        self.saldo = saldo
        self.excliente = excliente

    # ENT-CLI-001: Obtiene todos los clientes registrados (activos e inactivos)
    # Retorna:
    #   list[Cliente]: Lista completa de clientes ordenados por ID
    # Excepciones:
    #   - Captura y relanza excepciones de base de datos
    # Características:
    #   - Consulta JOIN entre tablas USUARIO y CLIENTE
    #   - Ordenamiento por ID de usuario
    @classmethod
    def obtener_todos(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT u.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                           FROM USUARIO u
                                    JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                           ORDER BY u.id_usuario
                           """)
            return [cls(*row) for row in cursor.fetchall()]
        except Exception:
            raise Exception("Error al obtener clientes")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CLI-002: Obtiene solo clientes activos (excliente = False)
    # Retorna:
    #   list[Cliente]: Lista de clientes activos ordenados por ID
    # Características:
    #   - Filtra por campo excliente = FALSE
    #   - Mismo formato de retorno que ENT-CLI-001
    @classmethod
    def obtener_clientes_activos(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT u.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                           FROM USUARIO u
                                    JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                           WHERE c.excliente = FALSE
                           ORDER BY u.id_usuario
                           """)
            return [cls(*row) for row in cursor.fetchall()]
        except Exception:
            raise Exception("Error al obtener clientes activos")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CLI-003: Obtiene solo exclientes (excliente = True)
    # Retorna:
    #   list[Cliente]: Lista de exclientes ordenados por ID
    # Características:
    #   - Filtra por campo excliente = TRUE
    #   - Mismo formato de retorno que ENT-CLI-001
    @classmethod
    def obtener_exclientes(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT u.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                           FROM USUARIO u
                                    JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                           WHERE c.excliente = TRUE
                           ORDER BY u.id_usuario
                           """)
            return [cls(*row) for row in cursor.fetchall()]
        except Exception:
            raise Exception("Error al obtener exclientes")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CLI-004: Busca clientes por término en nombre, apellido o username
    # Parámetros:
    #   termino (str): Texto a buscar (case-insensitive)
    # Retorna:
    #   list[Cliente]: Lista de clientes que coinciden con el término
    # Características:
    #   - Búsqueda con LIKE y LOWER para coincidencias parciales
    #   - Busca en múltiples campos
    @classmethod
    def buscar_por_termino(cls, termino):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            term = f"%{termino.lower()}%"
            cursor.execute("""
                           SELECT u.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                           FROM USUARIO u
                                    JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                           WHERE LOWER(u.nombre) LIKE %s
                              OR LOWER(u.apellido) LIKE %s
                              OR LOWER(u.username) LIKE %s
                           ORDER BY u.id_usuario
                           """, (term, term, term))
            return [cls(*row) for row in cursor.fetchall()]
        except Exception:
            raise Exception("Error al buscar clientes")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CLI-005: Busca solo clientes activos por término
    # Parámetros:
    #   termino (str): Texto a buscar (case-insensitive)
    # Retorna:
    #   list[Cliente]: Lista de clientes activos que coinciden
    # Características:
    #   - Combina filtro de activos con búsqueda por término
    @classmethod
    def buscar_clientes_activos_por_termino(cls, termino):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            term = f"%{termino.lower()}%"
            cursor.execute("""
                           SELECT u.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                           FROM USUARIO u
                                    JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                           WHERE c.excliente = FALSE
                             AND (LOWER(u.nombre) LIKE %s OR LOWER(u.apellido) LIKE %s OR LOWER(u.username) LIKE %s)
                           ORDER BY u.id_usuario
                           """, (term, term, term))
            return [cls(*row) for row in cursor.fetchall()]
        except Exception:
            raise Exception("Error al buscar clientes activos")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CLI-006: Obtiene un cliente específico por ID
    # Parámetros:
    #   id_usuario (int): ID del cliente a buscar
    # Retorna:
    #   Cliente: Objeto cliente encontrado | None si no existe
    # Características:
    #   - Consulta directa por clave primaria
    @classmethod
    def obtener_por_id(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT c.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                           FROM CLIENTE c
                                    JOIN USUARIO u ON c.id_usuario = u.id_usuario
                           WHERE c.id_usuario = %s
                           """, (id_usuario,))
            if row := cursor.fetchone():
                return cls(*row)
            return None
        finally:
            cursor.close()
            conexion.close()

    # ENT-CLI-007: Obtiene historial combinado de compras/descargas
    # Parámetros:
    #   id_usuario (int): ID del cliente
    # Retorna:
    #   dict: {success: bool, data/historial: list}
    # Características:
    #   - Consulta UNION de tablas DESCARGA y REGALO
    #   - Limita a últimos 12 meses
    #   - Incluye valoraciones de contenido
    @classmethod
    def obtener_historial(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT d.id_descarga,
                                  NULL AS id_compra,
                                  c.nombre AS nombre_contenido,
                                  c.autor,
                                  c.precio,
                                  c.tamano_archivo,
                                  d.fecha_y_hora,
                                  cat.nombre AS categoria,
                                  taf.formato,
                                  c.id_contenido,
                                  'descarga' AS tipo
                           FROM DESCARGA d
                                    JOIN USUARIO u ON d.id_usuario = u.id_usuario
                                    JOIN CONTENIDO c ON d.id_contenido = c.id_contenido
                                    JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                                    LEFT JOIN TIPO_ARCHIVO taf ON c.id_tipo_archivo = taf.id_tipo_archivo
                           WHERE u.id_usuario = %s
                             AND d.fecha_y_hora >= (CURRENT_DATE - INTERVAL '12 months')

                           UNION ALL

                           SELECT NULL AS id_descarga,
                                  comp.id_compra,
                                  c.nombre AS nombre_contenido,
                                  c.autor,
                                  c.precio,
                                  c.tamano_archivo,
                                  comp.fecha_y_hora,
                                  cat.nombre AS categoria,
                                  taf.formato,
                                  c.id_contenido,
                                  'regalo' AS tipo
                           FROM REGALO r
                                    JOIN COMPRA comp ON r.id_compra = comp.id_compra
                                    JOIN CONTENIDO c ON r.id_contenido = c.id_contenido
                                    JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                                    LEFT JOIN TIPO_ARCHIVO taf ON c.id_tipo_archivo = taf.id_tipo_archivo
                                    JOIN USUARIO u ON r.id_usuario_envia = u.id_usuario
                           WHERE r.id_usuario_recibe = %s
                             AND comp.fecha_y_hora >= (CURRENT_DATE - INTERVAL '12 months')

                           ORDER BY fecha_y_hora DESC LIMIT 20
                           """, (id_usuario, id_usuario))

            columns = [col[0] for col in cursor.description] if cursor.description else []
            resultados = [dict(zip(columns, row)) for row in cursor.fetchall()] if columns else []

            from domain.entities.valoracion import Valoracion
            historial = []
            for row in resultados:
                if row.get('id_descarga'):
                    calificacion = Valoracion.obtener_valoracion_por_descarga(id_usuario, row['id_contenido'], row['id_descarga'])
                else:
                    calificacion = 0
                historial.append({
                    "id_compra": row['id_compra'],
                    "id_contenido": row['id_contenido'],
                    "nombre_contenido": row['nombre_contenido'] or 'Sin nombre',
                    "autor": row['autor'] or 'Desconocido',
                    "precio": float(row['precio']) if row['precio'] else 0.0,
                    "categoria": row['categoria'] if row.get('categoria') is not None else 'N/A',
                    "formato": row['formato'] or 'N/A',
                    "fecha_compra": row['fecha_y_hora'].strftime("%Y-%m-%d %H:%M:%S") if row['fecha_y_hora'] else 'Sin fecha',
                    "calificacion": int(calificacion) if calificacion > 0 else 0
                })

            return {"success": True, "data": historial}
        except Exception:
            return {"success": False, "error": "Error al obtener historial"}
        finally:
            cursor.close()
            conexion.close()

    # ENT-CLI-008: Actualiza el saldo de un cliente
    # Parámetros:
    #   id_usuario (int): ID del cliente
    #   nuevo_saldo (float): Nuevo valor de saldo
    # Retorna:
    #   float: Saldo actualizado
    # Características:
    #   - Transacción atómica
    #   - Verifica existencia del cliente
    @classmethod
    def actualizar_saldo(cls, id_usuario, nuevo_saldo):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           UPDATE CLIENTE
                           SET saldo = %s
                           WHERE id_usuario = %s RETURNING saldo
                           """, (nuevo_saldo, id_usuario))

            if saldo := cursor.fetchone():
                conexion.commit()
                return saldo[0]
            raise Exception("Cliente no encontrado")
        except Exception:
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()

    # ENT-CLI-009: Marca/desmarca cliente como ex-cliente
    # Parámetros:
    #   id_usuario (int): ID del cliente
    #   excliente (bool): True para marcar como ex-cliente
    # Retorna:
    #   bool: Nuevo estado (True=excliente)
    # Características:
    #   - Transacción atómica
    #   - Verifica existencia del cliente
    @classmethod
    def marcar_como_excliente(cls, id_usuario, excliente=True):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           UPDATE CLIENTE
                           SET excliente = %s
                           WHERE id_usuario = %s RETURNING excliente
                           """, (excliente, id_usuario))

            if resultado := cursor.fetchone():
                conexion.commit()
                return resultado[0]
            raise Exception("Cliente no encontrado")
        except Exception:
            conexion.rollback()
            raise Exception("Error al actualizar estado")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CLI-010: Verifica existencia de cliente
    # Parámetros:
    #   id_usuario (int): ID a verificar
    # Retorna:
    #   bool: True si existe, False si no
    # Características:
    #   - Consulta simple por ID
    @classmethod
    def existe_cliente(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT id_usuario FROM CLIENTE WHERE id_usuario = %s", (id_usuario,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conexion.close()

    # ENT-CLI-011: Recarga saldo a cliente
    # Parámetros:
    #   id_usuario (int): ID del cliente
    #   monto (float): Cantidad a recargar
    # Retorna:
    #   dict: {success, message, nuevo_saldo}
    # Características:
    #   - Transacción atómica con registro
    #   - Actualiza saldo y crea registro en TRANSACCION
    @classmethod
    def recargar_saldo(cls, id_usuario, monto):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           UPDATE CLIENTE
                           SET saldo = COALESCE(saldo, 0) + %s
                           WHERE id_usuario = %s RETURNING saldo
                           """, (monto, id_usuario))

            if not (resultado := cursor.fetchone()):
                raise Exception("No se pudo actualizar el saldo")

            cursor.execute("""
                           INSERT INTO TRANSACCION (id_usuario, tipo, monto, descripcion)
                           VALUES (%s, 'RECARGA', %s, 'Recarga de saldo')
                           """, (id_usuario, monto))

            conexion.commit()
            return {
                "success": True,
                "message": f"Recarga exitosa: S/. {float(monto):.2f}",
                "nuevo_saldo": float(resultado[0])
            }
        except Exception:
            conexion.rollback()
            return {"success": False, "error": "Error al recargar saldo"}
        finally:
            cursor.close()
            conexion.close()

    # ENT-CLI-012: Obtiene historial de compras específico
    # Parámetros:
    #   id_usuario (int): ID del cliente
    #   limite (int): Límite de registros (default: 10)
    # Retorna:
    #   dict: {success, data/error}
    # Características:
    #   - Consulta específica a tabla COMPRA
    #   - Incluye valoraciones de contenido
    #   - Ordenado por fecha descendente
    @classmethod
    def obtener_historial_compras(cls, id_usuario, limite=10):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT c.id_compra,
                                  c.fecha_y_hora,
                                  co.id_contenido,
                                  co.nombre,
                                  co.autor,
                                  co.precio,
                                  cat.nombre AS categoria,
                                  taf.formato
                           FROM COMPRA c
                                    JOIN CONTENIDO co ON c.id_contenido = co.id_contenido
                                    JOIN CATEGORIA cat ON co.id_categoria = cat.id_categoria
                                    JOIN TIPO_ARCHIVO taf ON co.id_tipo_archivo = taf.id_tipo_archivo
                           WHERE c.id_usuario = %s
                           ORDER BY c.fecha_y_hora DESC
                               LIMIT %s
                           """, (id_usuario, limite))

            columns = [col[0] for col in cursor.description] if cursor.description else []
            resultados = [dict(zip(columns, row)) for row in cursor.fetchall()] if columns else []

            from domain.entities.valoracion import Valoracion
            historial = []
            for row in resultados:
                calificacion = Valoracion.obtener_valoracion_usuario(id_usuario, row['id_contenido'])
                historial.append({
                    "id_compra": row['id_compra'],
                    "id_contenido": row['id_contenido'],
                    "nombre_contenido": row['nombre'] or 'Sin nombre',
                    "autor": row['autor'] or 'Desconocido',
                    "precio": float(row['precio']) if row['precio'] else 0.0,
                    "categoria": row['categoria'] if row.get('categoria') is not None else 'N/A',
                    "formato": row['formato'] or 'N/A',
                    "fecha_compra": row['fecha_y_hora'].strftime("%Y-%m-%d %H:%M:%S") if row['fecha_y_hora'] else 'Sin fecha',
                    "calificacion": int(calificacion) if calificacion > 0 else 0
                })

            return {"success": True, "data": historial}
        except Exception:
            return {"success": False, "error": "Error al obtener historial"}
        finally:
            cursor.close()
            conexion.close()