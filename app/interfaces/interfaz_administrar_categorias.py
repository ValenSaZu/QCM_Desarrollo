# Clase que maneja la interfaz para administrar categorías, permitiendo visualizar y gestionar las categorías disponibles.
class InterfazAdministrarCategorias:

    @staticmethod
    def servir_pagina_admin_categorias():
        """Sirve la página de administrar categorías"""
        try:
            with open('static/html/UIAdministrarCategorias(MK-030).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin categorías: {e}")
            return None