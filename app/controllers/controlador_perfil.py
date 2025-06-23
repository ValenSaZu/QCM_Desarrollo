"""
Controlador para gestionar las operaciones relacionadas con el perfil del cliente.
"""
from domain.entities.cliente import Cliente
from domain.entities.usuario import Usuario
import hashlib
import os

class ControladorPerfil:
    def __init__(self):
        pass

    def obtener_datos_perfil(self, id_usuario):
        """
        Obtiene los datos del perfil de un usuario.
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            dict: Datos del perfil del usuario o None si no se encuentra
        """
        try:
            # Obtener los datos del cliente desde la base de datos
            cliente = Cliente.obtener_por_id(id_usuario)
            
            if not cliente:
                return None
                
            # Obtener el username del usuario
            username = Usuario.obtener_username_por_id(id_usuario)
                
            # Formatear los datos del perfil
            perfil = {
                "id_usuario": cliente.id_usuario,
                "username": username,
                "nombre": cliente.nombre,
                "apellido": cliente.apellido,
                "saldo": float(cliente.saldo) if cliente.saldo is not None else 0.0,
                "excliente": bool(cliente.excliente) if cliente.excliente is not None else False
            }
            
            return perfil
            
        except Exception as e:
            print(f"Error en obtener_datos_perfil: {str(e)}")
            raise Exception(f"Error al obtener datos del perfil: {str(e)}")
    
    def actualizar_perfil(self, id_usuario, datos_actualizados):
        """
        Actualiza los datos del perfil de un usuario.
        
        Args:
            id_usuario (int): ID del usuario
            datos_actualizados (dict): Diccionario con los datos a actualizar
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validar que el usuario exista
            if not Usuario.existe_usuario(id_usuario):
                return {"success": False, "error": "Usuario no encontrado"}
            
            # Actualizar perfil usando la entidad
            return Usuario.actualizar_perfil(id_usuario, datos_actualizados)
                
        except Exception as e:
            print(f"Error en actualizar_perfil: {str(e)}")
            return {"success": False, "error": f"Error al actualizar el perfil: {str(e)}"}
    
    def verificar_contrasena(self, id_usuario, contrasena):
        """
        Verifica si la contraseña proporcionada coincide con la del usuario.
        
        Args:
            id_usuario (int): ID del usuario
            contrasena (str): Contraseña a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        try:
            return Usuario.verificar_contrasena_por_id(id_usuario, contrasena)
        except Exception as e:
            print(f"Error en verificar_contrasena: {str(e)}")
            return False
    
    def cambiar_contrasena(self, id_usuario, contrasena_actual, nueva_contrasena):
        """
        Cambia la contraseña del usuario.
        
        Args:
            id_usuario (int): ID del usuario
            contrasena_actual (str): Contraseña actual
            nueva_contrasena (str): Nueva contraseña
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Verificar que la contraseña actual sea correcta
            if not self.verificar_contrasena(id_usuario, contrasena_actual):
                return {"success": False, "error": "La contraseña actual es incorrecta"}
            
            # Validar la nueva contraseña
            if not nueva_contrasena or len(nueva_contrasena) < 8:
                return {"success": False, "error": "La nueva contraseña debe tener al menos 8 caracteres"}
            
            # Hashear la nueva contraseña
            salt = os.environ.get("PASSWORD_SALT", "default_salt")
            nueva_contrasena_hash = hashlib.sha256((nueva_contrasena + salt).encode('utf-8')).hexdigest()
            
            # Cambiar contraseña usando la entidad
            return Usuario.cambiar_contrasena(id_usuario, nueva_contrasena_hash)
                
        except Exception as e:
            print(f"Error en cambiar_contrasena: {str(e)}")
            return {"success": False, "error": f"Error al cambiar la contraseña: {str(e)}"}
    
    def obtener_historial_compras(self, id_usuario, limite=10):
        """
        Obtiene el historial de compras de un usuario.
        
        Args:
            id_usuario (int): ID del usuario
            limite (int): Número máximo de registros a devolver
            
        Returns:
            dict: Historial de compras del usuario
        """
        try:
            return Cliente.obtener_historial_compras(id_usuario, limite)
        except Exception as e:
            print(f"Error en obtener_historial_compras: {str(e)}")
            return {"success": False, "error": f"Error al obtener el historial de compras: {str(e)}"}
    
    def recargar_saldo(self, id_usuario, monto):
        """
        Recarga saldo a la cuenta del usuario.
        
        Args:
            id_usuario (int): ID del usuario
            monto (float): Monto a recargar
            
        Returns:
            dict: Resultado de la operación con el nuevo saldo
        """
        try:
            # Validar que el monto sea positivo
            if monto <= 0:
                return {"success": False, "error": "El monto debe ser mayor a cero"}
            
            # Verificar que el usuario existe
            if not Cliente.existe_cliente(id_usuario):
                return {"success": False, "error": "Usuario no encontrado"}
            
            # Recargar saldo usando la entidad
            return Cliente.recargar_saldo(id_usuario, monto)
                
        except Exception as e:
            print(f"Error en recargar_saldo: {str(e)}")
            return {"success": False, "error": f"Error al recargar saldo: {str(e)}"}
    
    def eliminar_cuenta(self, id_usuario, contrasena):
        """
        Elimina la cuenta de un usuario (marcar como excliente).
        Solo permite eliminar si el saldo es 0.
        
        Args:
            id_usuario (int): ID del usuario
            contrasena (str): Contraseña del usuario para confirmar
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Verificar la contraseña
            if not self.verificar_contrasena(id_usuario, contrasena):
                return {"success": False, "error": "Contraseña incorrecta"}
            
            # Obtener datos del cliente para verificar el saldo
            cliente = Cliente.obtener_por_id(id_usuario)
            if not cliente:
                return {"success": False, "error": "Cliente no encontrado"}
            
            # Verificar que el saldo sea 0
            saldo_actual = float(cliente.saldo) if cliente.saldo is not None else 0.0
            if saldo_actual > 0:
                return {
                    "success": False, 
                    "error": f"No puedes eliminar tu cuenta mientras tengas un saldo de S/. {saldo_actual:.2f}. Debes gastar todo tu saldo antes de eliminar la cuenta."
                }
            
            # Marcar como excliente usando la entidad Cliente
            try:
                Cliente.marcar_como_excliente(id_usuario, True)
                return {"success": True, "message": "Cuenta eliminada correctamente"}
            except Exception as e:
                return {"success": False, "error": f"Error al marcar como excliente: {str(e)}"}
                
        except Exception as e:
            print(f"Error en eliminar_cuenta: {str(e)}")
            return {"success": False, "error": f"Error al eliminar la cuenta: {str(e)}"}

    def obtener_historial(self, id_usuario, limite=20):
        """
        Obtiene el historial de compras de un usuario.
        
        Args:
            id_usuario (int): ID del usuario
            limite (int): Número máximo de registros a devolver
            
        Returns:
            list: Lista de compras del usuario
        """
        try:
            # Usar el método de historial de compras
            resultado = Cliente.obtener_historial_compras(id_usuario, limite)
            
            # Verificar que el resultado sea válido
            if not resultado or not resultado.get('success'):
                return []
            
            return resultado.get('data', [])
            
        except Exception as e:
            print(f"Error en obtener_historial: {str(e)}")
            return []
