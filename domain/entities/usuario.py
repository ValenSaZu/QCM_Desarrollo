from infrastructure.bd.conexion import obtener_conexion

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
            id_usuario = cursor.fetchone()[0]

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
        query = "SELECT * FROM usuario WHERE username = %s;"
        cursor.execute(query, (username,))
        usuario_data = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario_data:
            # Convert tuple to dictionary using column names
            column_names = [desc[0] for desc in cursor.description]
            usuario_dict = dict(zip(column_names, usuario_data))
            return cls(
                id_usuario=usuario_dict['id_usuario'],
                username=usuario_dict['username'],
                contrasena=usuario_dict['contrasena'],
                nombre=usuario_dict['nombre'],
                apellido=usuario_dict['apellido']
            )
        return None

    def verificar_contrasena(self, contrasena):
        return self.contrasena == contrasena