from infrastructure.bd.conexion import obtener_conexion

# BD-009: Entidad para gestionar operaciones de categorías
class Categoria:
    def __init__(self, id_categoria, nombre, id_categoria_padre=None):
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.id_categoria_padre = id_categoria_padre

    # ENT-CAT-001: Obtiene todas las categorías del sistema
    @classmethod
    def obtener_todas_categorias(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT id_categoria, nombre, id_categoria_padre FROM categoria")
            return [
                cls(id_categoria=row[0], nombre=row[1], id_categoria_padre=row[2])
                for row in cursor.fetchall()
            ]
        except Exception:
            raise Exception("Error al obtener categorías")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CAT-002: Busca categorías por término de búsqueda
    @classmethod
    def buscar_categorias(cls, termino):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                    SELECT id_categoria, nombre, id_categoria_padre
                    FROM categoria
                    WHERE LOWER(nombre) LIKE LOWER(%s) \
                    """
            cursor.execute(query, (f"%{termino}%",))

            return [
                cls(id_categoria=row[0], nombre=row[1], id_categoria_padre=row[2])
                for row in cursor.fetchall()
            ]
        except Exception:
            raise Exception("Error al buscar categorías")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CAT-003: Crea una nueva categoría
    @classmethod
    def crear_categoria(cls, nombre, id_categoria_padre=None):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                    INSERT INTO categoria (nombre, id_categoria_padre)
                    VALUES (%s, %s) RETURNING id_categoria, nombre, id_categoria_padre \
                    """
            params = (nombre, id_categoria_padre) if id_categoria_padre else (nombre, None)

            cursor.execute(query, params)
            if not (row := cursor.fetchone()):
                raise Exception("No se pudo crear la categoría")

            conexion.commit()
            return cls(*row)
        except Exception:
            conexion.rollback()
            raise Exception("Error al crear categoría")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CAT-004: Actualiza una categoría existente
    @classmethod
    def actualizar_categoria(cls, id_categoria, nombre):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           UPDATE categoria
                           SET nombre = %s
                           WHERE id_categoria = %s RETURNING id_categoria, nombre, id_categoria_padre
                           """, (nombre, id_categoria))

            if not (row := cursor.fetchone()):
                raise Exception("Categoría no encontrada")

            conexion.commit()
            return cls(*row)
        except Exception:
            conexion.rollback()
            raise Exception("Error al actualizar categoría")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_relaciones_arbol(cls, id_categoria_principal):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id_categoria, nombre, id_categoria_padre FROM CATEGORIA")
            categorias = cursor.fetchall()
            cat_map = {row[0]: {"nombre": row[1], "padre": row[2]} for row in categorias}
            relaciones = []
            def recorrer(cat_id):
                for hijo_id, cat in cat_map.items():
                    if cat["padre"] == cat_id:
                        relaciones.append((cat_id, hijo_id, cat_map[cat_id]["nombre"], cat["nombre"]))
                        recorrer(hijo_id)
            recorrer(id_categoria_principal)
            return relaciones
        finally:
            cursor.close()
            conexion.close()