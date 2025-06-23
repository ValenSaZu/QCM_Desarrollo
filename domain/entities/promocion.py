from infrastructure.bd.conexion import obtener_conexion

class Promocion:
    def __init__(self, id_promocion, nombre, descuento, fecha_inicio, fecha_fin):
        self.id_promocion = id_promocion
        self.nombre = nombre
        self.descuento = descuento
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

    @classmethod
    def obtener_promocion_por_id(cls, id_promocion):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT * FROM promocion WHERE id_promocion = %s", (id_promocion,))
            row = cursor.fetchone()
            if row:
                return cls(
                    id_promocion=row[0],
                    nombre=row[1],
                    descuento=float(row[2]),
                    fecha_inicio=row[3],
                    fecha_fin=row[4]
                )
            return None
        except Exception as e:
            raise Exception(f"Error al obtener promoción: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_todas_promociones(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT * FROM promocion ORDER BY fecha_fin DESC")

            promociones = []
            for row in cursor.fetchall():
                promocion = cls(
                    id_promocion=row[0],
                    nombre=row[1],
                    descuento=float(row[2]),
                    fecha_inicio=row[3],
                    fecha_fin=row[4]
                )
                promociones.append(promocion)
            return promociones
        except Exception as e:
            raise Exception(f"Error al obtener promociones: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_contenido_promocion(cls, id_promocion):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            # Verificar que la promoción existe
            cursor.execute("SELECT 1 FROM promocion WHERE id_promocion = %s", (id_promocion,))
            if not cursor.fetchone():
                return []

            # Obtener los contenidos asociados a la promoción
            query = """
                SELECT c.id_contenido, c.nombre, t.formato, c.precio
                FROM contenido c
                LEFT JOIN tipo_archivo t ON c.id_tipo_archivo = t.id_tipo_archivo
                WHERE c.id_promocion = %s
                ORDER BY c.nombre
            """
            cursor.execute(query, (id_promocion,))

            # Devolver los resultados como una lista de diccionarios
            return [{
                'id_contenido': row[0],
                'nombre': row[1] or 'Sin nombre',
                'formato': row[2] or 'Desconocido',
                'precio': float(row[3]) if row[3] is not None else 0.0
            } for row in cursor.fetchall() if row[0] is not None]

        except Exception as e:
            raise Exception(f"Error al obtener contenido promociones: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def agregar_promocion(cls, nombre, descuento, fecha_inicio, fecha_fin):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """INSERT INTO promocion
                       (nombre, descuento, fecha_inicio, fecha_fin)
                   VALUES (%s, %s, %s, %s) RETURNING id_promocion""",
                (nombre, float(descuento), fecha_inicio, fecha_fin)
            )
            id_promocion_row = cursor.fetchone()
            if not id_promocion_row:
                raise Exception("No se pudo obtener el ID de la nueva promoción")
            id_promocion = id_promocion_row[0]
            conexion.commit()
            return id_promocion
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al agregar promoción: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar_promocion(cls, id_promocion, nombre, descuento, fecha_inicio, fecha_fin):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """UPDATE promocion
                   SET nombre       = %s,
                       descuento    = %s,
                       fecha_inicio = %s,
                       fecha_fin    = %s
                   WHERE id_promocion = %s""",
                (nombre, float(descuento), fecha_inicio, fecha_fin, id_promocion)
            )
            if cursor.rowcount == 0:
                raise Exception("Promoción no encontrada")
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al actualizar promoción: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def eliminar_promocion(cls, id_promocion):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "UPDATE contenido SET id_promocion = NULL WHERE id_promocion = %s",
                (id_promocion,)
            )

            cursor.execute(
                "DELETE FROM promocion WHERE id_promocion = %s",
                (id_promocion,)
            )

            if cursor.rowcount == 0:
                raise Exception("Promoción no encontrada")

            conexion.commit()
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al eliminar promoción: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def agregar_contenido_a_promocion(cls, id_promocion, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT 1 FROM promocion WHERE id_promocion = %s", (id_promocion,))
            if not cursor.fetchone():
                raise Exception("Promoción no encontrada")

            cursor.execute("SELECT 1 FROM contenido WHERE id_contenido = %s", (id_contenido,))
            if not cursor.fetchone():
                raise Exception("Contenido no encontrado")

            cursor.execute(
                "UPDATE contenido SET id_promocion = %s WHERE id_contenido = %s",
                (id_promocion, id_contenido)
            )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al agregar contenido a promoción: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def eliminar_contenido_de_promocion(cls, id_promocion, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "SELECT 1 FROM contenido WHERE id_contenido = %s AND id_promocion = %s",
                (id_contenido, id_promocion)
            )
            if not cursor.fetchone():
                raise Exception("El contenido no pertenece a esta promoción")

            cursor.execute(
                "UPDATE contenido SET id_promocion = NULL WHERE id_contenido = %s",
                (id_contenido,)
            )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al eliminar contenido de promoción: {str(e)}")
        finally:
            cursor.close()
            conexion.close()