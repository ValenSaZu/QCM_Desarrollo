from domain.entities.contenido import Contenido
from domain.entities.categoria import Categoria
from infrastructure.utils.archivos import procesar_archivo, determinar_tipo_archivo

# G-005: Controlador para gestión de contenidos digitales que incluye:
# - CRUD de contenidos (creación, lectura, actualización, eliminación)
# - Validación de metadatos y archivos
# - Gestión de categorías asociadas
# - Procesamiento de archivos multimedia
# - Manejo de promociones y descuentos
class ControladorContenido:

    # CTRL-CONT-001: Crea un nuevo contenido digital con validación completa
    # Parámetros:
    #   contenido_data (dict): {
    #       'nombre': str (requerido),
    #       'autor': str (requerido),
    #       'precio': float (requerido, >=0),
    #       'descripcion': str (requerido),
    #       'id_categoria': int (requerido, debe existir),
    #       'archivo': dict (requerido) {
    #           'filename': str,
    #           'file_content': bytes
    #       }
    #   }
    # Retorna:
    #   dict: {
    #       'success': bool,
    #       'message': str,
    #       'contenido': dict (con ID y nombre) | None,
    #       'error': str (si success=False)
    #   }
    # Validaciones:
    #   - Campos requeridos presentes
    #   - Tipo de archivo soportado
    #   - Categoría existente
    #   - Precio válido no negativo
    def agregar_contenido(self, contenido_data):
        try:
            campos_requeridos = ['nombre', 'autor', 'precio', 'descripcion', 'id_categoria']
            for campo in campos_requeridos:
                if campo not in contenido_data or not contenido_data[campo]:
                    raise ValueError(f"El campo {campo} es requerido")

            archivo_info = contenido_data.get('archivo')
            if not archivo_info or not archivo_info.get('filename'):
                raise ValueError("No se ha proporcionado ningún archivo")

            tipo_archivo = determinar_tipo_archivo(archivo_info['filename'])
            if not tipo_archivo:
                raise ValueError("Tipo de archivo no soportado")

            try:
                categoria_id = int(contenido_data['id_categoria'])
                if not self.validar_categoria_existe(categoria_id):
                    raise ValueError("La categoría especificada no existe")
            except (ValueError, TypeError):
                raise ValueError("ID de categoría no válido")

            try:
                precio = float(contenido_data['precio'])
                if precio < 0:
                    raise ValueError("El precio no puede ser negativo")
            except (ValueError, TypeError):
                raise ValueError("Precio no válido")

            contenido = Contenido.agregar_contenido(
                nombre=contenido_data['nombre'].strip(),
                autor=contenido_data['autor'].strip(),
                precio=precio,
                descripcion=contenido_data['descripcion'].strip(),
                archivo=archivo_info['file_content'],
                tamano_archivo=len(archivo_info['file_content']),
                id_tipo_archivo=tipo_archivo['id'],
                id_categoria=categoria_id
            )

            if not contenido or not hasattr(contenido, 'id_contenido'):
                raise Exception("Error al guardar el contenido en la base de datos")

            return {
                "success": True,
                "message": "Contenido agregado correctamente",
                "contenido": {
                    "id": contenido.id_contenido,
                    "nombre": contenido.nombre
                }
            }
        except ValueError as ve:
            return {"success": False, "error": str(ve)}
        except Exception as e:
            return {"success": False, "error": "Ocurrió un error al procesar la solicitud."}

    # CTRL-CONT-002: Actualiza un contenido existente con validaciones
    # Parámetros:
    #   contenido_data (dict): {
    #       'id_contenido': int (requerido),
    #       ... (otros campos opcionales igual que agregar_contenido)
    #   }
    # Retorna:
    #   dict: {
    #       'success': bool,
    #       'message': str,
    #       'error': str (si success=False)
    #   }
    # Validaciones:
    #   - Contenido debe existir
    #   - Categoría debe existir (si se proporciona)
    #   - Archivo debe ser válido (si se proporciona)
    def actualizar_contenido(self, contenido_data):
        try:
            id_contenido = contenido_data.get("id_contenido")
            if not id_contenido:
                return {"success": False, "error": "ID de contenido no proporcionado"}

            contenido = Contenido.obtener_por_id(id_contenido)
            if not contenido:
                return {"success": False, "error": "Contenido no encontrado"}

            categoria_id = contenido_data.get('id_categoria', contenido.id_categoria)
            if not self.validar_categoria_existe(int(categoria_id)):
                return {"success": False, "error": f"La categoría con ID {categoria_id} no existe"}

            try:
                precio = float(contenido_data.get('precio', contenido.precio))
            except (ValueError, TypeError):
                return {"success": False, "error": "El precio proporcionado no es válido"}

            datos_actualizacion = {
                "nombre": contenido_data.get('nombre', contenido.nombre),
                "autor": contenido_data.get('autor', contenido.autor),
                "precio": precio,
                "descripcion": contenido_data.get('descripcion', contenido.descripcion),
                "id_categoria": int(categoria_id)
            }

            archivo_info = contenido_data.get('archivo')
            if archivo_info and archivo_info.get('filename'):
                try:
                    tipo_archivo = determinar_tipo_archivo(archivo_info['filename'])
                    datos_actualizacion.update({
                        "archivo": archivo_info['file_content'],
                        "tamano_archivo": len(archivo_info['file_content']),
                        "id_tipo_archivo": tipo_archivo['id']
                    })
                except Exception as e:
                    return {"success": False, "error": f"Error al procesar el archivo: {str(e)}"}

            Contenido.actualizar_contenido(id_contenido, **datos_actualizacion)

            return {"success": True, "message": "Contenido actualizado correctamente"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # CTRL-CONT-003: Valida existencia de una categoría
    # Parámetros:
    #   id_categoria (int): ID de categoría a validar
    # Retorna:
    #   bool: True si existe, False si no existe o hay error
    def validar_categoria_existe(self, id_categoria):
        try:
            categorias = Categoria.obtener_todas_categorias()
            return any(c.id_categoria == id_categoria for c in categorias)
        except:
            return False

    # CTRL-CONT-004: Obtiene todos los contenidos con metadatos completos
    # Retorna:
    #   dict: {
    #       'success': bool,
    #       'data': list[dict] | [],
    #       'error': str (si success=False)
    #   }
    # Campos por contenido:
    #   - Detalles básicos (nombre, autor, precio)
    #   - Información de descuentos (si aplica)
    #   - Metadatos técnicos (tamaño, formato, tipo MIME)
    #   - Información de categoría
    #   - Calificación promedio
    #   - URLs para acceso
    def obtener_contenidos(self):
        try:
            contenidos = Contenido.obtener_todos()
            if not contenidos:
                return {"success": True, "data": []}

            def mapear_tipo_contenido(formato):
                if not formato:
                    return 'imagen'
                formato_lower = formato.lower()
                if 'imagen' in formato_lower or 'jpg' in formato_lower or 'png' in formato_lower or 'gif' in formato_lower:
                    return 'imagen'
                elif 'video' in formato_lower or 'mp4' in formato_lower or 'avi' in formato_lower or 'mov' in formato_lower:
                    return 'video'
                elif 'audio' in formato_lower or 'mp3' in formato_lower or 'wav' in formato_lower or 'ogg' in formato_lower:
                    return 'audio'
                else:
                    return 'imagen'

            data = []
            for c in contenidos:
                if hasattr(c, 'id_contenido'):
                    from domain.entities.valoracion import Valoracion
                    calificacion_promedio = Valoracion.obtener_promedio_valoracion(c.id_contenido)

                    precio_descuento = None
                    porcentaje_descuento = None
                    if hasattr(c, 'id_promocion') and c.id_promocion:
                        from domain.entities.promocion import Promocion
                        promocion = Promocion.obtener_promocion_por_id(c.id_promocion)
                        if promocion:
                            from datetime import datetime
                            fecha_actual = datetime.now().date()
                            if promocion.fecha_inicio <= fecha_actual <= promocion.fecha_fin:
                                porcentaje_descuento = promocion.descuento
                                precio_descuento = float(c.precio) * (1 - promocion.descuento / 100.0)

                    def obtener_mime_type(formato):
                        if not formato:
                            return 'application/octet-stream'
                        formato_lower = formato.lower()
                        mime_types = {
                            'mp4': 'video/mp4',
                            'avi': 'video/x-msvideo',
                            'mov': 'video/quicktime',
                            'jpg': 'image/jpeg',
                            'jpeg': 'image/jpeg',
                            'png': 'image/png',
                            'gif': 'image/gif',
                            'mp3': 'audio/mpeg',
                            'wav': 'audio/wav',
                            'ogg': 'audio/ogg',
                            'pdf': 'application/pdf',
                            'doc': 'application/msword',
                            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        }
                        return mime_types.get(formato_lower, 'application/octet-stream')

                    contenido_data = {
                        'id_contenido': c.id_contenido,
                        'nombre': c.nombre or 'Sin nombre',
                        'autor': c.autor or 'Desconocido',
                        'precio': float(c.precio) if c.precio is not None else 0.0,
                        'precio_descuento': precio_descuento,
                        'porcentaje_descuento': porcentaje_descuento,
                        'descripcion': c.descripcion or '',
                        'tipo_contenido': mapear_tipo_contenido(c.formato),
                        'categoria_id': c.id_categoria if c.id_categoria is not None else 0,
                        'categoria': getattr(c, 'categoria', 'Sin categoría') or 'Sin categoría',
                        'tamano': int(c.tamano_archivo) if c.tamano_archivo is not None else 0,
                        'tamanio_bytes': int(c.tamano_archivo) if c.tamano_archivo is not None else 0,
                        'tiene_archivo': c.archivo is not None,
                        'calificacion': float(calificacion_promedio) if calificacion_promedio is not None else 0.0,
                        'formato': c.formato or 'desconocido',
                        'extension': c.extension or c.formato or 'desconocido',
                        'mime_type': c.mime_type or obtener_mime_type(c.formato),
                        'url_preview': f'/api/contenido/{c.id_contenido}/miniatura'
                    }
                    data.append(contenido_data)

            return {"success": True, "data": data}

        except Exception as e:
            return {"success": False, "error": str(e), "data": []}

    # CTRL-CONT-005: Obtiene lista simplificada de contenidos
    # Retorna:
    #   list[dict]: Lista con campos básicos de cada contenido:
    #       - id_contenido
    #       - nombre
    #       - autor
    #       - formato
    #       - categoría
    #       - precio
    #       - descripción
    def obtener_todos_contenidos(self):
        contenidos = Contenido.obtener_todos()
        return [{
            "id_contenido": contenido.id_contenido,
            "nombre": contenido.nombre,
            "autor": contenido.autor,
            "formato": contenido.formato,
            "categoria": contenido.categoria,
            "precio": contenido.precio,
            "descripcion": contenido.descripcion
        } for contenido in contenidos]

    # CTRL-CONT-006: Obtiene detalles completos de un contenido específico
    # Parámetros:
    #   id_contenido (int): ID del contenido a consultar
    # Retorna:
    #   dict: {
    #       'success': bool,
    #       'contenido': dict | None,
    #       'error': str (si success=False)
    #   }
    # Campos del contenido:
    #   - Todos los metadatos básicos
    #   - Código formateado (ej: '001')
    #   - Indicador de si tiene archivo asociado
    def obtener_contenido(self, id_contenido):
        try:
            contenido = Contenido.obtener_por_id(id_contenido)
            if contenido:
                return {
                    "success": True,
                    "contenido": {
                        "id_contenido": contenido.id_contenido,
                        "codigo": str(contenido.id_contenido).zfill(3),  # Formato: 001, 002, etc.
                        "nombre": contenido.nombre,
                        "descripcion": contenido.descripcion,
                        "autor": contenido.autor,
                        "precio": float(contenido.precio) if contenido.precio is not None else 0.0,
                        "id_categoria": contenido.id_categoria,
                        "categoria": getattr(contenido, 'categoria', 'Sin categoría'),
                        "formato": contenido.formato,
                        "tiene_archivo": contenido.archivo is not None
                    }
                }
            return {"success": False, "error": "Contenido no encontrado"}
        except Exception as e:
            return {"success": False, "error": f"Error al obtener contenido: {str(e)}"}

    # CTRL-CONT-007: Elimina un contenido del sistema
    # Parámetros:
    #   id_contenido (int): ID del contenido a eliminar
    # Retorna:
    #   dict: {
    #       'success': bool,
    #       'message': str,
    #       'deleted_id': int | None,
    #       'error': str (si success=False)
    #   }
    # Validaciones:
    #   - ID debe ser válido (>0)
    #   - Contenido debe existir
    def eliminar_contenido(self, id_contenido):
        try:
            if not id_contenido:
                return {"success": False, "error": "No se proporcionó un ID de contenido"}

            try:
                id_contenido = int(id_contenido)
                if id_contenido <= 0:
                    raise ValueError("ID inválido")
            except (ValueError, TypeError) as e:
                return {"success": False, "error": "ID de contenido no válido"}

            contenido_existente = Contenido.obtener_por_id(id_contenido)
            if not contenido_existente:
                return {"success": False, "error": f"Contenido con ID {id_contenido} no encontrado"}

            eliminado = Contenido.eliminar(id_contenido)

            if eliminado:
                return {
                    "success": True,
                    "message": f"Contenido '{contenido_existente.nombre}' eliminado correctamente",
                    "deleted_id": id_contenido
                }
            else:
                return {"success": False, "error": "No se pudo eliminar el contenido"}

        except Exception as e:
            return {"success": False, "error": f"Error al eliminar el contenido: {str(e)}"}