# Clase que maneja la interfaz para administrar contenidos, permitiendo gestionar y visualizar los contenidos disponibles.
class InterfazAdministrarContenidos:

    @staticmethod
    def servir_pagina_admin_contenidos():
        """Sirve la página de administrar contenidos"""
        try:
            with open('static/html/UIAdministrarContenidos(MK-034).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin contenidos: {e}")
            return None