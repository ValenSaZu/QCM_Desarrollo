from domain.entities.cliente import Cliente
from domain.entities.usuario import Usuario
import hashlib
import os

# G-012: Controlador para gestión completa de perfiles de usuario que incluye:
# - Obtención y actualización de datos de perfil
# - Gestión de credenciales (contraseñas)
# - Administración de saldo (recargas y consultas)
# - Historial de compras y transacciones
# - Eliminación segura de cuentas
class ControladorPerfil:

    # CTRL-PER-001: Obtiene todos los datos del perfil de un usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario a consultar
    # Retorna:
    #   dict: {
    #       "id_usuario": int,
    #       "username": str,
    #       "nombre": str,
    #       "apellido": str,
    #       "saldo": float (formateado a 2 decimales),
    #       "excliente": bool
    #   } | None si no existe
    # Excepciones:
    #   Exception: Si falla la consulta a la base de datos
    def obtener_datos_perfil(self, id_usuario):
        try:
            cliente = Cliente.obtener_por_id(id_usuario)
            if not cliente:
                return None
                
            username = Usuario.obtener_username_por_id(id_usuario)
                
            return {
                "id_usuario": cliente.id_usuario,
                "username": username,
                "nombre": cliente.nombre,
                "apellido": cliente.apellido,
                "saldo": float(cliente.saldo) if cliente.saldo is not None else 0.0,
                "excliente": bool(cliente.excliente) if cliente.excliente is not None else False
            }
            
        except Exception as e:
            raise Exception(f"Error al obtener datos del perfil: {str(e)}")

    # CTRL-PER-002: Actualiza la información básica del perfil
    # Parámetros:
    #   id_usuario (int): ID del usuario a actualizar
    #   datos_actualizados (dict): Campos a modificar {
    #       "nombre": str (opcional),
    #       "apellido": str (opcional),
    #       "username": str (opcional)
    #   }
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "message": str | None,
    #       "error": str (si success=False)
    #   }
    # Validaciones:
    #   - Usuario debe existir
    #   - Al menos un campo debe ser proporcionado
    def actualizar_perfil(self, id_usuario, datos_actualizados):
        try:
            if not Usuario.existe_usuario(id_usuario):
                return {"success": False, "error": "Usuario no encontrado"}
            
            return Usuario.actualizar_perfil(id_usuario, datos_actualizados)
                
        except Exception as e:
            return {"success": False, "error": "Error al actualizar el perfil"}

    # CTRL-PER-003: Verifica si una contraseña coincide con la del usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   contrasena (str): Contraseña a verificar (en texto plano)
    # Retorna:
    #   bool: True si coincide, False si no coincide o hay error
    # Nota: Maneja internamente el hashing de la contraseña
    def verificar_contrasena(self, id_usuario, contrasena):
        try:
            return Usuario.verificar_contrasena_por_id(id_usuario, contrasena)
        except Exception:
            return False

    # CTRL-PER-004: Cambia la contraseña del usuario con validaciones
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   contrasena_actual (str): Contraseña actual (en texto plano)
    #   nueva_contrasena (str): Nueva contraseña (en texto plano)
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "message": str | None,
    #       "error": str (si success=False)
    #   }
    # Validaciones:
    #   - Contraseña actual debe ser correcta
    #   - Nueva contraseña debe tener al menos 8 caracteres
    # Seguridad:
    #   - Aplica hash SHA256 con salt a la nueva contraseña
    def cambiar_contrasena(self, id_usuario, contrasena_actual, nueva_contrasena):
        try:
            if not self.verificar_contrasena(id_usuario, contrasena_actual):
                return {"success": False, "error": "La contraseña actual es incorrecta"}
            
            if not nueva_contrasena or len(nueva_contrasena) < 8:
                return {"success": False, "error": "La nueva contraseña debe tener al menos 8 caracteres"}
            
            salt = os.environ.get("PASSWORD_SALT", "default_salt")
            nueva_contrasena_hash = hashlib.sha256((nueva_contrasena + salt).encode('utf-8')).hexdigest()
            
            return Usuario.cambiar_contrasena(id_usuario, nueva_contrasena_hash)
                
        except Exception:
            return {"success": False, "error": "Error al cambiar la contraseña"}

    # CTRL-PER-005: Obtiene el historial reciente de compras
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   limite (int): Máximo de registros a devolver (default: 10)
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "data": list[dict] | None,
    #       "error": str (si success=False)
    #   }
    # Campos en data:
    #   - id_transaccion
    #   - fecha
    #   - monto
    #   - contenido_comprado
    def obtener_historial_compras(self, id_usuario, limite=10):
        try:
            return Cliente.obtener_historial_compras(id_usuario, limite)
        except Exception:
            return {"success": False, "error": "Error al obtener el historial"}

    # CTRL-PER-006: Recarga saldo a la cuenta del usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   monto (float): Cantidad a recargar (debe ser positivo)
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "nuevo_saldo": float | None,
    #       "error": str (si success=False)
    #   }
    # Validaciones:
    #   - Monto debe ser mayor a cero
    #   - Usuario debe existir
    def recargar_saldo(self, id_usuario, monto):
        try:
            if monto <= 0:
                return {"success": False, "error": "El monto debe ser mayor a cero"}
            
            if not Cliente.existe_cliente(id_usuario):
                return {"success": False, "error": "Usuario no encontrado"}
            
            return Cliente.recargar_saldo(id_usuario, monto)
                
        except Exception:
            return {"success": False, "error": "Error al recargar saldo"}

    # CTRL-PER-007: Elimina la cuenta de usuario (marcado lógico)
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   contrasena (str): Contraseña actual para confirmación
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "message": str | None,
    #       "error": str (si success=False)
    #   }
    # Validaciones:
    #   - Contraseña debe ser correcta
    #   - Saldo debe ser cero
    #   - Usuario debe existir
    def eliminar_cuenta(self, id_usuario, contrasena):
        try:
            if not self.verificar_contrasena(id_usuario, contrasena):
                return {"success": False, "error": "Contraseña incorrecta"}
            
            cliente = Cliente.obtener_por_id(id_usuario)
            if not cliente:
                return {"success": False, "error": "Cliente no encontrado"}
            
            saldo_actual = float(cliente.saldo) if cliente.saldo is not None else 0.0
            if saldo_actual > 0:
                return {
                    "success": False, 
                    "error": f"Debes gastar tu saldo de S/. {saldo_actual:.2f} antes de eliminar la cuenta"
                }
            
            Cliente.marcar_como_excliente(id_usuario, True)
            return {"success": True, "message": "Cuenta eliminada correctamente"}
                
        except Exception:
            return {"success": False, "error": "Error al eliminar la cuenta"}

    # CTRL-PER-008: Obtiene historial completo de transacciones
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   limite (int): Máximo de registros (default: 20)
    # Retorna:
    #   list[dict]: Lista de transacciones o lista vacía si hay error
    # Campos en cada transacción:
    #   - id_transaccion
    #   - tipo (compra/recarga)
    #   - fecha
    #   - monto
    #   - detalle
    def obtener_historial(self, id_usuario, limite=20):
        try:
            resultado = Cliente.obtener_historial_compras(id_usuario, limite)
            return resultado.get('data', []) if resultado and resultado.get('success') else []
            
        except Exception:
            return []