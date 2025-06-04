# Controlador para gestionar las operaciones relacionadas con usuarios
from domain.entities.usuario import Usuario

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

        usuario = Usuario.registrar(username, contrasena, nombre, apellido)
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

        if not usuario.verificar_contrasena(contrasena):
            raise ValueError("Contraseña incorrecta")

        return {
            "mensaje": f"Bienvenido de vuelta, {usuario.nombre}!",
            "nombre": usuario.nombre,
            "apellido": usuario.apellido
        }