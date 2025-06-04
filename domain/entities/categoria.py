from infrastructure.bd.conexion import obtener_conexion

class Categoria:
    def __init__(self, id_categoria, nombre, id_categoria_padre=None):
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.id_categoria_padre = id_categoria_padre

    @classmethod
    def obtener_todas_categorias(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT id_categoria, nombre, id_categoria_padre FROM categoria")
            categorias = []
            for row in cursor.fetchall():
                categoria = cls(
                    id_categoria=row[0],
                    nombre=row[1],
                    id_categoria_padre=row[2]
                )
                categorias.append(categoria)
            return categorias
        except Exception as e:
            raise Exception(f"Error al obtener categorias: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def buscar_categorias(cls, termino):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "SELECT id_categoria, nombre, id_categoria_padre FROM categoria WHERE nombre LIKE %s",
                (f"%{termino}%",)
            )
            categorias = []
            for row in cursor.fetchall():
                categoria = cls(
                    id_categoria=row[0],
                    nombre=row[1],
                    id_categoria_padre=row[2]
                )
                categorias.append(categoria)
            return categorias
        except Exception as e:
            raise Exception(f"Error al buscar categorias: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def crear_categoria(cls, nombre, id_categoria_padre=None):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            if id_categoria_padre:
                cursor.execute(
                    "INSERT INTO categoria (nombre, id_categoria_padre) VALUES (%s, %s) RETURNING id_categoria, nombre, id_categoria_padre",
                    (nombre, id_categoria_padre)
                )
            else:
                cursor.execute(
                    "INSERT INTO categoria (nombre) VALUES (%s) RETURNING id_categoria, nombre, id_categoria_padre",
                    (nombre,)
                )

            row = cursor.fetchone()
            conexion.commit()
            return cls(
                id_categoria=row[0],
                nombre=row[1],
                id_categoria_padre=row[2]
            )
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al crear categoría: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def actualizar_categoria(cls, id_categoria, nombre):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "UPDATE categoria SET nombre = %s WHERE id_categoria = %s RETURNING id_categoria, nombre, id_categoria_padre",
                (nombre, id_categoria)
            )

            row = cursor.fetchone()
            if not row:
                raise Exception("Categoría no encontrada")

            conexion.commit()
            return cls(
                id_categoria=row[0],
                nombre=row[1],
                id_categoria_padre=row[2]
            )
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al actualizar categoría: {str(e)}")
        finally:
            cursor.close()
            conexion.close()