# UI-CONT-001: Clase para la interfaz de administración de contenidos que incluye:
# - Visualización de la interfaz principal de gestión de contenidos
# - Carga y servicio de páginas HTML estáticas
# - Manejo de errores de carga de archivos
class InterfazAdministrarContenidos:

    # FUNC-UI-CONT-001: Sirve la página principal de administración de contenidos
    # Retorna:
    #   str: Contenido HTML del archivo estático | None si ocurre error
    # Excepciones:
    #   - Captura y registra errores de lectura de archivos
    # Características:
    #   - Utiliza archivo HTML estático ubicado en ruta específica
    #   - Codificación UTF-8 para soporte de caracteres internacionales
    #   - Implementa manejo seguro de recursos con contexto 'with'
    #   - Registra errores en consola para diagnóstico
    # Dependencias:
    #   - Archivo HTML en 'static/html/UIAdministrarContenidos(MK-034).html'
    @staticmethod
    def servir_pagina_admin_contenidos():
        try:
            with open('static/html/UIAdministrarContenidos(MK-034).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin contenidos: {e}")
            return None