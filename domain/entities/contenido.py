from infrastructure.bd.conexion import obtener_conexion
from decimal import Decimal
from datetime import datetime

# BD-008: Entidad para gestionar operaciones de contenido digital
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

    # ENT-CONT-001: Obtiene el promedio de valoración de un contenido
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
            return 0.0
        finally:
            cursor.close()
            conexion.close()

    # ENT-CONT-002: Obtiene todos los contenidos disponibles
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
            return []
        finally:
            cursor.close()
            conexion.close()

    # ENT-CONT-003: Obtiene un contenido específico por su ID
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
            return None
        finally:
            cursor.close()
            conexion.close()

    # ENT-CONT-004: Agrega un nuevo contenido al sistema
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

                contenido_completo = cls.obtener_por_id(id_contenido)
                if contenido_completo:
                    return contenido_completo
                else:
                    raise Exception("Error al obtener el contenido después de insertarlo")
            else:
                raise Exception("No se pudo obtener el ID del contenido insertado")

        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al agregar contenido: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CONT-005: Actualiza la información de un contenido existente
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
            raise Exception(f"Error al actualizar contenido: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CONT-006: Elimina un contenido del sistema
    @classmethod
    def eliminar(cls, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("DELETE FROM CONTENIDO_CARRITO WHERE id_contenido = %s", (id_contenido,))

            cursor.execute("DELETE FROM REGALO WHERE id_contenido = %s", (id_contenido,))

            cursor.execute("DELETE FROM VALORACION WHERE id_contenido = %s", (id_contenido,))

            cursor.execute("DELETE FROM DESCARGA WHERE id_contenido = %s", (id_contenido,))

            cursor.execute("DELETE FROM COMPRA WHERE id_contenido = %s", (id_contenido,))

            cursor.execute("DELETE FROM CONTENIDO WHERE id_contenido = %s", (id_contenido,))

            if cursor.rowcount == 0:
                raise Exception("No se encontró el contenido para eliminar")

            conexion.commit()
            return True

        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al eliminar contenido: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CONT-007: Obtiene los contenidos adquiridos por un usuario
    @classmethod
    def obtener_contenidos_adquiridos(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            # Obtener compras
            cursor.execute("""
                SELECT c.id_contenido, c.nombre, c.autor, c.descripcion, t.formato AS tipo_formato, cat.nombre AS categoria, COUNT(*) as veces_comprado
                FROM COMPRA co
                JOIN CONTENIDO c ON co.id_contenido = c.id_contenido
                LEFT JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                LEFT JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                WHERE co.id_usuario = %s
                GROUP BY c.id_contenido, c.nombre, c.autor, c.descripcion, t.formato, cat.nombre
            """, (id_usuario,))
            compras = {row[0]: {"veces_comprado": row[6], "nombre": row[1], "autor": row[2], "descripcion": row[3], "formato": row[4], "categoria": row[5]} for row in cursor.fetchall()}

            # Obtener regalos
            cursor.execute("""
                SELECT c.id_contenido, c.nombre, c.autor, c.descripcion, t.formato AS tipo_formato, cat.nombre AS categoria, COUNT(*) as veces_regalado
                FROM REGALO r
                JOIN COMPRA comp ON r.id_compra = comp.id_compra
                JOIN CONTENIDO c ON r.id_contenido = c.id_contenido
                LEFT JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                LEFT JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                WHERE r.id_usuario_recibe = %s
                GROUP BY c.id_contenido, c.nombre, c.autor, c.descripcion, t.formato, cat.nombre
            """, (id_usuario,))
            regalos = {row[0]: {"veces_regalado": row[6], "nombre": row[1], "autor": row[2], "descripcion": row[3], "formato": row[4], "categoria": row[5]} for row in cursor.fetchall()}

            # Unir compras y regalos
            contenidos = {}
            for id_contenido, data in compras.items():
                contenidos[id_contenido] = {
                    **data,
                    "veces_comprado": data["veces_comprado"],
                    "veces_regalado": 0
                }
            for id_contenido, data in regalos.items():
                if id_contenido in contenidos:
                    contenidos[id_contenido]["veces_regalado"] = data["veces_regalado"]
                else:
                    contenidos[id_contenido] = {
                        **data,
                        "veces_comprado": 0,
                        "veces_regalado": data["veces_regalado"]
                    }

            # Obtener descargas
            cursor.execute("""
                SELECT id_contenido, COUNT(*) as veces_descargado
                FROM DESCARGA
                WHERE id_usuario = %s
                GROUP BY id_contenido
            """, (id_usuario,))
            descargas = {row[0]: row[1] for row in cursor.fetchall()}

            # Preparar respuesta
            resultado = []
            for id_contenido, data in contenidos.items():
                veces_comprado = data["veces_comprado"]
                veces_regalado = data["veces_regalado"]
                veces_adquirido = veces_comprado + veces_regalado
                veces_descargado = descargas.get(id_contenido, 0)
                from domain.entities.valoracion import Valoracion
                calificacion_promedio = Valoracion.obtener_promedio_valoracion(id_contenido)
                calificacion_usuario = Valoracion.obtener_valoracion_usuario(id_usuario, id_contenido)
                resultado.append({
                    "id_contenido": id_contenido,
                    "nombre": data["nombre"],
                    "autor": data["autor"],
                    "descripcion": data["descripcion"],
                    "formato": data["formato"] if data["formato"] else 'desconocido',
                    "tipo_contenido": cls._determinar_tipo_contenido(data["formato"]) if data["formato"] else 'desconocido',
                    "categoria": data["categoria"],
                    "veces_comprado": veces_comprado,
                    "veces_regalado": veces_regalado,
                    "veces_adquirido": veces_adquirido,
                    "veces_descargado": veces_descargado,
                    "descargas_disponibles": max(0, veces_adquirido - veces_descargado),
                    "calificacion_promedio": round(calificacion_promedio, 1),
                    "calificacion_usuario": int(calificacion_usuario) if calificacion_usuario > 0 else 0
                })
            return resultado
        except Exception as e:
            return []
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def _determinar_tipo_contenido(formato):
        if not formato:
            return 'desconocido'
        formato = formato.strip().lower()
        if any(ext == formato or ext in formato for ext in ['mp4', 'avi', 'mov', 'video']):
            return 'video'
        elif any(ext == formato or ext in formato for ext in ['jpg', 'png', 'gif', 'jpeg', 'imagen', 'image']):
            return 'imagen'
        elif any(ext == formato or ext in formato for ext in ['mp3', 'wav', 'ogg', 'audio']):
            return 'audio'
        return 'otro'

    # ENT-CONT-008: Obtiene información necesaria para descargar un contenido
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
            return None
        finally:
            cursor.close()
            conexion.close()

    # ENT-CONT-009: Registra una descarga de contenido por un usuario
    @classmethod
    def registrar_descarga(cls, id_usuario, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            # Contar compras y regalos
            cursor.execute("SELECT COUNT(*) FROM COMPRA WHERE id_usuario = %s AND id_contenido = %s", (id_usuario, id_contenido))
            compras = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM REGALO r WHERE r.id_usuario_recibe = %s AND r.id_contenido = %s", (id_usuario, id_contenido))
            regalos = cursor.fetchone()[0]
            total_adquirido = compras + regalos
            # Contar descargas
            cursor.execute("SELECT COUNT(*) FROM DESCARGA WHERE id_usuario = %s AND id_contenido = %s", (id_usuario, id_contenido))
            descargas = cursor.fetchone()[0]
            if descargas >= total_adquirido or total_adquirido == 0:
                return False
            cursor.execute("INSERT INTO DESCARGA (id_usuario, id_contenido, fecha_y_hora) VALUES (%s, %s, CURRENT_TIMESTAMP)", (id_usuario, id_contenido))
            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            return False
        finally:
            cursor.close()
            conexion.close()

    # ENT-CONT-010: Obtiene contenidos que tienen promociones activas
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
            return []
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()