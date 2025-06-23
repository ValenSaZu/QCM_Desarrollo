# UI-CAT-001: Clase para manejar la interfaz de administración de categorías, incluyendo la visualización y gestión de categorías
class InterfazAdministrarCategorias:

    # FUNC-UI-CAT-001: Sirve el archivo HTML de la página de administración de categorías
    @staticmethod
    def servir_pagina_admin_categorias():
        try:
            with open('static/html/UIAdministrarCategorias(MK-030).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin categorías: {e}")
            return None