from domain.entities.regalo import Regalo

# G-011: Controlador para gestionar las notificaciones de regalos de usuarios
class ControladorNotificacion:

    # CTRL-NOT-001: Obtiene las notificaciones de regalos pendientes para un usuario
    def obtener_notificaciones_regalos(self, id_usuario):
        try:
            regalos_sin_abrir = Regalo.obtener_regalos_sin_abrir(id_usuario)
            return {
                "success": True,
                "data": regalos_sin_abrir,
                "cantidad": len(regalos_sin_abrir)
            }
        except Exception as e:
            return {"success": False, "error": "Error al obtener notificaciones"}

    # CTRL-NOT-002: Marca notificaciones como leídas (individualmente o todas)
    def marcar_notificacion_leida(self, id_usuario, id_regalo=None):
        try:
            if id_regalo:
                resultado = Regalo.abrir_regalo(id_regalo, id_usuario)
                if resultado["success"]:
                    return {"success": True, "message": "Notificación marcada como leída"}
                return resultado
            else:
                resultado = Regalo.marcar_todos_regalos_abiertos(id_usuario)
                if resultado["success"]:
                    return {"success": True, "message": "Todas las notificaciones marcadas como leídas"}
                return resultado

        except Exception as e:
            return {"success": False, "error": "Error al actualizar notificaciones"}