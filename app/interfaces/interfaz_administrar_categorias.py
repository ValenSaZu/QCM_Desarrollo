# UI-CAT-001: Clase para la interfaz de administración de categorías que incluye:
# - Servicio de páginas HTML estáticas
# - Manejo de errores de carga de archivos
# - Soporte para internacionalización (UTF-8)
class InterfazAdministrarCategorias:

    # FUNC-UI-CAT-001: Sirve la página HTML de administración de categorías
    # Retorna:
    #   str: Contenido del archivo HTML como string | None si hay error
    # Excepciones:
    #   - Captura y registra errores de lectura de archivo
    # Características:
    #   - Encoding UTF-8 para soporte de caracteres especiales
    #   - Ruta relativa al archivo HTML estático
    #   - Manejo seguro de recursos (with statement)
    @staticmethod
    def servir_pagina_admin_categorias():
        try:
            with open('static/html/UIAdministrarCategorias(MK-030).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin categorías: {e}")
            return None