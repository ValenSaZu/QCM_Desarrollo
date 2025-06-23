# UI-CONT-001: Clase para manejar la interfaz de administración de contenidos, incluyendo gestión y visualización de contenidos
class InterfazAdministrarContenidos:

    # FUNC-UI-CONT-001: Sirve el archivo HTML de la página de administración de contenidos
    @staticmethod
    def servir_pagina_admin_contenidos():
        try:
            with open('static/html/UIAdministrarContenidos(MK-034).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin contenidos: {e}")
            return None