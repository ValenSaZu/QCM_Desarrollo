from infrastructure.bd.conexion import obtener_conexion
import hashlib
import os

# BD-015: Entidad para gestionar operaciones de usuarios
class Usuario:
    def __init__(self, id_usuario, username, contrasena, nombre, apellido):
        self.id_usuario = id_usuario
        self.username = username
        self.contrasena = contrasena
        self.nombre = nombre
        self.apellido = apellido

    # ENT-USR-001: Registra un nuevo usuario en el sistema
    @classmethod
    def registrar(cls, username, contrasena, nombre, apellido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           INSERT INTO usuario (username, contrasena, nombre, apellido)
                           VALUES (%s, %s, %s, %s) RETURNING id_usuario
                           """, (username, contrasena, nombre, apellido))
            resultado = cursor.fetchone()

            if resultado is None:
                raise Exception("No se pudo obtener el ID del usuario registrado")

            id_usuario = resultado[0]

            cursor.execute("""
                           INSERT INTO cliente(id_usuario, saldo, excliente)
                           VALUES (%s, 0, false)
                           """, (id_usuario,))

            conexion.commit()
            return cls(id_usuario, username, contrasena, nombre, apellido)

        except Exception:
            conexion.rollback()
            raise Exception("Error al registrar usuario")
        finally:
            cursor.close()
            conexion.close()

    # ENT-USR-002: Busca un usuario por su nombre de usuario
    @classmethod
    def buscar_por_username(cls, username):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                           SELECT id_usuario, username, contrasena, nombre, apellido
                           FROM usuario
                           WHERE username = %s
                           """, (username,))
            usuario_data = cursor.fetchone()

            if usuario_data:
                return cls(
                    id_usuario=usuario_data[0],
                    username=usuario_data[1],
                    contrasena=usuario_data[2],
                    nombre=usuario_data[3],
                    apellido=usuario_data[4]
                )
            return None
        finally:
            cursor.close()
            conexion.close()

    # ENT-USR-003: Verifica si la contraseña proporcionada coincide
    def verificar_contrasena(self, contrasena):
        return self.contrasena == contrasena

    # ENT-USR-004: Obtiene el nombre de usuario por su ID
    @classmethod
    def obtener_username_por_id(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                           SELECT username
                           FROM USUARIO
                           WHERE id_usuario = %s
                           """, (id_usuario,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else ""
        finally:
            cursor.close()
            conexion.close()

    # ENT-USR-005: Verifica si un usuario existe
    @classmethod
    def existe_usuario(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                           SELECT id_usuario
                           FROM USUARIO
                           WHERE id_usuario = %s
                           """, (id_usuario,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conexion.close()

    # ENT-USR-006: Actualiza el perfil de usuario
    @classmethod
    def actualizar_perfil(cls, id_usuario, datos_actualizados):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            campos_permitidos = ["nombre", "apellido", "username"]
            actualizaciones = []
            valores = []

            for campo in campos_permitidos:
                if campo in datos_actualizados:
                    actualizaciones.append(f"{campo} = %s")
                    valores.append(datos_actualizados[campo])

            if not actualizaciones:
                return {"success": False, "error": "No se proporcionaron datos válidos para actualizar"}

            query = f"""
                UPDATE USUARIO 
                SET {', '.join(actualizaciones)}
                WHERE id_usuario = %s
                RETURNING id_usuario
            """
            valores.append(id_usuario)

            cursor.execute(query, valores)
            conexion.commit()

            if cursor.rowcount > 0:
                return {"success": True, "message": "Perfil actualizado correctamente"}
            return {"success": False, "error": "No se pudo actualizar el perfil"}

        except Exception:
            conexion.rollback()
            return {"success": False, "error": "Error al actualizar el perfil"}
        finally:
            cursor.close()
            conexion.close()

    # ENT-USR-007: Verifica la contraseña de un usuario por su ID
    @classmethod
    def verificar_contrasena_por_id(cls, id_usuario, contrasena):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT contrasena
                           FROM USUARIO
                           WHERE id_usuario = %s
                           """, (id_usuario,))
            resultado = cursor.fetchone()

            if not resultado:
                return False

            contrasena_guardada = resultado[0]
            return cls._verificar_contrasena_compatible(contrasena_guardada, contrasena)

        except Exception:
            return False
        finally:
            cursor.close()
            conexion.close()

    # ENT-USR-008: Método interno para verificación de contraseña compatible
    @classmethod
    def _verificar_contrasena_compatible(cls, contrasena_guardada, contrasena_ingresada):
        salt = os.environ.get("PASSWORD_SALT", "default_salt")
        contrasena_hash = hashlib.sha256((contrasena_ingresada + salt).encode('utf-8')).hexdigest()

        if contrasena_hash == contrasena_guardada:
            return True

        if contrasena_ingresada == contrasena_guardada:
            return True

        return False

    # ENT-USR-009: Cambia la contraseña de un usuario
    @classmethod
    def cambiar_contrasena(cls, id_usuario, nueva_contrasena_hash):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           UPDATE USUARIO
                           SET contrasena = %s
                           WHERE id_usuario = %s RETURNING id_usuario
                           """, (nueva_contrasena_hash, id_usuario))

            conexion.commit()

            if cursor.rowcount > 0:
                return {"success": True, "message": "Contraseña actualizada correctamente"}
            return {"success": False, "error": "No se pudo actualizar la contraseña"}

        except Exception:
            conexion.rollback()
            return {"success": False, "error": "Error al cambiar la contraseña"}
        finally:
            cursor.close()
            conexion.close()

    # ENT-USR-010: Marca un usuario como inactivo
    @classmethod
    def marcar_como_inactivo(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           UPDATE CLIENTE
                           SET excliente = TRUE
                           WHERE id_usuario = %s RETURNING id_usuario
                           """, (id_usuario,))

            conexion.commit()

            if cursor.rowcount > 0:
                return {"success": True, "message": "Cuenta eliminada correctamente"}
            return {"success": False, "error": "No se pudo eliminar la cuenta"}

        except Exception:
            conexion.rollback()
            return {"success": False, "error": "Error al eliminar la cuenta"}
        finally:
            cursor.close()
            conexion.close()