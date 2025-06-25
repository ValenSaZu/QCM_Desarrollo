from domain.entities.categoria import Categoria

# G-003: Controlador para gestión completa de categorías que incluye:
# - CRUD básico (Crear, Leer, Actualizar, Eliminar)
# - Búsqueda y filtrado de categorías
# - Validación de jerarquías y relaciones padre-hijo
# - Generación de representación de árbol de categorías
# - Formateo de respuestas para API
class ControladorCategoria:
    # CTRL-CAT-001: Obtiene todas las categorías registradas en el sistema
    # Retorna:
    #   list[dict]: Lista de categorías en formato:
    #       [{
    #           "id_categoria": int,
    #           "nombre": str,
    #           "id_categoria_padre": int|null
    #       }]
    # Excepciones:
    #   Exception: Si falla la consulta a la base de datos
    # Logs:
    #   - Registra el proceso de obtención y conversión de datos
    def obtener_todas_categorias(self):
        try:
            print("ControladorCategoria: Iniciando obtención de todas las categorías")
            categorias = Categoria.obtener_todas_categorias()
            print(f"ControladorCategoria: Categorías obtenidas de la entidad: {len(categorias) if categorias else 0}")

            if not categorias:
                print("ControladorCategoria: No se encontraron categorías, devolviendo lista vacía")
                return []

            categorias_dict = [{
                "id_categoria": categoria.id_categoria,
                "nombre": categoria.nombre,
                "id_categoria_padre": categoria.id_categoria_padre
            } for categoria in categorias]

            print(f"ControladorCategoria: Categorías convertidas a diccionarios: {len(categorias_dict)}")
            return categorias_dict
        except Exception as e:
            print(f"Error en obtener_todas_categorias: {str(e)}")
            raise Exception(f"Error al obtener categorías: {str(e)}")

    # CTRL-CAT-002: Busca categorías cuyo nombre coincida con el término de búsqueda
    # Parámetros:
    #   termino (str): Texto a buscar en los nombres de categoría
    # Retorna:
    #   list[dict]: Lista de categorías que coinciden con el término de búsqueda
    #       (mismo formato que CTRL-CAT-002)
    # Excepciones:
    #   Exception: Si falla la consulta de búsqueda
    # Logs:
    #   - Registra el término de búsqueda y resultados encontrados
    def buscar_categorias(self, termino):
        try:
            print(f"ControladorCategoria: Buscando categorías con término: '{termino}'")
            categorias = Categoria.buscar_categorias(termino)
            print(f"ControladorCategoria: Categorías encontradas en búsqueda: {len(categorias) if categorias else 0}")

            if not categorias:
                print("ControladorCategoria: No se encontraron categorías en la búsqueda")
                return []

            categorias_dict = [{
                "id_categoria": categoria.id_categoria,
                "nombre": categoria.nombre,
                "id_categoria_padre": categoria.id_categoria_padre
            } for categoria in categorias]

            print(f"ControladorCategoria: Categorías convertidas a diccionarios: {len(categorias_dict)}")
            return categorias_dict
        except Exception as e:
            print(f"Error en buscar_categorias: {str(e)}")
            raise Exception(f"Error al buscar categorías: {str(e)}")

    # CTRL-CAT-003: Crea una nueva categoría en el sistema
    # Parámetros:
    #   nombre (str): Nombre de la nueva categoría
    #   id_categoria_padre (int|None): ID de la categoría padre (opcional)
    # Retorna:
    #   dict: Detalle de la categoría creada en formato:
    #       {
    #           "id_categoria": int,
    #           "nombre": str,
    #           "id_categoria_padre": int|null
    #       }
    # Excepciones:
    #   Exception: Si falla la creación en la base de datos
    def crear_categoria(self, nombre, id_categoria_padre=None):
        try:
            categoria = Categoria.crear_categoria(nombre, id_categoria_padre)
            return {
                "id_categoria": categoria.id_categoria,
                "nombre": categoria.nombre,
                "id_categoria_padre": categoria.id_categoria_padre
            }
        except Exception as e:
            raise Exception(f"Error al crear categoría: {str(e)}")

    # CTRL-CAT-004: Actualiza el nombre de una categoría existente
    # Parámetros:
    #   id_categoria (int): ID de la categoría a actualizar
    #   nombre (str): Nuevo nombre para la categoría
    # Retorna:
    #   dict: Detalle actualizado de la categoría (mismo formato que crear_categoria)
    # Excepciones:
    #   Exception: Si falla la actualización en la base de datos
    def actualizar_categoria(self, id_categoria, nombre):
        try:
            categoria = Categoria.actualizar_categoria(id_categoria, nombre)
            return {
                "id_categoria": categoria.id_categoria,
                "nombre": categoria.nombre,
                "id_categoria_padre": categoria.id_categoria_padre
            }
        except Exception as e:
            raise Exception(f"Error al actualizar categoría: {str(e)}")

    # CTRL-CAT-005: Agrega una categoría con validación completa de datos
    # Parámetros:
    #   categoria_data (dict): Datos de la categoría con estructura:
    #       {
    #           'nombre': str (requerido),
    #           'descripcion': str (opcional),
    #           'id_categoria_padre': int (opcional)
    #       }
    # Retorna:
    #   dict: Resultado de la operación con estructura:
    #       {
    #           "success": bool,
    #           "message": str,
    #           "categoria": dict (detalle de categoría creada) | null,
    #           "error": str (solo si success=False)
    #       }
    # Validaciones:
    #   - Nombre requerido
    #   - Categoría padre debe existir si se especifica
    #   - ID categoría padre debe ser numérico válido
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

    # CTRL-CAT-006: Valida si una categoría existe en el sistema
    # Parámetros:
    #   id_categoria (int): ID de la categoría a validar
    # Retorna:
    #   bool: True si la categoría existe, False si no existe o hay error
    def validar_categoria_existe(self, id_categoria):
        try:
            categorias = Categoria.obtener_todas_categorias()
            return any(c.id_categoria == id_categoria for c in categorias)
        except:
            return False

    # CTRL-CAT-007: Obtiene todas las categorías con formato estandarizado para API
    # Retorna:
    #   dict: Estructura estandarizada para respuesta API:
    #       {
    #           "success": bool,
    #           "data": list[dict] (categorías con campos completos),
    #           "error": str (solo si success=False)
    #       }
    # Campos por categoría:
    #   - id_categoria: int
    #   - nombre: str (default 'Sin nombre')
    #   - descripcion: str (default 'Sin descripción')
    #   - id_categoria_padre: int|null
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

    # CTRL-CAT-008: Obtiene una categoría específica por su ID
    # Parámetros:
    #   id_categoria (int): ID de la categoría a buscar
    # Retorna:
    #   dict: Resultado con estructura:
    #       {
    #           "success": bool,
    #           "data": dict (detalle categoría) | null,
    #           "error": str (solo si success=False)
    #       }
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

    # CTRL-CAT-009: Elimina una categoría existente con validación previa
    # Parámetros:
    #   id_categoria (int): ID de la categoría a eliminar
    # Retorna:
    #   dict: Resultado de la operación:
    #       {
    #           "success": bool,
    #           "message": str,
    #           "error": str (solo si success=False)
    #       }
    # Notas:
    #   - No valida dependencias o referencias a la categoría
    def eliminar_categoria(self, id_categoria):
        try:
            Categoria.eliminar_categoria_por_id(id_categoria)
            return {"success": True, "message": "Categoría eliminada correctamente"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # CTRL-CAT-010: Genera representación en formato Mermaid.js del árbol de categorías
    # Parámetros:
    #   id_categoria_principal (int): ID de la categoría raíz del árbol
    # Retorna:
    #   dict: Estructura con relaciones para gráfico:
    #       {
    #           "success": bool,
    #           "data": list (relaciones padre-hijo),
    #           "error": str (solo si success=False)
    #       }
    def obtener_arbol_mermaid(self, id_categoria_principal):
        relaciones = Categoria.obtener_relaciones_arbol(id_categoria_principal)
        return {"success": True, "data": relaciones}