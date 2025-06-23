from domain.entities.contenido import Contenido
from domain.entities.cliente import Cliente
from domain.entities.valoracion import Valoracion
from datetime import datetime, timedelta

# G-010: Controlador para gestionar todas las operaciones relacionadas con contenidos adquiridos por usuarios
class ControladorContenidosAdquiridos:

    # CTRL-CONT-ADQ-001: Obtiene todos los contenidos adquiridos por un usuario tanto en compras como en regalos con información detallada
    def obtener_contenidos_adquiridos(self, id_usuario):
        try:
            return Contenido.obtener_contenidos_adquiridos(id_usuario)
        except Exception as e:
            raise Exception(f"Error al obtener contenidos adquiridos: {str(e)}")

    # CTRL-CONT-ADQ-002: Determina el tipo de contenido (video, imagen, audio) basado en su formato
    def _determinar_tipo_contenido(self, formato):
        return Contenido._determinar_tipo_contenido(formato)

    # CTRL-CONT-ADQ-003: Permite a un usuario calificar un contenido adquirido (rango 1-10)
    def calificar_contenido(self, id_usuario, id_contenido, puntuacion, id_descarga=None):
        try:
            if not id_descarga:
                return {'success': False, 'error': 'Falta id_descarga para valorar.'}
            if puntuacion < 1 or puntuacion > 10:
                return {'success': False, 'error': 'La puntuación debe estar entre 1 y 10.'}
            puntuacion_normalizada = float(puntuacion) / 10.0
            resultado = Valoracion.crear_valoracion_por_descarga(id_usuario, id_contenido, id_descarga, puntuacion_normalizada)
            if resultado.get('success'):
                return {'success': True, 'message': '¡Gracias por tu valoración!', 'puntuacion': puntuacion}
            else:
                return resultado
        except Exception as e:
            return {'success': False, 'error': f'Error al guardar la valoración: {str(e)}'}

    # CTRL-CONT-ADQ-004: Gestiona el proceso de descarga de un contenido adquirido (una sola descarga permitida por compra)
    def descargar_contenido(self, id_usuario, id_contenido):
        try:
            # Verificar si el usuario ha adquirido el contenido
            contenidos = Contenido.obtener_contenidos_adquiridos(id_usuario)
            contenido_info = next((c for c in contenidos if c["id_contenido"] == id_contenido), None)
            if not contenido_info or contenido_info["descargas_disponibles"] <= 0:
                return {
                    'success': False,
                    'error': 'No tienes descargas disponibles para este contenido.'
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
                    'error': 'Ya has descargado este contenido el número máximo de veces permitido.'
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
            return {
                "success": True,
                "data": contenidos_adquiridos
            }
        except Exception as e:
            return {"success": False, "error": "No se pudieron cargar tus contenidos.", "data": []}

    def obtener_descargas_no_valoradas(self, id_usuario, id_contenido):
        descargas = Valoracion.obtener_descargas_no_valoradas(id_usuario, id_contenido)
        return {"success": True, "data": [{"id_descarga": d[0], "fecha": d[1].strftime('%Y-%m-%d %H:%M:%S') if d[1] else None} for d in descargas]}