from infrastructure.bd.conexion import obtener_conexion

class Cliente:
    def __init__(self, id_usuario, username, nombre, apellido, saldo, excliente):
        self.id_usuario = id_usuario
        self.username = username
        self.nombre = nombre
        self.apellido = apellido
        self.saldo = saldo
        self.excliente = excliente

    @classmethod
    def obtener_todos(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                    SELECT u.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                    FROM USUARIO u
                             JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                    ORDER BY u.id_usuario \
                    """
            cursor.execute(query)

            # Convertir resultados a objetos Cliente
            clientes = []
            for row in cursor.fetchall():
                cliente = cls(
                    id_usuario=row[0],
                    username=row[1],
                    nombre=row[2],
                    apellido=row[3],
                    saldo=row[4],
                    excliente=row[5]
                )
                clientes.append(cliente)
            return clientes
        except Exception as e:
            raise Exception(f"Error al obtener clientes: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_clientes_activos(cls):
        """Obtiene solo los clientes activos (no exclientes)"""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                    SELECT u.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                    FROM USUARIO u
                             JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                    WHERE c.excliente = FALSE
                    ORDER BY u.id_usuario \
                    """
            cursor.execute(query)

            # Convertir resultados a objetos Cliente
            clientes = []
            for row in cursor.fetchall():
                cliente = cls(
                    id_usuario=row[0],
                    username=row[1],
                    nombre=row[2],
                    apellido=row[3],
                    saldo=row[4],
                    excliente=row[5]
                )
                clientes.append(cliente)
            return clientes
        except Exception as e:
            raise Exception(f"Error al obtener clientes activos: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_exclientes(cls):
        """Obtiene solo los exclientes (clientes eliminados)"""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                    SELECT u.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                    FROM USUARIO u
                             JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                    WHERE c.excliente = TRUE
                    ORDER BY u.id_usuario \
                    """
            cursor.execute(query)

            # Convertir resultados a objetos Cliente
            clientes = []
            for row in cursor.fetchall():
                cliente = cls(
                    id_usuario=row[0],
                    username=row[1],
                    nombre=row[2],
                    apellido=row[3],
                    saldo=row[4],
                    excliente=row[5]
                )
                clientes.append(cliente)
            return clientes
        except Exception as e:
            raise Exception(f"Error al obtener exclientes: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def buscar_por_termino(cls, termino):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                    SELECT u.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                    FROM USUARIO u
                             JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                    WHERE LOWER(u.nombre) LIKE %s
                       OR LOWER(u.apellido) LIKE %s
                       OR LOWER(u.username) LIKE %s
                    ORDER BY u.id_usuario \
                    """
            search_term = f"%{termino.lower()}%"
            cursor.execute(query, (search_term, search_term, search_term))

            # Convertir resultados a objetos Cliente
            clientes = []
            for row in cursor.fetchall():
                cliente = cls(
                    id_usuario=row[0],
                    username=row[1],
                    nombre=row[2],
                    apellido=row[3],
                    saldo=row[4],
                    excliente=row[5]
                )
                clientes.append(cliente)
            return clientes
        except Exception as e:
            raise Exception(f"Error al buscar clientes: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def buscar_clientes_activos_por_termino(cls, termino):
        """Busca solo clientes activos que coincidan con el término de búsqueda"""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                    SELECT u.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                    FROM USUARIO u
                             JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                    WHERE c.excliente = FALSE
                      AND (LOWER(u.nombre) LIKE %s
                       OR LOWER(u.apellido) LIKE %s
                       OR LOWER(u.username) LIKE %s)
                    ORDER BY u.id_usuario \
                    """
            search_term = f"%{termino.lower()}%"
            cursor.execute(query, (search_term, search_term, search_term))

            # Convertir resultados a objetos Cliente
            clientes = []
            for row in cursor.fetchall():
                cliente = cls(
                    id_usuario=row[0],
                    username=row[1],
                    nombre=row[2],
                    apellido=row[3],
                    saldo=row[4],
                    excliente=row[5]
                )
                clientes.append(cliente)
            return clientes
        except Exception as e:
            raise Exception(f"Error al buscar clientes activos: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_por_id(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = "SELECT c.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente FROM CLIENTE c JOIN USUARIO u ON c.id_usuario = u.id_usuario WHERE c.id_usuario = %s;"
        cursor.execute(query, (id_usuario,))
        cliente_data = cursor.fetchone()
        cursor.close()
        conexion.close()

        if cliente_data:
            return cls(
                id_usuario=cliente_data[0],
                username=cliente_data[1],
                nombre=cliente_data[2],
                apellido=cliente_data[3],
                saldo=cliente_data[4],
                excliente=cliente_data[5]
            )
        return None

    @classmethod
    def obtener_historial(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            query = """
                    SELECT u.nombre,
                           c.nombre AS nombre_contenido,
                           c.autor,
                           c.precio,
                           c.tamano_archivo,
                           d.fecha_y_hora AS fecha_descarga,
                           cat.nombre AS categoria
                    FROM DESCARGA d
                             JOIN USUARIO u ON d.id_usuario = u.id_usuario
                             JOIN CONTENIDO c ON d.id_contenido = c.id_contenido
                             JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                    WHERE u.id_usuario = %s
                    ORDER BY d.fecha_y_hora DESC LIMIT 20
                    """
            cursor.execute(query, (id_usuario,))

            description = cursor.description
            if description is None:
                return []
                
            columns = [col[0] for col in description]
            resultados_raw = cursor.fetchall()
            
            if not resultados_raw:
                return []

            resultados = [dict(zip(columns, row)) for row in resultados_raw]
            return resultados
        except Exception as e:
            raise Exception(f"Error al obtener historial: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar_saldo(cls, id_usuario, nuevo_saldo):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            # Verificar si el cliente existe
            cursor.execute("SELECT 1 FROM CLIENTE WHERE id_usuario = %s", (id_usuario,))
            if not cursor.fetchone():
                raise ValueError("Cliente no encontrado")

            # Actualizar saldo
            update_query = """
                           UPDATE CLIENTE
                           SET saldo = %s
                           WHERE id_usuario = %s RETURNING saldo \
                           """
            cursor.execute(update_query, (nuevo_saldo, id_usuario))
            resultado = cursor.fetchone()
            
            if resultado is None:
                raise Exception("No se pudo actualizar el saldo")
                
            saldo_actualizado = resultado[0]
            conexion.commit()

            return saldo_actualizado
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def marcar_como_excliente(cls, id_usuario, excliente=True):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            update_query = """
                           UPDATE CLIENTE
                           SET excliente = %s
                           WHERE id_usuario = %s RETURNING excliente \
                           """
            cursor.execute(update_query, (excliente, id_usuario))
            resultado = cursor.fetchone()
            
            if resultado is None:
                raise Exception("No se pudo actualizar el estado excliente")
                
            resultado_final = resultado[0]
            conexion.commit()

            return resultado_final
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al actualizar estado excliente: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

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

    @classmethod
    def recargar_saldo(cls, id_usuario, monto):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # Actualizar el saldo
            cursor.execute(
                """
                UPDATE CLIENTE 
                SET saldo = COALESCE(saldo, 0) + %s 
                WHERE id_usuario = %s 
                RETURNING saldo
                """,
                (monto, id_usuario)
            )
            
            resultado = cursor.fetchone()
            if resultado is None:
                raise Exception("No se pudo actualizar el saldo")
                
            nuevo_saldo = resultado[0]
            conexion.commit()
            
            # Registrar la transacción
            cursor.execute(
                """
                INSERT INTO TRANSACCION (
                    id_usuario, 
                    tipo, 
                    monto, 
                    descripcion
                ) VALUES (%s, %s, %s, %s)
                """,
                (id_usuario, 'RECARGA', monto, 'Recarga de saldo')
            )
            
            conexion.commit()
            
            return {
                "success": True, 
                "message": f"Se ha recargado S/. {float(monto):.2f} a tu cuenta",
                "nuevo_saldo": float(nuevo_saldo)
            }
                
        except Exception as e:
            conexion.rollback()
            print(f"Error en recargar_saldo: {str(e)}")
            return {"success": False, "error": f"Error al recargar saldo: {str(e)}"}
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_historial_compras(cls, id_usuario, limite=10):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            query = """
                SELECT 
                    c.id_compra,
                    c.fecha_y_hora,
                    co.id_contenido,
                    co.nombre AS nombre_contenido,
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
            """
            
            cursor.execute(query, (id_usuario, limite))
            
            description = cursor.description
            if description is None:
                return {
                    "success": True, 
                    "data": []
                }
                
            columns = [col[0] for col in description]
            resultados_raw = cursor.fetchall()
            
            if not resultados_raw:
                return {
                    "success": True, 
                    "data": []
                }
            
            resultados = [dict(zip(columns, row)) for row in resultados_raw]
            
            # Formatear los datos para el frontend
            historial_formateado = []
            for row in resultados:
                try:
                    # Obtener la calificación real del usuario para este contenido
                    from domain.entities.valoracion import Valoracion
                    calificacion_usuario = Valoracion.obtener_valoracion_usuario(id_usuario, row['id_contenido'])
                    calificacion_mostrar = int(calificacion_usuario) if calificacion_usuario > 0 else 0
                    
                    historial_formateado.append({
                        "id_compra": row['id_compra'],
                        "nombre_contenido": row['nombre_contenido'] or 'Sin nombre',
                        "autor": row['autor'] or 'Desconocido',
                        "precio": float(row['precio']) if row['precio'] is not None else 0.0,
                        "categoria": row['categoria'] or 'N/A',
                        "formato": row['formato'] or 'N/A',
                        "fecha_compra": row['fecha_y_hora'].strftime("%Y-%m-%d %H:%M:%S") if row['fecha_y_hora'] else 'Sin fecha',
                        "fecha_compra_raw": row['fecha_y_hora'].isoformat() if row['fecha_y_hora'] else None,
                        "calificacion": calificacion_mostrar
                    })
                    
                    # Debug log para verificar la fecha
                    print(f"Fecha de compra procesada: {row['fecha_y_hora']} -> {row['fecha_y_hora'].strftime('%Y-%m-%d %H:%M:%S') if row['fecha_y_hora'] else 'Sin fecha'}")
                except (TypeError, AttributeError, ValueError) as e:
                    print(f"Error procesando item del historial de compras: {e}")
                    continue  # Saltar elementos inválidos
            
            return {
                "success": True, 
                "data": historial_formateado
            }
            
        except Exception as e:
            print(f"Error en obtener_historial_compras: {str(e)}")
            return {"success": False, "error": f"Error al obtener el historial de compras: {str(e)}"}
        finally:
            cursor.close()
            conexion.close()