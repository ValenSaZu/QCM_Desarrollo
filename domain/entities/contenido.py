from infrastructure.bd.conexion import obtener_conexion
from decimal import Decimal
from datetime import datetime

# BD-008: Entidad para gestionar operaciones de contenido digital que incluye:
# - Gestión de metadatos de contenido (nombre, autor, formato, etc.)
# - Manejo de precios y promociones
# - Consulta de valoraciones y descargas
# - Operaciones CRUD para contenido
# - Gestión de descargas y adquisiciones
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
    # Parámetros:
    #   id_contenido (int): ID del contenido a consultar
    # Retorna:
    #   float: Promedio de valoración (0-10) o 0 si no hay valoraciones
    # Características:
    #   - Escala el promedio de 1-5 a 0-10
    #   - Maneja casos donde no hay valoraciones
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
    # Retorna:
    #   list[Contenido]: Lista completa de contenidos ordenados por nombre
    # Características:
    #   - Consulta JOIN entre CONTENIDO, TIPO_ARCHIVO y CATEGORIA
    #   - Incluye promedio de valoraciones
    #   - Ordenamiento alfabético por nombre
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
    # Parámetros:
    #   id_contenido (int): ID del contenido a buscar
    # Retorna:
    #   Contenido: Objeto con todos los datos del contenido | None si no existe
    # Características:
    #   - Consulta JOIN similar a ENT-CONT-002 pero filtrada por ID
    #   - Incluye metadatos completos y valoración promedio
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
    # Parámetros:
    #   nombre (str): Nombre del contenido
    #   autor (str): Autor/Creador
    #   precio (float): Precio base
    #   descripcion (str): Descripción detallada
    #   archivo (bin): Archivo binario del contenido
    #   tamano_archivo (int): Tamaño en bytes
    #   id_tipo_archivo (int): FK a tipo de archivo
    #   id_categoria (int): FK a categoría
    #   id_promocion (int|None): FK a promoción (opcional)
    # Retorna:
    #   Contenido: Objeto del contenido recién creado
    # Excepciones:
    #   - Lanza excepción si falla la inserción
    # Características:
    #   - Transacción atómica
    #   - Retorna el objeto completo con todos los datos
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
    # Parámetros:
    #   id_contenido (int): ID del contenido a actualizar
    #   **kwargs: Campos a actualizar (nombre, autor, precio, etc.)
    # Retorna:
    #   bool: True si la actualización fue exitosa
    # Excepciones:
    #   - Lanza excepción si no se encuentran campos válidos
    #   - Lanza excepción si el contenido no existe
    # Características:
    #   - Actualización dinámica de campos
    #   - Transacción atómica
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
    # Parámetros:
    #   id_contenido (int): ID del contenido a eliminar
    # Retorna:
    #   bool: True si la eliminación fue exitosa
    # Excepciones:
    #   - Lanza excepción si el contenido no existe
    # Características:
    #   - Elimina registros relacionados en tablas dependientes
    #   - Transacción atómica con múltiples operaciones
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
    # Parámetros:
    #   id_usuario (int): ID del usuario/cliente
    # Retorna:
    #   list[dict]: Lista de diccionarios con información detallada de cada contenido
    # Características:
    #   - Combina datos de compras, regalos y descargas
    #   - Incluye estadísticas de uso y valoraciones
    #   - Calcula descargas disponibles
    @classmethod
    def obtener_contenidos_adquiridos(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT c.id_contenido, c.nombre, c.autor, c.descripcion, t.formato AS tipo_formato, cat.nombre AS categoria, COUNT(*) as veces_comprado, MAX(co.fecha_y_hora) as fecha_compra_mas_reciente
                FROM COMPRA co
                JOIN CONTENIDO c ON co.id_contenido = c.id_contenido
                LEFT JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                LEFT JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                WHERE co.id_usuario = %s
                GROUP BY c.id_contenido, c.nombre, c.autor, c.descripcion, t.formato, cat.nombre
            """, (id_usuario,))
            compras = {row[0]: {"veces_comprado": row[6], "nombre": row[1], "autor": row[2], "descripcion": row[3], "formato": row[4], "categoria": row[5], "fecha_compra": row[7]} for row in cursor.fetchall()}

            cursor.execute("""
                SELECT c.id_contenido, c.nombre, c.autor, c.descripcion, t.formato AS tipo_formato, cat.nombre AS categoria, COUNT(*) as veces_regalado, MAX(comp.fecha_y_hora) as fecha_regalo_mas_reciente
                FROM REGALO r
                JOIN COMPRA comp ON r.id_compra = comp.id_compra
                JOIN CONTENIDO c ON r.id_contenido = c.id_contenido
                LEFT JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                LEFT JOIN CATEGORIA cat ON c.id_categoria = cat.id_categoria
                WHERE r.id_usuario_recibe = %s
                GROUP BY c.id_contenido, c.nombre, c.autor, c.descripcion, t.formato, cat.nombre
            """, (id_usuario,))
            regalos = {row[0]: {"veces_regalado": row[6], "nombre": row[1], "autor": row[2], "descripcion": row[3], "formato": row[4], "categoria": row[5], "fecha_regalo": row[7]} for row in cursor.fetchall()}

            contenidos = {}
            for id_contenido, data in compras.items():
                contenidos[id_contenido] = {
                    **data,
                    "veces_comprado": data["veces_comprado"],
                    "veces_regalado": 0,
                    "fecha_compra": data["fecha_compra"],
                    "fecha_regalo": None
                }
            for id_contenido, data in regalos.items():
                if id_contenido in contenidos:
                    contenidos[id_contenido]["veces_regalado"] = data["veces_regalado"]
                    contenidos[id_contenido]["fecha_regalo"] = data["fecha_regalo"]
                else:
                    contenidos[id_contenido] = {
                        **data,
                        "veces_comprado": 0,
                        "veces_regalado": data["veces_regalado"],
                        "fecha_compra": None,
                        "fecha_regalo": data["fecha_regalo"]
                    }

            cursor.execute("""
                SELECT id_contenido, COUNT(*) as veces_descargado
                FROM DESCARGA
                WHERE id_usuario = %s
                GROUP BY id_contenido
            """, (id_usuario,))
            descargas = {row[0]: row[1] for row in cursor.fetchall()}

            resultado = []
            for id_contenido, data in contenidos.items():
                veces_comprado = data["veces_comprado"]
                veces_regalado = data["veces_regalado"]
                veces_adquirido = veces_comprado + veces_regalado
                veces_descargado = descargas.get(id_contenido, 0)
                
                # Determinar la fecha de adquisición más reciente
                fecha_compra = data.get("fecha_compra")
                fecha_regalo = data.get("fecha_regalo")
                fecha_adquisicion = None
                
                if fecha_compra and fecha_regalo:
                    # Si tiene tanto compras como regalos, tomar la fecha más reciente
                    fecha_adquisicion = max(fecha_compra, fecha_regalo)
                elif fecha_compra:
                    fecha_adquisicion = fecha_compra
                elif fecha_regalo:
                    fecha_adquisicion = fecha_regalo
                
                # Formatear la fecha si existe
                if fecha_adquisicion:
                    try:
                        fecha_adquisicion = fecha_adquisicion.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        fecha_adquisicion = str(fecha_adquisicion)
                
                from domain.entities.valoracion import Valoracion
                calificacion_promedio = Valoracion.obtener_promedio_valoracion(id_contenido)
                calificacion_usuario = Valoracion.obtener_valoracion_usuario(id_usuario, id_contenido)
                ultima_valoracion = Valoracion.obtener_ultima_valoracion_usuario(id_usuario, id_contenido)
                if ultima_valoracion is None or not isinstance(ultima_valoracion, dict):
                    ultima_valoracion = {'puntuacion': None, 'fecha': None}
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
                        "calificacion_usuario": int(calificacion_usuario) if calificacion_usuario > 0 else 0,
                        "ultima_valoracion_usuario": ultima_valoracion,
                        "fecha_adquisicion": fecha_adquisicion
                    })
                    continue
                if 'puntuacion' not in ultima_valoracion or 'fecha' not in ultima_valoracion:
                    ultima_valoracion = {'puntuacion': None, 'fecha': None}
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
                        "calificacion_usuario": int(calificacion_usuario) if calificacion_usuario > 0 else 0,
                        "ultima_valoracion_usuario": ultima_valoracion,
                        "fecha_adquisicion": fecha_adquisicion
                    })
                    continue
                if ultima_valoracion['fecha'] is not None:
                    try:
                        ultima_valoracion['fecha'] = ultima_valoracion['fecha'].strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        ultima_valoracion['fecha'] = str(ultima_valoracion['fecha'])
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
                    "calificacion_usuario": int(calificacion_usuario) if calificacion_usuario > 0 else 0,
                    "ultima_valoracion_usuario": ultima_valoracion,
                    "fecha_adquisicion": fecha_adquisicion
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
    # Parámetros:
    #   id_contenido (int): ID del contenido a descargar
    # Retorna:
    #   dict: {'nombre': str, 'archivo': bin, 'formato': str} | None si no existe
    # Características:
    #   - Proporciona datos listos para generar respuesta de descarga
    #   - Incluye nombre formateado con extensión
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
    # Parámetros:
    #   id_usuario (int): ID del usuario que descarga
    #   id_contenido (int): ID del contenido descargado
    # Retorna:
    #   bool: True si el registro fue exitoso, False si no tiene descargas disponibles
    # Características:
    #   - Verifica límites de descargas según compras/regalos
    #   - Transacción atómica
    @classmethod
    def registrar_descarga(cls, id_usuario, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM COMPRA WHERE id_usuario = %s AND id_contenido = %s", (id_usuario, id_contenido))
            compras = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM REGALO r WHERE r.id_usuario_recibe = %s AND r.id_contenido = %s", (id_usuario, id_contenido))
            regalos = cursor.fetchone()[0]
            total_adquirido = compras + regalos
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

    # ENT-CONT-010: Obtiene contenidos con promociones activas
    # Retorna:
    #   list[dict]: Lista de contenidos con promoción vigente
    # Características:
    #   - Filtra por fechas de promoción válidas
    #   - Incluye información de descuento
    #   - Ordena alfabéticamente
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
                    ta.mime_type,
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
                    ta.mime_type,
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
                    'mime_type': row[7],
                    'categoria': row[8],
                    'descuento': row[9],
                    'calificacion': float(row[10]) if row[10] is not None else 0.0
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