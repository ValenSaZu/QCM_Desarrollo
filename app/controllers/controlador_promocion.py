# Controlador para gestionar las operaciones relacionadas con promociones
from domain.entities.promocion import Promocion
from datetime import datetime
from domain.entities.contenido import Contenido


class ControladorPromocion:

    def obtener_todas_promociones(self):
        """Obtiene todas las promociones disponibles"""
        try:
            promociones = Promocion.obtener_todas_promociones()
            if not promociones:
                return []
                
            return [{
                "id": promocion.id_promocion,
                "nombre": promocion.nombre,
                "porcentaje": float(promocion.descuento) if promocion.descuento is not None else 0.0,
                "fecha_inicio": promocion.fecha_inicio.isoformat() if hasattr(promocion.fecha_inicio, 'isoformat') else str(promocion.fecha_inicio),
                "fecha_fin": promocion.fecha_fin.isoformat() if hasattr(promocion.fecha_fin, 'isoformat') else str(promocion.fecha_fin)
            } for promocion in promociones]
        except Exception as e:
            print(f"Error en obtener_todas_promociones: {str(e)}")
            raise Exception(f"Error al obtener promociones: {str(e)}")

    def obtener_promocion_por_id(self, id_promocion):
        """Obtiene los detalles de una promoción específica por su ID"""
        try:
            if not id_promocion:
                raise ValueError("ID de promoción no proporcionado")
                
            promocion = Promocion.obtener_promocion_por_id(id_promocion)
            if not promocion:
                return {"error": "Promoción no encontrada", "success": False}

            contenidos = Promocion.obtener_contenido_promocion(id_promocion)
            return {
                "id": promocion.id_promocion,
                "nombre": promocion.nombre,
                "porcentaje": float(promocion.descuento) if promocion.descuento is not None else 0.0,
                "fecha_inicio": promocion.fecha_inicio.isoformat() if hasattr(promocion.fecha_inicio, 'isoformat') else str(promocion.fecha_inicio),
                "fecha_fin": promocion.fecha_fin.isoformat() if hasattr(promocion.fecha_fin, 'isoformat') else str(promocion.fecha_fin),
                "contenidos": [{
                    "id": contenido.get('id_contenido'),
                    "nombre": contenido.get('nombre', 'Sin nombre'),
                    "codigo": str(contenido.get('id_contenido', '')),
                    "formato": contenido.get('formato', 'Desconocido'),
                    "precio": float(contenido.get('precio', 0.0))
                } for contenido in (contenidos or []) if contenido],
                "success": True
            }
        except ValueError as ve:
            print(f"Error de validación en obtener_promocion_por_id: {str(ve)}")
            return {"error": f"Error de validación: {str(ve)}", "success": False}
        except Exception as e:
            print(f"Error en obtener_promocion_por_id: {str(e)}")
            return {"error": f"Error al obtener la promoción: {str(e)}", "success": False}

    def agregar_promocion(self, form_data):
        """Crea una nueva promoción con sus contenidos asociados"""
        try:
            print(f"Datos recibidos en agregar_promocion: {form_data}")
            
            # Obtener datos básicos de la promoción
            nombre = form_data.get('nombre')
            porcentaje = float(form_data.get('porcentaje'))
            fecha_inicio = datetime.strptime(form_data.get('fecha_inicio'), '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(form_data.get('fecha_fin'), '%Y-%m-%d').date()

            # Crear la promoción
            id_promocion = Promocion.agregar_promocion(
                nombre=nombre,
                descuento=porcentaje,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            
            print(f"Promoción creada con ID: {id_promocion}")

            # Obtener los contenidos a asociar
            contenidos = form_data.get('contenidos', [])
            print(f"Contenidos a asociar: {contenidos}")
            
            # Procesar los IDs de contenido
            contenidos_unicos = set()
            if isinstance(contenidos, list):
                # Convertir a enteros para eliminar duplicados
                try:
                    contenidos_unicos = {int(id) for id in contenidos if id and str(id).strip()}
                except (ValueError, TypeError) as e:
                    print(f"Error al procesar IDs de contenido: {e}")
            elif contenidos:
                try:
                    id_str = str(contenidos).strip()
                    if id_str:
                        contenidos_unicos = {int(id_str)}
                except (ValueError, TypeError) as e:
                    print(f"ID de contenido no válido: {contenidos}")
            
            print(f"Contenidos únicos a asociar: {contenidos_unicos}")
            
            # Procesar cada contenido único
            for id_contenido in contenidos_unicos:
                try:
                    print(f"Asociando contenido {id_contenido} a la promoción {id_promocion}")
                    Promocion.agregar_contenido_a_promocion(id_promocion, id_contenido)
                except Exception as e:
                    print(f"Error al asociar contenido {id_contenido} a la promoción: {str(e)}")
                    continue  # Continuar con el siguiente contenido si hay un error

            return {
                "success": True, 
                "message": "Promoción agregada correctamente", 
                "id_promocion": id_promocion
            }
            
        except Exception as e:
            print(f"Error en agregar_promocion: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def editar_promocion(self, id_promocion, promocion_data):
        """Actualiza una promoción existente y sus contenidos asociados"""
        try:
            print(f"Editando promoción {id_promocion} con datos: {promocion_data}")

            # Validar y obtener datos básicos
            try:
                nombre = promocion_data['nombre']
                porcentaje = float(promocion_data['porcentaje'])
                fecha_inicio = datetime.strptime(promocion_data['fecha_inicio'], '%Y-%m-%d').date()
                fecha_fin = datetime.strptime(promocion_data['fecha_fin'], '%Y-%m-%d').date()
            except (ValueError, TypeError) as e:
                error_msg = f"Error al procesar datos: {str(e)}"
                print(error_msg)
                return {"success": False, "error": error_msg}

            # Actualizar datos básicos
            Promocion.actualizar_promocion(
                id_promocion=id_promocion,
                nombre=nombre,
                descuento=porcentaje,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            # Procesar contenidos
            contenidos_raw = promocion_data.get('contenidos', []) or promocion_data.get('contenidos[]', [])
            print(f"[DEBUG] Contenidos raw: {contenidos_raw}")
            
            # Convertir a lista si no lo es
            if not isinstance(contenidos_raw, list):
                contenidos_raw = [contenidos_raw] if contenidos_raw else []
            
            contenidos_nuevos = set(map(str, contenidos_raw))
            print(f"[DEBUG] Contenidos nuevos procesados: {contenidos_nuevos}")

            # Obtener contenidos actuales
            contenidos_actuales = set()
            contenidos_db = Promocion.obtener_contenido_promocion(id_promocion) or []
            for c in contenidos_db:
                if c and c.get('id_contenido'):
                    contenidos_actuales.add(str(c.get('id_contenido')))

            print(f"Contenidos actuales: {contenidos_actuales}")
            print(f"Contenidos nuevos: {contenidos_nuevos}")

            # Eliminar contenidos que ya no están
            for id_contenido in (contenidos_actuales - contenidos_nuevos):
                try:
                    print(f"[DEBUG] Eliminando contenido {id_contenido}")
                    Promocion.eliminar_contenido_de_promocion(id_promocion, id_contenido)
                except Exception as e:
                    print(f"Error al eliminar contenido {id_contenido}: {str(e)}")

            # Agregar nuevos contenidos
            for id_contenido in (contenidos_nuevos - contenidos_actuales):
                try:
                    print(f"[DEBUG] Agregando contenido {id_contenido}")
                    Promocion.agregar_contenido_a_promocion(id_promocion, id_contenido)
                except Exception as e:
                    print(f"Error al agregar contenido {id_contenido}: {str(e)}")

            return {
                "success": True,
                "message": "Promoción actualizada correctamente",
                "id_promocion": id_promocion
            }
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}

    def eliminar_promocion(self, id_promocion):
        """Elimina una promoción del sistema"""
        try:
            Promocion.eliminar_promocion(id_promocion)
            return {"success": True, "message": "Promoción eliminada correctamente"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def obtener_contenidos_promocion(self, id_promocion):
        """Obtiene los contenidos asociados a una promoción específica"""
        try:
            promocion = self.obtener_promocion_por_id(id_promocion)
            if not promocion or not promocion.get("success", True):
                return {"success": False, "error": "Promoción no encontrada"}, 404

            return {
                "success": True,
                "contenidos": promocion.get("contenidos", []),
                "promocion": {
                    "porcentaje": promocion.get("porcentaje", 0)
                }
            }
        except Exception as e:
            print(f"Error en obtener_contenidos_promocion: {e}")
            return {"success": False, "error": str(e)}, 500

    def obtener_contenidos_con_promociones(self):
        """Obtiene todos los contenidos que tienen promociones activas"""
        try:
            # Obtener contenidos con promociones activas
            contenidos_con_promociones = Contenido.obtener_contenidos_con_promociones()
            
            if not contenidos_con_promociones:
                return {
                    "success": True,
                    "data": []
                }
            
            # Formatear los datos para la respuesta
            contenidos_formateados = []
            for contenido in contenidos_con_promociones:
                # Determinar el tipo de contenido basado en el formato
                formato = contenido.get('formato', 'desconocido')
                tipo_contenido = self._determinar_tipo_contenido(formato)
                
                contenidos_formateados.append({
                    "id_contenido": contenido.get('id_contenido'),
                    "nombre": contenido.get('nombre'),
                    "autor": contenido.get('autor'),
                    "descripcion": contenido.get('descripcion'),
                    "formato": contenido.get('formato'),
                    "tipo_contenido": tipo_contenido,
                    "categoria": contenido.get('categoria'),
                    "precio": float(contenido.get('precio', 0)) if contenido.get('precio') is not None else 0.0,
                    "tamano": contenido.get('tamano'),
                    "calificacion": float(contenido.get('calificacion', 0)) if contenido.get('calificacion') is not None else 0.0,
                    "descuento": float(contenido.get('descuento', 0)) if contenido.get('descuento') is not None else 0.0,
                    "fecha_descarga": contenido.get('fecha_descarga')
                })
            
            return {
                "success": True,
                "data": contenidos_formateados
            }
            
        except Exception as e:
            print(f"Error en obtener_contenidos_con_promociones: {str(e)}")
            return {
                "success": False,
                "error": f"Error al obtener contenidos con promociones: {str(e)}",
                "data": []
            }

    def _determinar_tipo_contenido(self, formato):
        """
        Determina el tipo de contenido basado en su formato.
        
        Args:
            formato (str): Formato del archivo
            
        Returns:
            str: 'video', 'imagen', 'audio' o 'otro'
        """
        if not formato or formato == 'desconocido':
            return 'otro'
            
        formato_lower = formato.lower().strip()
        
        formatos_video = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm']
        formatos_imagen = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'imagen']
        formatos_audio = ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac']
        
        if formato_lower in formatos_video:
            return 'video'
        elif formato_lower in formatos_imagen:
            return 'imagen'
        elif formato_lower in formatos_audio:
            return 'audio'
        return 'otro'