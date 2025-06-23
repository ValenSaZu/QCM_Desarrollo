from domain.entities.contenido import Contenido
from domain.entities.cliente import Cliente
from domain.entities.valoracion import Valoracion
from datetime import datetime, timedelta

# G-010: Controlador para gestionar todas las operaciones relacionadas con contenidos adquiridos por usuarios
class ControladorContenidosAdquiridos:

    # CTRL-CONT-ADQ-001: Obtiene todos los contenidos adquiridos por un usuario tanto en compras como en regalos con información detallada
    def obtener_contenidos_adquiridos(self, id_usuario):
        try:
            historial = Cliente.obtener_historial(id_usuario)

            if not historial:
                return []

            contenidos = []
            for item in historial:
                contenido = Contenido.obtener_por_id(item['id_contenido'])
                if contenido:
                    fecha_descarga = datetime.strptime(item['fecha_descarga'], '%Y-%m-%d %H:%M:%S')
                    es_reciente = (datetime.now() - fecha_descarga) < timedelta(days=7)

                    tipo_contenido = self._determinar_tipo_contenido(contenido.formato.lower())

                    es_regalo = item.get('tipo_adquisicion') == 'regalo'
                    tipo_adquisicion = 'Regalo' if es_regalo else 'Compra'

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
                        'valoracion': Valoracion.obtener_valoracion_usuario(id_usuario, contenido.id_contenido),
                        'tipo_adquisicion': tipo_adquisicion,
                        'es_regalo': es_regalo
                    })

            return contenidos

        except Exception as e:
            raise Exception(f"Error al obtener contenidos adquiridos: {str(e)}")

    # CTRL-CONT-ADQ-002: Determina el tipo de contenido (video, imagen, audio) basado en su formato
    def _determinar_tipo_contenido(self, formato):
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

    # CTRL-CONT-ADQ-003: Permite a un usuario calificar un contenido adquirido (rango 1-10)
    def calificar_contenido(self, id_usuario, id_contenido, puntuacion):
        try:
            if not Valoracion.verificar_adquisicion_contenido(id_usuario, id_contenido):
                return {
                    'success': False,
                    'error': 'No has adquirido este contenido o no existe.'
                }

            if puntuacion < 1 or puntuacion > 10:
                return {
                    'success': False,
                    'error': 'La puntuación debe estar entre 1 y 10.'
                }

            puntuacion_normalizada = float(puntuacion) / 10.0

            if Valoracion.existe_valoracion(id_usuario, id_contenido):
                resultado = Valoracion.actualizar_valoracion(id_usuario, id_contenido, puntuacion_normalizada)
            else:
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
            return {
                'success': False,
                'error': f'Error al guardar la valoración: {str(e)}'
            }

    # CTRL-CONT-ADQ-004: Gestiona el proceso de descarga de un contenido adquirido (una sola descarga permitida por compra)
    def descargar_contenido(self, id_usuario, id_contenido):
        try:
            if not Valoracion.verificar_adquisicion_contenido(id_usuario, id_contenido):
                return {
                    'success': False,
                    'error': 'No has adquirido este contenido o no existe.'
                }

            info_contenido = Contenido.obtener_info_descarga(id_contenido)
            if not info_contenido:
                return {
                    'success': False,
                    'error': 'Contenido no encontrado.'
                }

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
            return {
                'success': False,
                'error': f'Error al procesar la descarga: {str(e)}'
            }

    # CTRL-CONT-ADQ-005: Devuelve el MIME type correspondiente a un formato de archivo
    def _obtener_mime_type(self, formato):
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

    # CTRL-CONT-ADQ-006: Obtiene y formatea los contenidos adquiridos para ser enviados a la API
    def obtener_mis_contenidos(self, id_usuario):
        try:
            contenidos_adquiridos = Contenido.obtener_contenidos_adquiridos(id_usuario)

            for contenido in contenidos_adquiridos:
                formato = contenido.get('formato', 'desconocido')
                contenido['tipo_contenido'] = self._determinar_tipo_contenido(formato)

                if 'tipo_adquisicion' not in contenido:
                    contenido['tipo_adquisicion'] = 'Compra'
                    contenido['es_regalo'] = False

            return {
                "success": True,
                "data": contenidos_adquiridos
            }
        except Exception as e:
            return {"success": False, "error": "No se pudieron cargar tus contenidos.", "data": []}