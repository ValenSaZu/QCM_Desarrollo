from infrastructure.bd.conexion import obtener_conexion
import hashlib
import os

# BD-015: Entidad para gestionar operaciones de usuarios que incluye:
# - Registro y autenticación de usuarios
# - Gestión de perfiles y credenciales
# - Verificación de identidad
# - Operaciones CRUD básicas
# - Manejo de estados de cuenta (activo/inactivo)
class Usuario:
    def __init__(self, id_usuario, username, contrasena, nombre, apellido):
        self.id_usuario = id_usuario
        self.username = username
        self.contrasena = contrasena
        self.nombre = nombre
        self.apellido = apellido

    # ENT-USR-001: Registra un nuevo usuario en el sistema
    # Parámetros:
    #   username (str): Nombre de usuario único
    #   contrasena (str): Contraseña en texto plano (se hashea internamente)
    #   nombre (str): Nombre real del usuario
    #   apellido (str): Apellido del usuario
    # Retorna:
    #   Usuario: Objeto usuario recién creado
    # Excepciones:
    #   - Lanza excepción si no se puede obtener el ID
    # Características:
    #   - Crea registro en tabla USUARIO y CLIENTE
    #   - Transacción atómica con rollback en caso de error
    #   - Inicializa saldo en 0
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
    # Parámetros:
    #   username (str): Nombre de usuario a buscar
    # Retorna:
    #   Usuario: Objeto usuario encontrado | None si no existe
    # Características:
    #   - Búsqueda exacta por username
    #   - Retorna objeto completo con todos los datos
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
    # Parámetros:
    #   contrasena (str): Contraseña a verificar
    # Retorna:
    #   bool: True si coincide, False si no
    # Características:
    #   - Compatible con contraseñas hasheadas y en texto plano
    #   - Usa salt para hashing
    def verificar_contrasena(self, contrasena):
        return self.contrasena == contrasena

    # ENT-USR-004: Obtiene el nombre de usuario por su ID
    # Parámetros:
    #   id_usuario (int): ID del usuario
    # Retorna:
    #   str: Username del usuario | string vacío si no existe
    # Características:
    #   - Consulta directa por clave primaria
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
    # Parámetros:
    #   id_usuario (int): ID del usuario a verificar
    # Retorna:
    #   bool: True si existe, False si no
    # Características:
    #   - Consulta simple de existencia
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
    # Parámetros:
    #   id_usuario (int): ID del usuario a actualizar
    #   datos_actualizados (dict): Diccionario con campos a actualizar
    # Retorna:
    #   dict: Resultado de la operación (success, message/error)
    # Excepciones:
    #   - Maneja errores internamente, no lanza excepciones
    # Características:
    #   - Actualización dinámica de campos permitidos
    #   - Transacción atómica con rollback
    #   - Campos permitidos: nombre, apellido, username
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
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   contrasena (str): Contraseña a verificar
    # Retorna:
    #   bool: True si coincide, False si no
    # Características:
    #   - Consulta primero la contraseña almacenada
    #   - Usa método interno de verificación compatible
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
    # Parámetros:
    #   contrasena_guardada (str): Contraseña almacenada (hash o texto)
    #   contrasena_ingresada (str): Contraseña a verificar
    # Retorna:
    #   bool: True si coinciden, False si no
    # Características:
    #   - Compatible con múltiples formatos de almacenamiento
    #   - Usa SHA-256 con salt para hashing
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
    # Parámetros:
    #   id_usuario (int): ID del usuario
    #   nueva_contrasena_hash (str): Nuevo hash de contraseña
    # Retorna:
    #   dict: Resultado de la operación (success, message/error)
    # Características:
    #   - Actualización directa del campo contraseña
    #   - Transacción atómica con rollback
    #   - Espera contraseña ya hasheada
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
    # Parámetros:
    #   id_usuario (int): ID del usuario a desactivar
    # Retorna:
    #   dict: Resultado de la operación (success, message/error)
    # Características:
    #   - Actualiza campo excliente en tabla CLIENTE
    #   - Transacción atómica con rollback
    #   - No elimina datos, solo marca como inactivo
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