# Controlador para gestionar las operaciones relacionadas con categorías
from domain.entities.categoria import Categoria

class ControladorCategoria:
    def obtener_todas_categorias(self):
        """Obtiene todas las categorías existentes y las retorna en formato JSON"""
        try:
            print("ControladorCategoria: Iniciando obtención de todas las categorías")
            categorias = Categoria.obtener_todas_categorias()
            print(f"ControladorCategoria: Categorías obtenidas de la entidad: {len(categorias) if categorias else 0}")
            
            # Asegurarse de que siempre devolvemos una lista
            if not categorias:
                print("ControladorCategoria: No se encontraron categorías, devolviendo lista vacía")
                return []
                
            # Convertir las categorías a diccionarios
            categorias_dict = [{
                "id_categoria": categoria.id_categoria,
                "nombre": categoria.nombre,
                "id_categoria_padre": categoria.id_categoria_padre
            } for categoria in categorias]
            
            print(f"ControladorCategoria: Categorías convertidas a diccionarios: {len(categorias_dict)}")
            print(f"ControladorCategoria: Categorías principales: {[cat for cat in categorias_dict if cat['id_categoria_padre'] is None]}")
            
            return categorias_dict
        except Exception as e:
            print(f"Error en obtener_todas_categorias: {str(e)}")
            raise Exception(f"Error al obtener categorías: {str(e)}")

    def buscar_categorias(self, termino):
        """Busca categorías que coincidan con el término de búsqueda"""
        try:
            print(f"ControladorCategoria: Buscando categorías con término: '{termino}'")
            categorias = Categoria.buscar_categorias(termino)
            print(f"ControladorCategoria: Categorías encontradas en búsqueda: {len(categorias) if categorias else 0}")
            
            # Asegurarse de que siempre devolvemos una lista
            if not categorias:
                print("ControladorCategoria: No se encontraron categorías en la búsqueda")
                return []
                
            # Convertir las categorías a diccionarios
            categorias_dict = [{
                "id_categoria": categoria.id_categoria,
                "nombre": categoria.nombre,
                "id_categoria_padre": categoria.id_categoria_padre
            } for categoria in categorias]
            
            print(f"ControladorCategoria: Categorías convertidas a diccionarios: {len(categorias_dict)}")
            print(f"ControladorCategoria: Categorías encontradas: {[cat['nombre'] for cat in categorias_dict]}")
            
            return categorias_dict
        except Exception as e:
            print(f"Error en buscar_categorias: {str(e)}")
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

    def agregar_categoria(self, categoria_data):
        try:
            nombre = categoria_data.get('nombre')
            descripcion = categoria_data.get('descripcion', '')
            id_categoria_padre = categoria_data.get('id_categoria_padre')

            if not nombre:
                return {"success": False, "error": "El nombre de la categoría es requerido"}

            if id_categoria_padre:
                try:
                    id_categoria_padre = int(id_categoria_padre)
                    if not self.validar_categoria_existe(id_categoria_padre):
                        return {"success": False, "error": "La categoría padre especificada no existe"}
                except (ValueError, TypeError):
                    return {"success": False, "error": "ID de categoría padre no válido"}

            categoria = Categoria.crear_categoria(nombre.strip(), id_categoria_padre)

            return {
                "success": True,
                "message": "Categoría agregada correctamente",
                "categoria": {
                    "id": categoria.id_categoria,
                    "nombre": categoria.nombre
                }
            }
        except Exception as e:
            print(f"Error al agregar categoría: {str(e)}")
            return {"success": False, "error": str(e)}

    def validar_categoria_existe(self, id_categoria):
        try:
            categorias = Categoria.obtener_todas_categorias()
            return any(c.id_categoria == id_categoria for c in categorias)
        except:
            return False

    def obtener_categorias(self):
        try:
            categorias = Categoria.obtener_todas_categorias()
            data = []
            for c in categorias:
                categoria_data = {
                    'id_categoria': c.id_categoria,
                    'nombre': c.nombre or 'Sin nombre',
                    'descripcion': c.descripcion or 'Sin descripción',
                    'id_categoria_padre': c.id_categoria_padre
                }
                data.append(categoria_data)

            return {"success": True, "data": data}
        except Exception as e:
            print(f"Error al obtener categorías: {str(e)}")
            return {"success": False, "error": str(e)}

    def obtener_categoria(self, id_categoria):
        try:
            categorias = Categoria.obtener_todas_categorias()
            categoria = next((c for c in categorias if c.id_categoria == id_categoria), None)
            if categoria:
                return {"success": True, "data": categoria}
            else:
                return {"success": False, "error": "Categoría no encontrada"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def eliminar_categoria(self, id_categoria):
        try:
            Categoria.eliminar_categoria_por_id(id_categoria)
            return {"success": True, "message": "Categoría eliminada correctamente"}
        except Exception as e:
            return {"success": False, "error": str(e)}