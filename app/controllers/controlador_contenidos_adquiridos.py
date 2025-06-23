from domain.entities.contenido import Contenido
from domain.entities.cliente import Cliente
from domain.entities.valoracion import Valoracion
from datetime import datetime, timedelta

class ControladorContenidosAdquiridos:
    def obtener_contenidos_adquiridos(self, id_usuario):
        """
        Obtiene todos los contenidos adquiridos por un usuario.
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            list: Lista de diccionarios con la información de los contenidos adquiridos
        """
        try:
            # Obtener el historial de descargas del usuario
            historial = Cliente.obtener_historial(id_usuario)
            
            if not historial:
                return []
                
            # Obtener detalles completos de cada contenido
            contenidos = []
            for item in historial:
                contenido = Contenido.obtener_por_id(item['id_contenido'])
                if contenido:
                    # Calcular si el contenido fue descargado en los últimos 7 días
                    fecha_descarga = item['fecha_descarga']
                    fecha_descarga = datetime.strptime(fecha_descarga, '%Y-%m-%d %H:%M:%S')
                    es_reciente = (datetime.now() - fecha_descarga) < timedelta(days=7)
                    
                    # Determinar el tipo de contenido basado en la extensión
                    tipo_contenido = self._determinar_tipo_contenido(contenido.formato.lower())
                    
                    contenidos.append({
                        'id_contenido': contenido.id_contenido,
                        'nombre': contenido.nombre,
                        'autor': contenido.autor,
                        'descripcion': contenido.descripcion or 'Sin descripción',
                        'fecha_descarga': fecha_descarga.strftime('%Y-%m-%d %H:%M:%S'),
                        'formato': contenido.formato,
                        'tipo_contenido': tipo_contenido,
                        'es_reciente': es_reciente,
                        'categoria': getattr(contenido, 'categoria', 'Sin categoría'),
                        'valoracion': Valoracion.obtener_valoracion_usuario(id_usuario, contenido.id_contenido)
                    })
            
            return contenidos
            
        except Exception as e:
            print(f"Error en obtener_contenidos_adquiridos: {str(e)}")
            raise Exception(f"Error al obtener contenidos adquiridos: {str(e)}")
    
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
    
    def calificar_contenido(self, id_usuario, id_contenido, puntuacion):
        """
        Guarda o actualiza la calificación de un usuario para un contenido.
        
        Args:
            id_usuario (int): ID del usuario
            id_contenido (int): ID del contenido
            puntuacion (int): Puntuación del 1 al 10
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validar que el usuario ha adquirido el contenido
            if not Valoracion.verificar_adquisicion_contenido(id_usuario, id_contenido):
                return {
                    'success': False,
                    'error': 'No has adquirido este contenido o no existe.'
                }
            
            # Validar que la puntuación esté en el rango correcto
            if puntuacion < 1 or puntuacion > 10:
                return {
                    'success': False,
                    'error': 'La puntuación debe estar entre 1 y 10.'
                }
            
            # Convertir la puntuación de 1-10 a 0-1 (escala de la base de datos)
            puntuacion_normalizada = float(puntuacion) / 10.0
            
            # Verificar si ya existe una valoración
            if Valoracion.existe_valoracion(id_usuario, id_contenido):
                # Actualizar valoración existente
                resultado = Valoracion.actualizar_valoracion(id_usuario, id_contenido, puntuacion_normalizada)
            else:
                # Insertar nueva valoración
                resultado = Valoracion.crear_valoracion(id_usuario, id_contenido, puntuacion_normalizada)
            
            if resultado.get('success'):
                return {
                    'success': True,
                    'message': '¡Gracias por tu valoración!',
                    'puntuacion': puntuacion
                }
            else:
                return resultado
            
        except Exception as e:
            print(f"Error en calificar_contenido: {str(e)}")
            return {
                'success': False,
                'error': f'Error al guardar la valoración: {str(e)}'
            }
    
    def descargar_contenido(self, id_usuario, id_contenido):
        """
        Obtiene la información necesaria para descargar un contenido.
        Solo permite una descarga por compra.
        
        Args:
            id_usuario (int): ID del usuario
            id_contenido (int): ID del contenido
            
        Returns:
            dict: Información del contenido para la descarga o mensaje de error
        """
        try:
            # Verificar que el usuario ha adquirido el contenido
            if not Valoracion.verificar_adquisicion_contenido(id_usuario, id_contenido):
                return {
                    'success': False,
                    'error': 'No has adquirido este contenido o no existe.'
                }
            
            # Obtener información del contenido
            info_contenido = Contenido.obtener_info_descarga(id_contenido)
            if not info_contenido:
                return {
                    'success': False,
                    'error': 'Contenido no encontrado.'
                }
            
            # Registrar la descarga en el historial
            descarga_registrada = Contenido.registrar_descarga(id_usuario, id_contenido)
            
            if not descarga_registrada:
                return {
                    'success': False,
                    'error': 'Ya has descargado este contenido. Solo puedes descargar una vez por compra.'
                }
            
            return {
                'success': True,
                'nombre': info_contenido['nombre'],
                'archivo': info_contenido['archivo'],
                'mime_type': self._obtener_mime_type(info_contenido['formato'])
            }
            
        except Exception as e:
            print(f"Error en descargar_contenido: {str(e)}")
            return {
                'success': False,
                'error': f'Error al procesar la descarga: {str(e)}'
            }
    
    def _obtener_mime_type(self, formato):
        """
        Obtiene el MIME type correspondiente a un formato de archivo.
        
        Args:
            formato (str): Extensión del archivo
            
        Returns:
            str: MIME type correspondiente
        """
        mime_types = {
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'wmv': 'video/x-ms-wmv',
            'flv': 'video/x-flv',
            'mkv': 'video/x-matroska',
            'webm': 'video/webm',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'webp': 'image/webp',
            'svg': 'image/svg+xml',
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'm4a': 'audio/mp4',
            'flac': 'audio/flac',
            'aac': 'audio/aac',
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed',
            '7z': 'application/x-7z-compressed',
            'txt': 'text/plain',
            'html': 'text/html',
            'css': 'text/css',
            'js': 'application/javascript',
            'json': 'application/json',
            'xml': 'application/xml'
        }
        
        return mime_types.get(formato.lower(), 'application/octet-stream')

    def obtener_mis_contenidos(self, id_usuario):
        """
        Obtiene y formatea los contenidos adquiridos por un usuario
        para ser enviados a la API.
        """
        try:
            # Llama al nuevo método en la entidad Contenido
            contenidos_adquiridos = Contenido.obtener_contenidos_adquiridos(id_usuario)

            # Formatear el tipo de contenido para la vista
            for contenido in contenidos_adquiridos:
                formato = contenido.get('formato', 'desconocido')
                contenido['tipo_contenido'] = self._determinar_tipo_contenido(formato)

            return {
                "success": True,
                "data": contenidos_adquiridos
            }
        except Exception as e:
            print(f"Error al obtener mis contenidos (controlador): {str(e)}")
            return {"success": False, "error": "No se pudieron cargar tus contenidos.", "data": []}
