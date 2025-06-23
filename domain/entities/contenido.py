from infrastructure.bd.conexion import obtener_conexion
from decimal import Decimal

class Contenido:
    def __init__(self, id_contenido, formato, autor, archivo, nombre, precio, tamano_archivo, descripcion,
                 id_tipo_archivo, id_promocion, id_categoria, categoria=None, extension=None, mime_type=None, promedio_valoracion=None):
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
        self.extension = extension
        self.mime_type = mime_type
        self.promedio_valoracion = promedio_valoracion

    @classmethod
    def obtener_promedio_valoracion(cls, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT COALESCE(AVG(puntuacion) * 10, 0) as promedio
                FROM VALORACION
                WHERE id_contenido = %s
            """, (id_contenido,))
            
            resultado = cursor.fetchone()
            return float(resultado[0]) if resultado and resultado[0] is not None else 0.0
            
        except Exception as e:
            print(f"Error al obtener promedio de valoración: {str(e)}")
            return 0.0
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_todos(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT 
                    c.id_contenido,
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
                    cat.nombre as categoria,
                    t.extension,
                    t.mime_type,
                    COALESCE(AVG(v.puntuacion) * 10, 0) as promedio_valoracion
                FROM CONTENIDO c
                LEFT JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                LEFT JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                LEFT JOIN VALORACION v ON c.id_contenido = v.id_contenido
                GROUP BY 
                    c.id_contenido,
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
                    cat.nombre,
                    t.extension,
                    t.mime_type
                ORDER BY c.nombre
            """)
            
            contenidos = []
            for row in cursor.fetchall():
                contenido = Contenido(
                    id_contenido=row[0],
                    formato=row[1],
                    autor=row[2],
                    archivo=row[3],
                    nombre=row[4],
                    precio=row[5],
                    tamano_archivo=row[6],
                    descripcion=row[7],
                    id_tipo_archivo=row[8],
                    id_promocion=row[9],
                    id_categoria=row[10],
                    categoria=row[11],
                    extension=row[12],
                    mime_type=row[13],
                    promedio_valoracion=float(row[14]) if row[14] is not None else 0.0
                )
                contenidos.append(contenido)
            
            return contenidos
            
        except Exception as e:
            print(f"Error al obtener todos los contenidos: {str(e)}")
            return []
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_por_id(cls, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT 
                    c.id_contenido,
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
                    cat.nombre as categoria,
                    t.extension,
                    t.mime_type,
                    COALESCE(AVG(v.puntuacion) * 10, 0) as promedio_valoracion
                FROM CONTENIDO c
                LEFT JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                LEFT JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                LEFT JOIN VALORACION v ON c.id_contenido = v.id_contenido
                WHERE c.id_contenido = %s
                GROUP BY 
                    c.id_contenido,
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
                    cat.nombre,
                    t.extension,
                    t.mime_type
            """, (id_contenido,))
            
            row = cursor.fetchone()
            if row:
                return Contenido(
                    id_contenido=row[0],
                    formato=row[1],
                    autor=row[2],
                    archivo=row[3],
                    nombre=row[4],
                    precio=row[5],
                    tamano_archivo=row[6],
                    descripcion=row[7],
                    id_tipo_archivo=row[8],
                    id_promocion=row[9],
                    id_categoria=row[10],
                    categoria=row[11],
                    extension=row[12],
                    mime_type=row[13],
                    promedio_valoracion=float(row[14]) if row[14] is not None else 0.0
                )
            return None
            
        except Exception as e:
            print(f"Error al obtener contenido por ID: {str(e)}")
            return None
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def agregar_contenido(cls, nombre, autor, precio, descripcion, archivo, tamano_archivo,
                          id_tipo_archivo, id_categoria, id_promocion=None):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                INSERT INTO CONTENIDO (nombre, autor, precio, descripcion, archivo, tamano_archivo, 
                                     id_tipo_archivo, id_categoria, id_promocion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_contenido
            """, (nombre, autor, precio, descripcion, archivo, tamano_archivo, 
                  id_tipo_archivo, id_categoria, id_promocion))
            
            resultado = cursor.fetchone()
            if resultado:
                id_contenido = resultado[0]
                conexion.commit()
                return id_contenido
            else:
                raise Exception("No se pudo obtener el ID del contenido insertado")
            
        except Exception as e:
            conexion.rollback()
            print(f"Error al agregar contenido: {str(e)}")
            raise Exception(f"Error al agregar contenido: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar_contenido(cls, id_contenido, **kwargs):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            campos_permitidos = {
                'nombre', 'autor', 'precio', 'descripcion', 'tamano_archivo',
                'id_tipo_archivo', 'id_categoria', 'id_promocion'
            }
            
            campos_actualizar = []
            valores = []
            
            for campo, valor in kwargs.items():
                if campo in campos_permitidos:
                    campos_actualizar.append(f"{campo} = %s")
                    valores.append(valor)
            
            if not campos_actualizar:
                raise ValueError("No se proporcionaron campos válidos para actualizar")
            
            valores.append(id_contenido)
            
            query = f"""
                UPDATE CONTENIDO 
                SET {', '.join(campos_actualizar)}
                WHERE id_contenido = %s
            """
            
            cursor.execute(query, valores)
            
            if cursor.rowcount == 0:
                raise Exception("No se encontró el contenido para actualizar")
            
            conexion.commit()
            return True
            
        except Exception as e:
            conexion.rollback()
            print(f"Error al actualizar contenido: {str(e)}")
            raise Exception(f"Error al actualizar contenido: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def eliminar(cls, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("DELETE FROM CONTENIDO WHERE id_contenido = %s", (id_contenido,))
            
            if cursor.rowcount == 0:
                raise Exception("No se encontró el contenido para eliminar")
            
            conexion.commit()
            return True
            
        except Exception as e:
            conexion.rollback()
            print(f"Error al eliminar contenido: {str(e)}")
            raise Exception(f"Error al eliminar contenido: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_contenidos_adquiridos(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            query = """
                SELECT DISTINCT
                    c.id_contenido,
                    c.nombre,
                    c.autor,
                    c.descripcion,
                    t.formato AS tipo_formato,
                    cat.nombre AS categoria,
                    CASE WHEN d.id_descarga IS NOT NULL THEN true ELSE false END AS ya_descargado,
                    co.fecha_y_hora AS fecha_adquisicion,
                    d.fecha_y_hora AS fecha_descarga,
                    CASE WHEN r.id_regalo IS NOT NULL THEN true ELSE false END AS es_regalo,
                    CASE WHEN r.abierto = true THEN true ELSE false END AS regalo_abierto,
                    u.nombre || ' ' || u.apellido AS remitente_regalo
                FROM COMPRA co
                JOIN CONTENIDO c ON co.id_contenido = c.id_contenido
                LEFT JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                LEFT JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                LEFT JOIN DESCARGA d ON c.id_contenido = d.id_contenido AND d.id_usuario = %s
                LEFT JOIN REGALO r ON co.id_compra = r.id_compra
                LEFT JOIN USUARIO u ON r.id_usuario_envia = u.id_usuario
                WHERE co.id_usuario = %s
                ORDER BY c.nombre;
            """
            cursor.execute(query, (id_usuario, id_usuario))
            rows = cursor.fetchall()

            contenidos_adquiridos = []
            for row in rows:
                id_contenido = row[0]
                
                from domain.entities.valoracion import Valoracion
                calificacion_promedio = Valoracion.obtener_promedio_valoracion(id_contenido)
                calificacion_usuario = Valoracion.obtener_valoracion_usuario(id_usuario, id_contenido)
                
                fecha_adquisicion = None
                fecha_descarga = None
                if row[7]:
                    fecha_adquisicion = row[7].strftime('%Y-%m-%d %H:%M:%S')
                if row[8]:
                    fecha_descarga = row[8].strftime('%Y-%m-%d %H:%M:%S')
                
                contenidos_adquiridos.append({
                    "id_contenido": id_contenido,
                    "nombre": row[1],
                    "autor": row[2],
                    "descripcion": row[3],
                    "formato": row[4] if row[4] else 'desconocido',
                    "tipo_contenido": row[4].lower() if row[4] else 'desconocido',
                    "categoria": row[5],
                    "ya_descargado": row[6],
                    "fecha_adquisicion": fecha_adquisicion,
                    "fecha_descarga": fecha_descarga,
                    "calificacion_promedio": round(calificacion_promedio, 1),
                    "calificacion_usuario": int(calificacion_usuario) if calificacion_usuario > 0 else 0,
                    "es_regalo": row[9] if row[9] is not None else False,
                    "regalo_abierto": row[10] if row[10] is not None else False,
                    "remitente_regalo": row[11] if row[11] else None
                })
            
            return contenidos_adquiridos
        except Exception as e:
            print(f"Error al obtener contenidos adquiridos (entidad): {str(e)}")
            return []
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_info_descarga(cls, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            cursor.execute("""
                SELECT c.nombre, c.archivo, t.formato
                FROM CONTENIDO c
                JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                WHERE c.id_contenido = %s
            """, (id_contenido,))
            
            contenido = cursor.fetchone()
            if not contenido:
                return None
            
            nombre_archivo, archivo_binario, formato = contenido
            
            return {
                'nombre': f"{nombre_archivo}.{formato}",
                'archivo': archivo_binario,
                'formato': formato
            }
            
        except Exception as e:
            print(f"Error al obtener info de descarga: {str(e)}")
            return None
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def registrar_descarga(cls, id_usuario, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            cursor.execute("""
                SELECT id_descarga FROM DESCARGA 
                WHERE id_usuario = %s AND id_contenido = %s
            """, (id_usuario, id_contenido))
            
            if cursor.fetchone():
                print(f"El usuario {id_usuario} ya ha descargado el contenido {id_contenido}")
                return False
            
            cursor.execute("""
                INSERT INTO DESCARGA (id_usuario, id_contenido, fecha_y_hora)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
            """, (id_usuario, id_contenido))
            
            conexion.commit()
            print(f"Descarga registrada para usuario {id_usuario}, contenido {id_contenido}")
            return True
            
        except Exception as e:
            conexion.rollback()
            print(f"Error al registrar descarga: {str(e)}")
            return False
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_contenidos_con_promociones(cls):
        conexion = None
        cursor = None
        
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            query = """
                SELECT 
                    c.id_contenido,
                    c.nombre,
                    c.autor,
                    c.descripcion,
                    c.precio,
                    c.tamano_archivo as tamano,
                    ta.formato,
                    cat.nombre as categoria,
                    p.descuento,
                    COALESCE(AVG(v.puntuacion) * 10, 0) as calificacion
                FROM CONTENIDO c
                INNER JOIN TIPO_ARCHIVO ta ON c.id_tipo_archivo = ta.id_tipo_archivo
                INNER JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                INNER JOIN PROMOCION p ON c.id_promocion = p.id_promocion
                LEFT JOIN VALORACION v ON c.id_contenido = v.id_contenido
                WHERE p.fecha_inicio <= CURRENT_DATE 
                AND p.fecha_fin >= CURRENT_DATE
                AND p.descuento > 0
                GROUP BY 
                    c.id_contenido,
                    c.nombre,
                    c.autor,
                    c.descripcion,
                    c.precio,
                    c.tamano_archivo,
                    ta.formato,
                    cat.nombre,
                    p.descuento
                ORDER BY c.nombre
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            contenidos = []
            for row in resultados:
                contenido = {
                    'id_contenido': row[0],
                    'nombre': row[1],
                    'autor': row[2],
                    'descripcion': row[3],
                    'precio': row[4],
                    'tamano': row[5],
                    'formato': row[6],
                    'categoria': row[7],
                    'descuento': row[8],
                    'calificacion': float(row[9]) if row[9] is not None else 0.0
                }
                contenidos.append(contenido)
            
            return contenidos
            
        except Exception as e:
            print(f"Error al obtener contenidos con promociones: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()
