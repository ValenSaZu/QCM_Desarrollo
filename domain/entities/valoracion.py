from infrastructure.bd.conexion import obtener_conexion

class Valoracion:
    def __init__(self, id_valoracion, id_usuario, id_contenido, puntuacion, fecha):
        self.id_valoracion = id_valoracion
        self.id_usuario = id_usuario
        self.id_contenido = id_contenido
        self.puntuacion = puntuacion
        self.fecha = fecha

    @classmethod
    def obtener_valoracion_usuario(cls, id_usuario, id_contenido):
        """
        Obtiene la valoración que un usuario ha dado a un contenido.
        
        Args:
            id_usuario (int): ID del usuario
            id_contenido (int): ID del contenido
            
        Returns:
            float: Valoración del usuario (0 si no ha valorado) - escala 1-10
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            query = """
                SELECT puntuacion 
                FROM VALORACION 
                WHERE id_usuario = %s AND id_contenido = %s
            """
            cursor.execute(query, (id_usuario, id_contenido))
            resultado = cursor.fetchone()
            
            if resultado:
                # Convertir la puntuación de 0-1 a 1-10
                return float(resultado[0]) * 10
            return 0
            
        except Exception as e:
            print(f"Error al obtener valoración del usuario: {str(e)}")
            return 0
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_promedio_valoracion(cls, id_contenido):
        """
        Obtiene el promedio de valoraciones de un contenido.
        
        Args:
            id_contenido (int): ID del contenido
            
        Returns:
            float: Promedio de valoraciones (0 si no hay valoraciones) - escala 1-10
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            query = """
                SELECT AVG(puntuacion) 
                FROM VALORACION 
                WHERE id_contenido = %s
            """
            cursor.execute(query, (id_contenido,))
            resultado = cursor.fetchone()
            
            if resultado and resultado[0] is not None:
                # Convertir la puntuación de 0-1 a 1-10
                return float(resultado[0]) * 10
            return 0
            
        except Exception as e:
            print(f"Error al obtener promedio de valoración: {str(e)}")
            return 0
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def verificar_adquisicion_contenido(cls, id_usuario, id_contenido):
        """
        Verifica si el usuario ha adquirido el contenido.
        
        Args:
            id_usuario (int): ID del usuario
            id_contenido (int): ID del contenido
            
        Returns:
            bool: True si el usuario ha adquirido el contenido
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            cursor.execute("""
                SELECT 1 FROM COMPRA 
                WHERE id_usuario = %s AND id_contenido = %s
            """, (id_usuario, id_contenido))
            
            return cursor.fetchone() is not None
            
        except Exception as e:
            print(f"Error al verificar adquisición: {str(e)}")
            return False
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def existe_valoracion(cls, id_usuario, id_contenido):
        """
        Verifica si ya existe una valoración del usuario para el contenido.
        
        Args:
            id_usuario (int): ID del usuario
            id_contenido (int): ID del contenido
            
        Returns:
            bool: True si existe una valoración
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            cursor.execute("""
                SELECT id_valoracion FROM VALORACION 
                WHERE id_usuario = %s AND id_contenido = %s
            """, (id_usuario, id_contenido))
            
            return cursor.fetchone() is not None
            
        except Exception as e:
            print(f"Error al verificar existencia de valoración: {str(e)}")
            return False
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar_valoracion(cls, id_usuario, id_contenido, puntuacion_normalizada):
        """
        Actualiza una valoración existente.
        
        Args:
            id_usuario (int): ID del usuario
            id_contenido (int): ID del contenido
            puntuacion_normalizada (float): Puntuación normalizada (0-1)
            
        Returns:
            dict: Resultado de la operación
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            cursor.execute("""
                UPDATE VALORACION 
                SET puntuacion = %s, fecha = CURRENT_TIMESTAMP
                WHERE id_usuario = %s AND id_contenido = %s
            """, (puntuacion_normalizada, id_usuario, id_contenido))
            
            conexion.commit()
            
            if cursor.rowcount > 0:
                return {"success": True, "message": "Valoración actualizada correctamente"}
            else:
                return {"success": False, "error": "No se pudo actualizar la valoración"}
                
        except Exception as e:
            conexion.rollback()
            print(f"Error al actualizar valoración: {str(e)}")
            return {"success": False, "error": f"Error al actualizar valoración: {str(e)}"}
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def crear_valoracion(cls, id_usuario, id_contenido, puntuacion_normalizada):
        """
        Crea una nueva valoración.
        
        Args:
            id_usuario (int): ID del usuario
            id_contenido (int): ID del contenido
            puntuacion_normalizada (float): Puntuación normalizada (0-1)
            
        Returns:
            dict: Resultado de la operación
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO VALORACION 
                (id_usuario, id_contenido, puntuacion, fecha)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """, (id_usuario, id_contenido, puntuacion_normalizada))
            
            conexion.commit()
            
            if cursor.rowcount > 0:
                return {"success": True, "message": "Valoración creada correctamente"}
            else:
                return {"success": False, "error": "No se pudo crear la valoración"}
                
        except Exception as e:
            conexion.rollback()
            print(f"Error al crear valoración: {str(e)}")
            return {"success": False, "error": f"Error al crear valoración: {str(e)}"}
        finally:
            cursor.close()
            conexion.close() 