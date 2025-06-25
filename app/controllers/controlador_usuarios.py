from domain.entities.usuario import Usuario
import hashlib
import os

# G-001: Controlador para gestión de usuarios que incluye:
# - Registro y autenticación de usuarios
# - Validación de credenciales
# - Búsqueda de usuarios
# - Gestión de tipos de usuario (admin/cliente)
# - Manejo seguro de contraseñas (hashing con salt)
class ControladorUsuarios:

    # CTRL-USR-001: Registra un nuevo usuario en el sistema
    # Parámetros:
    #   datos (dict): {
    #       'username': str (requerido, único),
    #       'password': str (requerido),
    #       'nombre': str (requerido),
    #       'apellido': str (opcional)
    #   }
    # Retorna:
    #   dict: {
    #       'success': bool (siempre True si no hay excepción),
    #       'mensaje': str,
    #       'nombre': str,
    #       'apellido': str
    #   }
    # Excepciones:
    #   ValueError: Si faltan campos obligatorios o username existe
    # Proceso:
    #   1. Valida campos obligatorios
    #   2. Verifica unicidad de username
    #   3. Aplica hash SHA256 con salt a la contraseña
    #   4. Crea registro en base de datos
    def registrar_usuario(self, datos):
        username = datos['username']
        contrasena = datos['password']
        nombre = datos['nombre']
        apellido = datos.get('apellido', '')

        if not username or not contrasena or not nombre:
            raise ValueError("Todos los campos obligatorios deben estar completos")

        if Usuario.buscar_por_username(username):
            raise ValueError("El nombre de usuario ya está en uso")

        salt = os.environ.get("PASSWORD_SALT", "default_salt")
        contrasena_hash = hashlib.sha256((contrasena + salt).encode('utf-8')).hexdigest()

        usuario = Usuario.registrar(username, contrasena_hash, nombre, apellido)
        return {
            "success": True,
            "mensaje": f"¡Bienvenido {nombre}! Registro exitoso.",
            "nombre": nombre,
            "apellido": apellido
        }

    # CTRL-USR-002: Autentica un usuario existente
    # Parámetros:
    #   datos (dict): {
    #       'username': str (requerido),
    #       'password': str (requerido)
    #   }
    # Retorna:
    #   dict: {
    #       'success': bool (siempre True si no hay excepción),
    #       'mensaje': str,
    #       'nombre': str,
    #       'apellido': str,
    #       'user_id': int
    #   }
    # Excepciones:
    #   ValueError: Si credenciales son inválidas
    # Seguridad:
    #   - Compatible con contraseñas en texto plano y hasheadas
    def autenticar_usuario(self, datos):
        username = datos['username']
        contrasena = datos['password']

        if not username or not contrasena:
            raise ValueError("Usuario y contraseña son requeridos")

        usuario = Usuario.buscar_por_username(username)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        if not self._verificar_contrasena_compatible(usuario.contrasena, contrasena):
            raise ValueError("Contraseña incorrecta")

        return {
            "success": True,
            "mensaje": f"Bienvenido de vuelta, {usuario.nombre}!",
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "user_id": usuario.id_usuario
        }

    # CTRL-USR-003: Verifica contraseña (método interno)
    # Parámetros:
    #   contrasena_guardada (str): Contraseña almacenada (hash o texto)
    #   contrasena_ingresada (str): Contraseña a verificar (texto plano)
    # Retorna:
    #   bool: True si coinciden, False si no
    # Nota:
    #   - Compatible con sistemas migrados de texto plano a hash
    #   - Usa salt de entorno para hashing
    def _verificar_contrasena_compatible(self, contrasena_guardada, contrasena_ingresada):
        salt = os.environ.get("PASSWORD_SALT", "default_salt")
        contrasena_hash = hashlib.sha256((contrasena_ingresada + salt).encode('utf-8')).hexdigest()

        if contrasena_hash == contrasena_guardada:
            return True

        if contrasena_ingresada == contrasena_guardada:
            return True

        return False

    # CTRL-USR-004: Busca usuario por username
    # Parámetros:
    #   username (str): Nombre de usuario a buscar
    # Retorna:
    #   dict: {
    #       'success': bool,
    #       'data': {
    #           'id_usuario': int,
    #           'username': str,
    #           'nombre': str,
    #           'apellido': str,
    #           'nombre_completo': str
    #       } | None,
    #       'error': str (si success=False)
    #   }
    # Validaciones:
    #   - Usuario debe existir
    #   - Usuario debe tener perfil de cliente
    def buscar_usuario_por_username(self, username):
        try:
            if not username:
                return {"success": False, "error": "Username requerido"}

            usuario = Usuario.buscar_por_username(username)
            if not usuario:
                return {"success": False, "error": "Usuario no encontrado"}

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
        except Exception:
            return {"success": False, "error": "Error al buscar usuario"}

    # CTRL-USR-005: Determina tipo de usuario (admin/cliente)
    # Parámetros:
    #   user_id (int): ID del usuario
    #   username (str): Nombre de usuario (no usado actualmente)
    # Retorna:
    #   str: 'admin' o 'cliente'
    # Nota:
    #   - Por defecto retorna 'cliente' si hay error
    #   - Actualmente no usa el parámetro username
    def determinar_tipo_usuario(self, user_id, username):
        try:
            from domain.entities.administrador import Administrador
            admin = Administrador.obtener_por_id(user_id)
            return 'admin' if admin else 'cliente'
        except Exception:
            return 'cliente'