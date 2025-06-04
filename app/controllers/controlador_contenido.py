# Controlador para gestionar las operaciones relacionadas con contenidos digitales
from domain.entities.contenido import Contenido
from infrastructure.utils.archivos import procesar_archivo, determinar_tipo_archivo

class ControladorContenido:

    def manejar_agregar_contenido(self, form_data):
        """Procesa y guarda un nuevo contenido digital con sus metadatos y archivo asociado"""
        try:
            archivo_info = form_data['archivo']
            tipo_archivo = determinar_tipo_archivo(archivo_info['nombre'])
            if not tipo_archivo:
                raise Exception("Tipo de archivo no soportado")

            if not self.validar_categoria_existe(int(form_data['categoria_id'])):
                raise Exception("Categoría no válida")

            contenido = Contenido.agregar_contenido(
                nombre=form_data['nombre'],
                autor=form_data['autor'],
                precio=float(form_data['precio']),
                descripcion=form_data['descripcion'],
                archivo=archivo_info['contenido'],
                tamano_archivo=archivo_info['tamano'],
                id_tipo_archivo=tipo_archivo['id'],
                id_categoria=int(form_data['categoria_id'])
            )

            return {
                "success": True,
                "message": "Contenido agregado correctamente",
                "contenido": {
                    "id": contenido.id_contenido,
                    "nombre": contenido.nombre
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def validar_categoria_existe(self, id_categoria):
        """Verifica si una categoría existe en el sistema"""
        from domain.entities.categoria import Categoria
        try:
            categorias = Categoria.obtener_todas_categorias()
            return any(c.id_categoria == id_categoria for c in categorias)
        except:
            return False

    def obtener_contenidos(self):
        """Obtiene todos los contenidos disponibles con sus metadatos"""
        try:
            contenidos = Contenido.obtener_todos()
            if not contenidos:
                return []

            return [{
                'id': c.id_contenido,
                'nombre': c.nombre,
                'autor': c.autor,
                'precio': float(c.precio) if c.precio is not None else 0.0,
                'descripcion': c.descripcion,
                'tipo_archivo': c.formato,
                'categoria_id': c.id_categoria,
                'categoria': getattr(c, 'categoria', 'Sin categoría'),
                'tamano': c.tamano_archivo,
                'tiene_archivo': c.archivo is not None,
                'calificacion': getattr(c, 'promedio_valoracion', 0.0)
            } for c in contenidos]
        except Exception as e:
            raise

    def manejar_editar_contenido(self, id_contenido, form_data):
        """Actualiza la información y archivo de un contenido existente"""
        try:
            contenido = Contenido.obtener_por_id(id_contenido)
            if not contenido:
                return {"success": False, "error": "Contenido no encontrado"}

            categoria_id = form_data.get('categoria_id', contenido.id_categoria)
            if not self.validar_categoria_existe(categoria_id):
                return {"success": False, "error": f"La categoría con ID {categoria_id} no existe"}

            try:
                precio = float(form_data.get('precio', contenido.precio))
            except (ValueError, TypeError):
                return {"success": False, "error": "El precio proporcionado no es válido"}

            datos_actualizacion = {
                "nombre": form_data.get('nombre', contenido.nombre),
                "autor": form_data.get('autor', contenido.autor),
                "precio": precio,
                "descripcion": form_data.get('descripcion', contenido.descripcion),
                "id_categoria": categoria_id
            }

            if 'archivo' in form_data and form_data['archivo']:
                try:
                    if not isinstance(form_data['archivo'], str):
                        archivo_info = procesar_archivo(form_data['archivo'])
                        tipo_archivo = determinar_tipo_archivo(archivo_info['nombre'])

                        datos_actualizacion.update({
                            "archivo": archivo_info['contenido'],
                            "tamano_archivo": archivo_info['tamano'],
                            "id_tipo_archivo": tipo_archivo['id']
                        })
                except Exception as e:
                    return {"success": False, "error": f"Error al procesar el archivo: {str(e)}"}

            Contenido.actualizar_contenido(id_contenido, **datos_actualizacion)

            return {
                "success": True,
                "message": "Contenido actualizado correctamente"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def obtener_todos_contenidos(self):
        """Obtiene una lista simplificada de todos los contenidos"""
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

    def obtener_contenido(self, id_contenido):
        """Obtiene los detalles de un contenido específico por su ID"""
        contenido = Contenido.obtener_por_id(id_contenido)
        if contenido:
            return {
                "id_contenido": contenido.id_contenido,
                "nombre": contenido.nombre,
                "formato": contenido.formato,
                "categoria": contenido.categoria,
                "precio": contenido.precio,
                "autor": contenido.autor,
                "descripcion": contenido.descripcion
            }
        return None

    def eliminar_contenido(self, id_contenido):
        """Elimina un contenido del sistema por su ID"""
        try:
            if not id_contenido:
                return {"success": False, "error": "No se proporcionó un ID de contenido"}

            try:
                id_contenido = int(id_contenido)
                if id_contenido <= 0:
                    raise ValueError("ID inválido")
            except (ValueError, TypeError):
                return {"success": False, "error": "ID de contenido no válido"}

            if not Contenido.obtener_por_id(id_contenido):
                return {"success": False, "error": f"Contenido con ID {id_contenido} no encontrado"}

            eliminado = Contenido.eliminar(id_contenido)

            if eliminado:
                return {
                    "success": True,
                    "message": f"Contenido eliminado correctamente",
                    "deleted_id": id_contenido
                }
            return {"success": False, "error": "No se pudo eliminar el contenido"}
        except Exception as e:
            return {"success": False, "error": "Error al eliminar el contenido"}