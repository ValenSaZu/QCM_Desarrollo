# Controlador para gestionar las operaciones relacionadas con categorías
from domain.entities.categoria import Categoria

class ControladorCategoria:
    def obtener_todas_categorias(self):
        """Obtiene todas las categorías existentes y las retorna en formato JSON"""
        try:
            categorias = Categoria.obtener_todas_categorias()
            return [{
                "id_categoria": categoria.id_categoria,
                "nombre": categoria.nombre,
                "id_categoria_padre": categoria.id_categoria_padre
            } for categoria in categorias]
        except Exception as e:
            raise Exception(f"Error al obtener categorías: {str(e)}")

    def buscar_categorias(self, termino):
        """Busca categorías que coincidan con el término de búsqueda"""
        try:
            categorias = Categoria.buscar_categorias(termino)
            return [{
                "id_categoria": categoria.id_categoria,
                "nombre": categoria.nombre,
                "id_categoria_padre": categoria.id_categoria_padre
            } for categoria in categorias]
        except Exception as e:
            raise Exception(f"Error al buscar categorías: {str(e)}")

    def crear_categoria(self, nombre, id_categoria_padre=None):
        """Crea una nueva categoría con el nombre y categoría padre especificados"""
        try:
            categoria = Categoria.crear_categoria(nombre, id_categoria_padre)
            return {
                "id_categoria": categoria.id_categoria,
                "nombre": categoria.nombre,
                "id_categoria_padre": categoria.id_categoria_padre
            }
        except Exception as e:
            raise Exception(f"Error al crear categoría: {str(e)}")

    def actualizar_categoria(self, id_categoria, nombre):
        """Actualiza el nombre de una categoría existente"""
        try:
            categoria = Categoria.actualizar_categoria(id_categoria, nombre)
            return {
                "id_categoria": categoria.id_categoria,
                "nombre": categoria.nombre,
                "id_categoria_padre": categoria.id_categoria_padre
            }
        except Exception as e:
            raise Exception(f"Error al actualizar categoría: {str(e)}")