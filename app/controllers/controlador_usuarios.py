# Controlador para gestionar las operaciones relacionadas con usuarios
from domain.entities.usuario import Usuario
import hashlib
import os

class ControladorUsuarios:

    def registrar_usuario(self, datos):
        """Registra un nuevo usuario en el sistema"""
        username = datos['username']
        contrasena = datos['password']
        nombre = datos['nombre']
        apellido = datos.get('apellido', '')

        if not username or not contrasena or not nombre:
            raise ValueError("Todos los campos obligatorios deben estar completos")

        if Usuario.buscar_por_username(username):
            raise ValueError("El nombre de usuario ya está en uso")

        # Hashear la contraseña antes de guardarla
        salt = os.environ.get("PASSWORD_SALT", "default_salt")
        contrasena_hash = hashlib.sha256((contrasena + salt).encode('utf-8')).hexdigest()

        usuario = Usuario.registrar(username, contrasena_hash, nombre, apellido)
        return {
            "mensaje": f"¡Bienvenido {nombre}! Registro exitoso.",
            "nombre": nombre,
            "apellido": apellido
        }

    def autenticar_usuario(self, datos):
        """Autentica un usuario existente en el sistema"""
        username = datos['username']
        contrasena = datos['password']

        if not username or not contrasena:
            raise ValueError("Usuario y contraseña son requeridos")

        usuario = Usuario.buscar_por_username(username)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Verificar contraseña (compatible con contraseñas hasheadas y sin hashear)
        if not self._verificar_contrasena_compatible(usuario.contrasena, contrasena):
            raise ValueError("Contraseña incorrecta")

        return {
            "success": True,
            "mensaje": f"Bienvenido de vuelta, {usuario.nombre}!",
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "user_id": usuario.id_usuario
        }

    def _verificar_contrasena_compatible(self, contrasena_guardada, contrasena_ingresada):
        """
        Verifica la contraseña de manera compatible con contraseñas hasheadas y sin hashear.
        Esto permite la transición gradual de contraseñas sin hashear a hasheadas.
        """
        # Primero intentar verificar como contraseña hasheada
        salt = os.environ.get("PASSWORD_SALT", "default_salt")
        contrasena_hash = hashlib.sha256((contrasena_ingresada + salt).encode('utf-8')).hexdigest()
        
        if contrasena_hash == contrasena_guardada:
            return True
        
        # Si no coincide, verificar como contraseña sin hashear (para usuarios existentes)
        if contrasena_ingresada == contrasena_guardada:
            return True
        
        return False

    def buscar_usuario_por_username(self, username):
        """Busca un usuario por username y retorna información básica"""
        try:
            if not username:
                return {"success": False, "error": "Username requerido"}

            usuario = Usuario.buscar_por_username(username)
            if not usuario:
                return {"success": False, "error": "Usuario no encontrado"}

            # Verificar que sea un cliente (no admin)
            from domain.entities.cliente import Cliente
            cliente = Cliente.obtener_por_id(usuario.id_usuario)
            if not cliente:
                return {"success": False, "error": "Usuario no es un cliente válido"}

            return {
                "success": True,
                "data": {
                    "id_usuario": usuario.id_usuario,
                    "username": usuario.username,
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido,
                    "nombre_completo": f"{usuario.nombre} {usuario.apellido}"
                }
            }
        except Exception as e:
            print(f"Error en buscar_usuario_por_username: {str(e)}")
            return {"success": False, "error": f"Error al buscar usuario: {str(e)}"}

    def determinar_tipo_usuario(self, user_id, username):
        """Determina si un usuario es administrador o cliente"""
        try:
            # Verificar si existe en la tabla de administradores
            from domain.entities.administrador import Administrador
            admin = Administrador.obtener_por_id(user_id)
            if admin:
                print(f"Usuario {username} (ID: {user_id}) encontrado en tabla administrador")
                return 'admin'
            else:
                print(f"Usuario {username} (ID: {user_id}) no encontrado en tabla administrador, es cliente")
                return 'cliente'
        except Exception as e:
            print(f"Error determinando tipo de usuario: {e}")
            return 'cliente'  # Por defecto, asumir cliente