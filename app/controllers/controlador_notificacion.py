# Controlador para gestionar las notificaciones
from domain.entities.regalo import Regalo

class ControladorNotificacion:
    def obtener_notificaciones_regalos(self, id_usuario):
        """
        Obtiene las notificaciones de regalos sin abrir para un usuario.
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            dict: Lista de notificaciones de regalos
        """
        try:
            regalos_sin_abrir = Regalo.obtener_regalos_sin_abrir(id_usuario)
            return {
                "success": True, 
                "data": regalos_sin_abrir,
                "cantidad": len(regalos_sin_abrir)
            }
        except Exception as e:
            print(f"Error en obtener_notificaciones_regalos: {str(e)}")
            return {"success": False, "error": f"Error al obtener notificaciones: {str(e)}"}
    
    def marcar_notificacion_leida(self, id_usuario, id_regalo=None):
        """
        Marca una notificación específica o todas las notificaciones como leídas.
        
        Args:
            id_usuario (int): ID del usuario
            id_regalo (int, optional): ID del regalo específico. Si es None, marca todas como leídas
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            if id_regalo:
                # Marcar un regalo específico como abierto
                resultado = Regalo.abrir_regalo(id_regalo, id_usuario)
                if resultado["success"]:
                    return {"success": True, "message": "Notificación marcada como leída"}
                else:
                    return resultado
            else:
                # Marcar todos los regalos sin abrir como abiertos
                resultado = Regalo.marcar_todos_regalos_abiertos(id_usuario)
                if resultado["success"]:
                    return {"success": True, "message": "Todas las notificaciones marcadas como leídas"}
                else:
                    return resultado
                    
        except Exception as e:
            print(f"Error en marcar_notificacion_leida: {str(e)}")
            return {"success": False, "error": f"Error al marcar notificación como leída: {str(e)}"} 