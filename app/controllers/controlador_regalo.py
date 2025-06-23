# Controlador para gestionar las operaciones relacionadas con regalos
from domain.entities.regalo import Regalo

class ControladorRegalo:
    def enviar_regalo(self, id_usuario_envia, id_usuario_recibe, id_contenido):
        """
        Envía un regalo de un usuario a otro.
        
        Args:
            id_usuario_envia (int): ID del usuario que envía el regalo
            id_usuario_recibe (int): ID del usuario que recibe el regalo
            id_contenido (int): ID del contenido que se regala
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            resultado = Regalo.crear_regalo(id_usuario_envia, id_usuario_recibe, id_contenido)
            return resultado
        except Exception as e:
            print(f"Error en enviar_regalo: {str(e)}")
            return {"success": False, "error": f"Error al enviar regalo: {str(e)}"}

    def obtener_regalos_recibidos(self, id_usuario):
        """
        Obtiene los regalos recibidos por un usuario.
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            dict: Lista de regalos recibidos
        """
        try:
            regalos = Regalo.obtener_regalos_recibidos(id_usuario)
            return {"success": True, "data": regalos}
        except Exception as e:
            print(f"Error en obtener_regalos_recibidos: {str(e)}")
            return {"success": False, "error": f"Error al obtener regalos: {str(e)}"}

    def abrir_regalo(self, id_regalo, id_usuario):
        """
        Marca un regalo como abierto.
        
        Args:
            id_regalo (int): ID del regalo
            id_usuario (int): ID del usuario que abre el regalo
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            resultado = Regalo.abrir_regalo(id_regalo, id_usuario)
            return resultado
        except Exception as e:
            print(f"Error en abrir_regalo: {str(e)}")
            return {"success": False, "error": f"Error al abrir regalo: {str(e)}"} 