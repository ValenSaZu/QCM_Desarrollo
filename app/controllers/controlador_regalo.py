from domain.entities.regalo import Regalo

# G-013: Controlador para gestionar todas las operaciones de regalos entre usuarios
class ControladorRegalo:

    # CTRL-REG-001: Envia un contenido como regalo de un usuario a otro
    def enviar_regalo(self, id_usuario_envia, id_usuario_recibe, id_contenido):
        try:
            return Regalo.crear_regalo(id_usuario_envia, id_usuario_recibe, id_contenido)
        except Exception:
            return {"success": False, "error": "Error al enviar regalo"}

    # CTRL-REG-002: Obtiene todos los regalos recibidos por un usuario
    def obtener_regalos_recibidos(self, id_usuario):
        try:
            regalos = Regalo.obtener_regalos_recibidos(id_usuario)
            return {"success": True, "data": regalos}
        except Exception:
            return {"success": False, "error": "Error al obtener regalos"}

    # CTRL-REG-003: Marca un regalo como abierto por el usuario receptor
    def abrir_regalo(self, id_regalo, id_usuario):
        try:
            return Regalo.abrir_regalo(id_regalo, id_usuario)
        except Exception:
            return {"success": False, "error": "Error al abrir regalo"}