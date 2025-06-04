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
    def obtener_por_id(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                    SELECT u.id_usuario, u.username, u.nombre, u.apellido, c.saldo, c.excliente
                    FROM USUARIO u
                             JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                    WHERE u.id_usuario = %s \
                    """
            cursor.execute(query, (id_usuario,))
            row = cursor.fetchone()

            if not row:
                return None

            return cls(
                id_usuario=row[0],
                username=row[1],
                nombre=row[2],
                apellido=row[3],
                saldo=row[4],
                excliente=row[5]
            )
        except Exception as e:
            raise Exception(f"Error al obtener cliente: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_historial(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                    SELECT c.id_contenido,
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

            columns = [col[0] for col in cursor.description]
            resultados = [dict(zip(columns, row)) for row in cursor.fetchall()]

            if not resultados:
                return []

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
            saldo_actualizado = cursor.fetchone()[0]
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
            resultado = cursor.fetchone()[0]
            conexion.commit()

            return resultado
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al actualizar estado excliente: {str(e)}")
        finally:
            cursor.close()
            conexion.close()