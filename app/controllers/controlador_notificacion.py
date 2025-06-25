from domain.entities.regalo import Regalo

# G-011: Controlador para gestión de notificaciones de regalos que incluye:
# - Consulta de regalos pendientes
# - Marcado de notificaciones como leídas
# - Gestión individual y masiva de notificaciones
# - Conteo de regalos sin abrir
class ControladorNotificacion:

    # CTRL-NOT-001: Obtiene los regalos pendientes de visualización para un usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario a consultar
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "data": list[dict] - Lista de regalos pendientes con estructura:
    #           - id_regalo
    #           - id_contenido
    #           - nombre_contenido
    #           - id_usuario_remitente
    #           - nombre_remitente
    #           - fecha_envio
    #       "cantidad": int - Total de regalos pendientes
    #       "error": str (solo si success=False)
    #   }
    # Excepciones:
    #   - Captura errores de base de datos y los devuelve formateados
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

    # CTRL-NOT-002: Marca notificaciones de regalos como visualizadas
    # Parámetros:
    #   id_usuario (int): ID del usuario destinatario
    #   id_regalo (int|None): ID específico de regalo a marcar (opcional)
    #     Si None, marca todos los regalos pendientes del usuario
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "message": str - Mensaje de confirmación,
    #       "error": str (solo si success=False)
    #   }
    # Comportamiento:
    #   - Si se proporciona id_regalo: marca solo ese regalo como abierto
    #   - Si no se proporciona id_regalo: marca todos los regalos del usuario
    # Validaciones:
    #   - El regalo debe pertenecer al usuario destinatario
    #   - El regalo no debe estar ya marcado como abierto (para casos individuales
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