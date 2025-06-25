# UI-PROM-001: Clase para la interfaz de administración de promociones que incluye:
# - Visualización de la interfaz principal de gestión de promociones
# - Manejo de descuentos y ofertas especiales
# - Carga segura de plantillas HTML estáticas
class InterfazAdministrarPromocion:

    # FUNC-UI-PROM-001: Sirve la página de administración de promociones
    # Retorna:
    #   str: Contenido HTML completo | None si hay error
    # Excepciones:
    #   - Captura y registra errores de lectura de archivos
    # Características:
    #   - Usa archivo HTML estático con ruta específica
    #   - Codificación UTF-8 para soporte multilingüe
    #   - Manejo seguro de recursos con context manager
    #   - Registra errores en consola para diagnóstico
    # Dependencias:
    #   - Requiere archivo HTML en ruta 'static/html/UIAdministrarPromocion(MK-025).html's
    @staticmethod
    def servir_pagina_admin_promociones():
        try:
            with open('static/html/UIAdministrarPromocion(MK-025).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin promociones: {e}")
            return None