from infrastructure.bd.conexion import obtener_conexion
from decimal import Decimal

class Contenido:
    def __init__(self, id_contenido, formato, autor, archivo, nombre, precio, tamano_archivo, descripcion,
                 id_tipo_archivo, id_promocion, id_categoria, categoria=None):
        self.id_contenido = id_contenido
        self.formato = formato
        self.autor = autor
        self.archivo = archivo
        self.nombre = nombre
        self.precio = precio
        self.tamano_archivo = tamano_archivo
        self.descripcion = descripcion
        self.id_tipo_archivo = id_tipo_archivo
        self.id_promocion = id_promocion
        self.id_categoria = id_categoria
        self.categoria = categoria

    @classmethod
    def obtener_promedio_valoracion(cls, id_contenido):
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            query = """
                SELECT AVG(puntuacion * 5) as promedio
                FROM VALORACION
                WHERE id_contenido = %s
                GROUP BY id_contenido
            """
            
            cursor.execute(query, (id_contenido,))
            resultado = cursor.fetchone()
            
            if resultado and resultado[0] is not None:
                # Redondear a un decimal y convertir a float
                return float(round(Decimal(resultado[0]), 1))
            return 0.0
            
        except Exception as e:
            print(f"Error al obtener promedio de valoración: {str(e)}")
            return 0.0
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conexion' in locals() and conexion is not None:
                conexion.close()

    @classmethod
    def obtener_todos(cls):
        import traceback

        print("Obteniendo conexión a la base de datos...")
        try:
            conexion = obtener_conexion()
            print("Conexión establecida correctamente")
            cursor = conexion.cursor()

            query = """
                    SELECT c.id_contenido,
                           c.nombre,
                           c.autor,
                           c.archivo,
                           c.precio,
                           c.tamano_archivo,
                           c.descripcion,
                           c.id_tipo_archivo,
                           c.id_promocion,
                           c.id_categoria,
                           cat.nombre                         AS categoria,
                           t.formato                          AS tipo_formato,
                           COALESCE(AVG(v.puntuacion * 5), 0) as promedio_valoracion
                    FROM CONTENIDO c
                             LEFT JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                             LEFT JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                             LEFT JOIN VALORACION v ON c.id_contenido = v.id_contenido
                    GROUP BY c.id_contenido, c.nombre, c.autor, c.archivo, c.precio,
                             c.tamano_archivo, c.descripcion, c.id_tipo_archivo,
                             c.id_promocion, c.id_categoria, cat.nombre, t.formato
                    ORDER BY c.id_contenido
                    """
            print("Ejecutando consulta SQL...")
            cursor.execute(query)
            print("Consulta ejecutada, obteniendo resultados...")

            rows = cursor.fetchall()
            print(f"Se encontraron {len(rows)} registros")

            contenidos = []
            for i, row in enumerate(rows, 1):
                try:
                    print(f"Procesando registro {i} de {len(rows)}")
                    # El promedio de valoración está en el índice 12 (row[12])
                    promedio_valoracion = float(row[12]) if row[12] is not None else 0.0

                    contenido = cls(
                        id_contenido=row[0],
                        nombre=row[1],
                        autor=row[2],
                        archivo=row[3],
                        precio=float(row[4]) if row[4] is not None else 0.0,
                        tamano_archivo=row[5],
                        descripcion=row[6],
                        id_tipo_archivo=row[7],
                        id_promocion=row[8],
                        id_categoria=row[9] if row[9] is not None else 0,
                        categoria=row[10] if row[10] is not None else 'Sin categoría',
                        formato=row[11] if row[11] is not None else 'Sin formato'
                    )
                    # Agregar el promedio de valoración como un atributo adicional
                    contenido.promedio_valoracion = round(promedio_valoracion, 1)
                    contenidos.append(contenido)
                except Exception as e:
                    print(f"Error al procesar el registro {i}: {str(e)}")
                    print(f"Datos del registro: {row}")
                    traceback.print_exc()
                    continue

            print(f"Procesamiento completado. {len(contenidos)} registros procesados correctamente.")
            return contenidos

        except Exception as e:
            error_msg = f"Error en obtener_todos: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            raise Exception(error_msg)

        finally:
            try:
                if 'cursor' in locals() and cursor is not None:
                    cursor.close()
                    print("Cursor cerrado correctamente")
            except Exception as e:
                print(f"Error al cerrar el cursor: {str(e)}")

            try:
                if 'conexion' in locals() and conexion is not None:
                    conexion.close()
                    print("Conexión cerrada correctamente")
            except Exception as e:
                print(f"Error al cerrar la conexión: {str(e)}")

    @classmethod
    def obtener_por_id(cls, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            query = """
                    SELECT c.id_contenido,
                           t.formato,
                           c.autor,
                           c.archivo,
                           c.nombre,
                           c.precio,
                           c.tamano_archivo,
                           c.descripcion,
                           c.id_tipo_archivo,
                           c.id_promocion,
                           c.id_categoria,
                           cat.nombre AS categoria,
                           t.formato AS tipo_formato
                    FROM CONTENIDO c
                    LEFT JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                    LEFT JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                    WHERE c.id_contenido = %s
                    """
            cursor.execute(query, (id_contenido,))
            row = cursor.fetchone()

            if row:
                return cls(
                    id_contenido=row[0],
                    formato=row[12] if row[12] is not None else 'Sin formato',
                    autor=row[2],
                    archivo=row[3],
                    nombre=row[4],
                    precio=row[5],
                    tamano_archivo=row[6],
                    descripcion=row[7],
                    id_tipo_archivo=row[8],
                    id_promocion=row[9],
                    id_categoria=row[10],
                    categoria=row[11]
                )
            return None
        except Exception as e:
            raise Exception(f"Error al obtener contenido: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def agregar_contenido(cls, nombre, autor, precio, descripcion, archivo, tamano_archivo,
                          id_tipo_archivo, id_categoria, id_promocion=None):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            query = """
                    INSERT INTO CONTENIDO
                    (nombre, autor, precio, descripcion, archivo, tamano_archivo,
                     id_tipo_archivo, id_categoria, id_promocion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_contenido \
                    """
            cursor.execute(query, (
                nombre, autor, precio, descripcion, archivo, tamano_archivo,
                id_tipo_archivo, id_categoria, id_promocion
            ))

            id_contenido = cursor.fetchone()[0]
            conexion.commit()

            cursor.execute("SELECT formato FROM TIPO_ARCHIVO WHERE id_tipo_archivo = %s", (id_tipo_archivo,))
            formato = cursor.fetchone()[0]

            return cls(
                id_contenido=id_contenido,
                nombre=nombre,
                autor=autor,
                precio=precio,
                descripcion=descripcion,
                tamano_archivo=tamano_archivo,
                archivo=archivo,
                id_tipo_archivo=id_tipo_archivo,
                id_categoria=id_categoria,
                id_promocion=id_promocion,
                formato=formato
            )
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al agregar contenido: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar_contenido(cls, id_contenido, **kwargs):
        """
        Actualiza un contenido existente en la base de datos.
        
        Args:
            id_contenido (int): ID del contenido a actualizar
            **kwargs: Campos a actualizar con sus nuevos valores
            
        Returns:
            int: ID del contenido actualizado
            
        Raises:
            Exception: Si ocurre un error durante la actualización
        """
        conexion = None
        cursor = None
        
        try:
            print(f"[DEBUG] Actualizando contenido ID {id_contenido} con datos: {kwargs}")
            
            # Validar que el ID del contenido sea válido
            if not id_contenido or not isinstance(id_contenido, int) or id_contenido <= 0:
                raise ValueError("ID de contenido no válido")
                
            # Validar que hay campos para actualizar
            if not kwargs:
                print("[WARNING] No se proporcionaron campos para actualizar")
                return id_contenido
                
            # Preparar la consulta SQL
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(id_contenido)

            query = f"""
                UPDATE CONTENIDO
                SET {set_clause}
                WHERE id_contenido = %s
                RETURNING id_contenido
            """
            
            print(f"[DEBUG] Ejecutando consulta: {query}")
            print(f"[DEBUG] Valores: {values}")
            
            # Obtener conexión y cursor
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            # Ejecutar la actualización
            cursor.execute(query, values)
            
            # Verificar que se actualizó exactamente un registro
            if cursor.rowcount == 0:
                raise ValueError(f"No se encontró el contenido con ID {id_contenido}")
                
            # Obtener el ID actualizado
            id_actualizado = cursor.fetchone()[0]
            conexion.commit()
            
            print(f"[DEBUG] Contenido {id_actualizado} actualizado exitosamente")
            return id_actualizado
            
        except Exception as e:
            # Hacer rollback en caso de error
            if conexion:
                conexion.rollback()
                
            # Loggear el error
            error_msg = f"Error al actualizar contenido ID {id_contenido}: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            print(f"[DEBUG] {traceback.format_exc()}")
            
            # Relanzar la excepción con un mensaje más descriptivo
            raise Exception(error_msg) from e
            
        finally:
            # Cerrar cursor y conexión
            try:
                if cursor:
                    cursor.close()
            except Exception as e:
                print(f"[WARNING] Error al cerrar el cursor: {str(e)}")
                
            try:
                if conexion:
                    conexion.close()
            except Exception as e:
                print(f"[WARNING] Error al cerrar la conexión: {str(e)}")

    @classmethod
    def eliminar(cls, id_contenido):
        """
        Elimina un contenido de la base de datos por su ID.
        
        Args:
            id_contenido (int): ID del contenido a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si no se encontró el contenido
            
        Raises:
            Exception: Si ocurre un error durante la eliminación
        """
        conexion = None
        cursor = None
        
        try:
            # Validar que el ID sea un entero positivo
            if not id_contenido or not isinstance(id_contenido, int) or id_contenido <= 0:
                print(f"[ERROR] ID de contenido no válido: {id_contenido}")
                return False
                
            print(f"[DEBUG] Iniciando eliminación de contenido ID: {id_contenido}")
            
            # Obtener conexión y cursor
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            # Verificar si el contenido existe antes de intentar eliminarlo
            cursor.execute(
                "SELECT id_contenido FROM CONTENIDO WHERE id_contenido = %s", 
                (id_contenido,)
            )
            
            if not cursor.fetchone():
                print(f"[WARNING] No se encontró contenido con ID {id_contenido} para eliminar")
                return False
                
            # Eliminar el contenido
            cursor.execute(
                "DELETE FROM CONTENIDO WHERE id_contenido = %s RETURNING id_contenido", 
                (id_contenido,)
            )
            
            # Verificar que se eliminó exactamente un registro
            if cursor.rowcount == 0:
                print(f"[WARNING] No se pudo eliminar el contenido con ID {id_contenido}")
                return False
                
            # Confirmar los cambios
            conexion.commit()
            print(f"[DEBUG] Contenido {id_contenido} eliminado exitosamente")
            return True
            
        except Exception as e:
            # Hacer rollback en caso de error
            if conexion:
                conexion.rollback()
                
            # Loggear el error
            import traceback
            error_msg = f"Error al eliminar contenido ID {id_contenido}: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[DEBUG] {traceback.format_exc()}")
            
            # Relanzar la excepción con un mensaje más descriptivo
            raise Exception(f"Error al eliminar el contenido: {str(e)}") from e
            
        finally:
            # Cerrar cursor y conexión
            try:
                if cursor:
                    cursor.close()
            except Exception as e:
                print(f"[WARNING] Error al cerrar el cursor: {str(e)}")
                
            try:
                if conexion:
                    conexion.close()
            except Exception as e:
                print(f"[WARNING] Error al cerrar la conexión: {str(e)}")