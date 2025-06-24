from infrastructure.bd.conexion import obtener_conexion

# BD-001: Entidad para gestionar operaciones de clientes
class Cliente:
    def __init__(self, id_usuario, username, nombre, apellido, saldo, excliente):
        self.id_usuario = id_usuario
        self.username = username
        self.nombre = nombre
        self.apellido = apellido
        self.saldo = saldo
        self.excliente = excliente

    # ENT-CLI-001: Obtiene todos los clientes (activos e inactivos)
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

    # ENT-CLI-002: Obtiene solo clientes activos
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

    # ENT-CLI-003: Obtiene solo exclientes
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

    # ENT-CLI-004: Busca clientes por término (nombre, apellido o username)
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

    # ENT-CLI-006: Obtiene un cliente por ID
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

    # ENT-CLI-007: Obtiene el historial de compras/descargas de un cliente
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

    # ENT-CLI-009: Marca/desmarca un cliente como ex-cliente
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

    # ENT-CLI-010: Verifica si un cliente existe
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

    # ENT-CLI-011: Recarga saldo a un cliente
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

    # ENT-CLI-012: Obtiene el historial de compras de un cliente
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
                                  cat.nombre,
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