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
            print("Categoria.obtener_todas_categorias: Ejecutando consulta SQL")
            cursor.execute("SELECT id_categoria, nombre, id_categoria_padre FROM categoria")
            categorias = []
            for row in cursor.fetchall():
                categoria = cls(
                    id_categoria=row[0],
                    nombre=row[1],
                    id_categoria_padre=row[2]
                )
                categorias.append(categoria)
            
            print(f"Categoria.obtener_todas_categorias: Se encontraron {len(categorias)} categorías")
            categorias_principales = [cat.nombre for cat in categorias if cat.id_categoria_padre is None]
            print(f"Categoria.obtener_todas_categorias: Categorías principales: {categorias_principales}")
            
            return categorias
        except Exception as e:
            print(f"Categoria.obtener_todas_categorias: Error - {str(e)}")
            raise Exception(f"Error al obtener categorias: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def buscar_categorias(cls, termino):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            print(f"Categoria.buscar_categorias: Buscando con término '{termino}'")
            
            # Construir la consulta SQL
            query = "SELECT id_categoria, nombre, id_categoria_padre FROM categoria WHERE LOWER(nombre) LIKE LOWER(%s)"
            params = (f"%{termino}%",)
            
            print(f"Categoria.buscar_categorias: Query SQL: {query}")
            print(f"Categoria.buscar_categorias: Parámetros: {params}")
            
            cursor.execute(query, params)
            
            # Verificar todas las categorías para debug
            cursor.execute("SELECT id_categoria, nombre, id_categoria_padre FROM categoria ORDER BY nombre")
            todas_categorias = cursor.fetchall()
            print(f"Categoria.buscar_categorias: Todas las categorías en BD: {[cat[1] for cat in todas_categorias]}")
            
            # Ejecutar la búsqueda real
            cursor.execute(query, params)
            
            categorias = []
            for row in cursor.fetchall():
                categoria = cls(
                    id_categoria=row[0],
                    nombre=row[1],
                    id_categoria_padre=row[2]
                )
                categorias.append(categoria)
            
            print(f"Categoria.buscar_categorias: Se encontraron {len(categorias)} categorías")
            print(f"Categoria.buscar_categorias: Categorías encontradas: {[cat.nombre for cat in categorias]}")
            
            return categorias
        except Exception as e:
            print(f"Categoria.buscar_categorias: Error - {str(e)}")
            raise Exception(f"Error al buscar categorias: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def crear_categoria(cls, nombre, id_categoria_padre=None):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            print(f"Categoria.crear_categoria: Creando categoría '{nombre}' con padre: {id_categoria_padre}")
            
            if id_categoria_padre:
                cursor.execute(
                    "INSERT INTO categoria (nombre, id_categoria_padre) VALUES (%s, %s) RETURNING id_categoria, nombre, id_categoria_padre",
                    (nombre, id_categoria_padre)
                )
            else:
                cursor.execute(
                    "INSERT INTO categoria (nombre, id_categoria_padre) VALUES (%s, NULL) RETURNING id_categoria, nombre, id_categoria_padre",
                    (nombre,)
                )

            row = cursor.fetchone()
            if not row:
                raise Exception("No se pudo crear la categoría")
                
            conexion.commit()
            categoria = cls(
                id_categoria=row[0],
                nombre=row[1],
                id_categoria_padre=row[2]
            )
            print(f"Categoria.crear_categoria: Categoría creada exitosamente - ID: {categoria.id_categoria}, Nombre: {categoria.nombre}, Padre: {categoria.id_categoria_padre}")
            return categoria
        except Exception as e:
            conexion.rollback()
            print(f"Categoria.crear_categoria: Error - {str(e)}")
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