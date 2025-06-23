from infrastructure.bd.conexion import obtener_conexion
import hashlib
import os

class Usuario:
    def __init__(self, id_usuario, username, contrasena, nombre, apellido):
        self.id_usuario = id_usuario
        self.username = username
        self.contrasena = contrasena
        self.nombre = nombre
        self.apellido = apellido

    @classmethod
    def registrar(cls, username, contrasena, nombre, apellido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query_usuario = """
                            INSERT INTO usuario (username, contrasena, nombre, apellido)
                            VALUES (%s, %s, %s, %s) RETURNING id_usuario; \
                            """
            cursor.execute(query_usuario, (username, contrasena, nombre, apellido))
            resultado = cursor.fetchone()
            
            if resultado is None:
                raise Exception("No se pudo obtener el ID del usuario registrado")
                
            id_usuario = resultado[0]

            query_cliente = """
                            INSERT INTO cliente(id_usuario, saldo, excliente)
                            VALUES (%s, 0, false); \
                            """
            cursor.execute(query_cliente, (id_usuario,))

            conexion.commit()
            return cls(id_usuario, username, contrasena, nombre, apellido)

        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def buscar_por_username(cls, username):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = "SELECT id_usuario, username, contrasena, nombre, apellido FROM usuario WHERE username = %s;"
        cursor.execute(query, (username,))
        usuario_data = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario_data:
            return cls(
                id_usuario=usuario_data[0],
                username=usuario_data[1],
                contrasena=usuario_data[2],
                nombre=usuario_data[3],
                apellido=usuario_data[4]
            )
        return None

    def verificar_contrasena(self, contrasena):
        return self.contrasena == contrasena

    @classmethod
    def obtener_username_por_id(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT username FROM USUARIO WHERE id_usuario = %s", (id_usuario,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else ""
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def existe_usuario(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id_usuario FROM USUARIO WHERE id_usuario = %s", (id_usuario,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar_perfil(cls, id_usuario, datos_actualizados):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # Actualizar solo los campos permitidos
            campos_permitidos = ["nombre", "apellido", "username"]
            actualizaciones = []
            valores = []
            
            for campo in campos_permitidos:
                if campo in datos_actualizados:
                    actualizaciones.append(f"{campo} = %s")
                    valores.append(datos_actualizados[campo])
            
            # Si no hay campos válidos para actualizar
            if not actualizaciones:
                return {"success": False, "error": "No se proporcionaron datos válidos para actualizar"}
            
            # Construir y ejecutar la consulta
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
            else:
                return {"success": False, "error": "No se pudo actualizar el perfil"}
                
        except Exception as e:
            conexion.rollback()
            print(f"Error en actualizar_perfil: {str(e)}")
            return {"success": False, "error": f"Error al actualizar el perfil: {str(e)}"}
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def verificar_contrasena_por_id(cls, id_usuario, contrasena):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # Obtener la contraseña guardada de la base de datos
            cursor.execute(
                "SELECT contrasena FROM USUARIO WHERE id_usuario = %s", 
                (id_usuario,)
            )
            resultado = cursor.fetchone()
            
            if not resultado:
                return False
                
            contrasena_guardada = resultado[0]
            
            # Verificar contraseña de manera compatible (hasheadas y sin hashear)
            return cls._verificar_contrasena_compatible(contrasena_guardada, contrasena)
            
        except Exception as e:
            print(f"Error en verificar_contrasena_por_id: {str(e)}")
            return False
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def _verificar_contrasena_compatible(cls, contrasena_guardada, contrasena_ingresada):
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

    @classmethod
    def cambiar_contrasena(cls, id_usuario, nueva_contrasena_hash):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # Actualizar la contraseña en la base de datos
            cursor.execute(
                "UPDATE USUARIO SET contrasena = %s WHERE id_usuario = %s RETURNING id_usuario",
                (nueva_contrasena_hash, id_usuario)
            )
            
            conexion.commit()
            
            if cursor.rowcount > 0:
                return {"success": True, "message": "Contraseña actualizada correctamente"}
            else:
                return {"success": False, "error": "No se pudo actualizar la contraseña"}
                
        except Exception as e:
            conexion.rollback()
            print(f"Error en cambiar_contrasena: {str(e)}")
            return {"success": False, "error": f"Error al cambiar la contraseña: {str(e)}"}
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def marcar_como_inactivo(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # Marcar como excliente en la tabla CLIENTE
            cursor.execute(
                "UPDATE CLIENTE SET excliente = TRUE WHERE id_usuario = %s RETURNING id_usuario",
                (id_usuario,)
            )
            
            conexion.commit()
            
            if cursor.rowcount > 0:
                return {"success": True, "message": "Cuenta eliminada correctamente"}
            else:
                return {"success": False, "error": "No se pudo eliminar la cuenta"}
                
        except Exception as e:
            conexion.rollback()
            print(f"Error en marcar_como_inactivo: {str(e)}")
            return {"success": False, "error": f"Error al eliminar la cuenta: {str(e)}"}
        finally:
            cursor.close()
            conexion.close()