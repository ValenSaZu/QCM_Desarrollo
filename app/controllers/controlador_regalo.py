from domain.entities.regalo import Regalo

# G-013: Controlador para gestión de regalos entre usuarios que incluye:
# - Envío de contenidos como regalos
# - Consulta de regalos recibidos
# - Gestión de estado de regalos (abierto/cerrado)
class ControladorRegalo:

    # CTRL-REG-001: Envía un contenido como regalo entre usuarios
    # Parámetros:
    #   id_usuario_envia (int): ID del usuario que envía el regalo
    #   id_usuario_recibe (int): ID del usuario que recibe el regalo
    #   id_contenido (int): ID del contenido a regalar
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "message": str | None,
    #       "error": str (si success=False)
    #   }
    # Validaciones:
    #   - Usuarios deben existir
    #   - Contenido debe existir y ser regalable
    #   - Usuario no puede regalarse a sí mismo
    def enviar_regalo(self, id_usuario_envia, id_usuario_recibe, id_contenido):
        try:
            return Regalo.crear_regalo(id_usuario_envia, id_usuario_recibe, id_contenido)
        except Exception:
            return {"success": False, "error": "Error al enviar regalo"}

    # CTRL-REG-002: Obtiene todos los regalos recibidos por un usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario receptor
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "data": list[dict] | [],  # Lista de regalos con estructura:
    #           {
    #               "id_regalo": int,
    #               "id_contenido": int,
    #               "nombre_contenido": str,
    #               "id_usuario_envia": int,
    #               "nombre_envia": str,
    #               "fecha_envio": str (ISO format),
    #               "abierto": bool
    #           }
    #       "error": str (si success=False)
    #   }
    # Nota: Incluye tanto regalos abiertos como no abiertos
    def obtener_regalos_recibidos(self, id_usuario):
        try:
            regalos = Regalo.obtener_regalos_recibidos(id_usuario)
            return {"success": True, "data": regalos}
        except Exception:
            return {"success": False, "error": "Error al obtener regalos"}

    # CTRL-REG-003: Marca un regalo como abierto por el receptor
    # Parámetros:
    #   id_regalo (int): ID del regalo a marcar
    #   id_usuario (int): ID del usuario receptor (para validación)
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "message": str | None,
    #       "error": str (si success=False)
    #   }
    # Validaciones:
    #   - Regalo debe existir
    #   - Usuario debe ser el receptor real del regalo
    #   - Regalo no debe estar ya abierto
    def abrir_regalo(self, id_regalo, id_usuario):
        try:
            return Regalo.abrir_regalo(id_regalo, id_usuario)
        except Exception:
            return {"success": False, "error": "Error al abrir regalo"}