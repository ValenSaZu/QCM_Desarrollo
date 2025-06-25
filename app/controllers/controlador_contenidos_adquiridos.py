from domain.entities.contenido import Contenido
from domain.entities.cliente import Cliente
from domain.entities.valoracion import Valoracion
from datetime import datetime, timedelta

# G-010: Controlador para gestión de contenidos adquiridos por usuarios que incluye:
# - Consulta de contenidos comprados/regalados
# - Proceso de descarga con control de límites
# - Sistema de valoración de contenidos
# - Gestión de tipos MIME para descargas
# - Formateo de datos para API
class ControladorContenidosAdquiridos:

    # CTRL-CONT-ADQ-001: Obtiene todos los contenidos adquiridos por un usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario a consultar
    # Retorna:
    #   list[dict]: Lista de contenidos con estructura:
    #       - id_contenido
    #       - nombre
    #       - tipo_adquisicion (compra/regalo)
    #       - fecha_adquisicion
    #       - descargas_disponibles
    # Excepciones:
    #   Exception: Si falla la consulta a la base de datos
    def obtener_contenidos_adquiridos(self, id_usuario):
        try:
            return Contenido.obtener_contenidos_adquiridos(id_usuario)
        except Exception as e:
            raise Exception(f"Error al obtener contenidos adquiridos: {str(e)}")

    # CTRL-CONT-ADQ-002: Determina el tipo de contenido (video/imagen/audio)
    # Parámetros:
    #   formato (str): Extensión o tipo de archivo
    # Retorna:
    #   str: 'video', 'imagen' o 'audio' (default: 'imagen')
    # Nota: Método interno usado para clasificación
    def _determinar_tipo_contenido(self, formato):
        return Contenido._determinar_tipo_contenido(formato)

    # CTRL-CONT-ADQ-003: Permite valorar un contenido adquirido (escala 1-10)
    # Parámetros:
    #   id_usuario (int): ID del usuario que valora
    #   id_contenido (int): ID del contenido a valorar
    #   puntuacion (int): Valor entre 1 y 10
    #   id_descarga (int): ID de descarga asociada (requerido)
    # Retorna:
    #   dict: {
    #       'success': bool,
    #       'message': str,
    #       'puntuacion': int | None,
    #       'error': str (si success=False)
    #   }
    # Validaciones:
    #   - Puntuación entre 1-10
    #   - ID de descarga requerido
    #   - Usuario debe haber descargado el contenido
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

    # CTRL-CONT-ADQ-004: Gestiona el proceso de descarga de un contenido
    # Parámetros:
    #   id_usuario (int): ID del usuario solicitante
    #   id_contenido (int): ID del contenido a descargar
    # Retorna:
    #   dict: {
    #       'success': bool,
    #       'nombre': str | None,
    #       'archivo': bytes | None,
    #       'mime_type': str | None,
    #       'error': str (si success=False)
    #   }
    # Validaciones:
    #   - Usuario debe tener derechos de descarga
    #   - Límite de descargas no excedido
    #   - Contenido debe existir
    def descargar_contenido(self, id_usuario, id_contenido):
        try:
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

    # CTRL-CONT-ADQ-005: Obtiene el tipo MIME correspondiente a un formato de archivo
    # Parámetros:
    #   formato (str): Extensión del archivo (ej: 'mp4', 'pdf')
    # Retorna:
    #   str: Tipo MIME correspondiente o 'application/octet-stream' por defecto
    # Nota: Método interno usado para descargas
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

    # CTRL-CONT-ADQ-006: Obtiene contenidos adquiridos formateados para API
    # Parámetros:
    #   id_usuario (int): ID del usuario a consultar
    # Retorna:
    #   dict: {
    #       'success': bool,
    #       'data': list[dict] | [],
    #       'error': str (si success=False)
    #   }
    # Campos adicionales en data:
    #   - tipo_contenido: Clasificación multimedia
    #   - info_formato: Metadatos técnicos
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

    # CTRL-CONT-ADQ-007: Obtiene descargas no valoradas por usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   id_contenido (int): ID del contenido (opcional)
    # Retorna:
    #   dict: {
    #       'success': bool,
    #       'data': list[dict] | []
    #   }
    # Campos en data:
    #   - id_descarga: Identificador único
    #   - fecha: Fecha de descarga formateada
    def obtener_descargas_no_valoradas(self, id_usuario, id_contenido):
        descargas = Valoracion.obtener_descargas_no_valoradas(id_usuario, id_contenido)
        return {"success": True, "data": [{"id_descarga": d[0], "fecha": d[1].strftime('%Y-%m-%d %H:%M:%S') if d[1] else None} for d in descargas]}