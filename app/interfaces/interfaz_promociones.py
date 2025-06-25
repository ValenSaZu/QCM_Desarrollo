# UI-PROM-002: Clase para manejar la interfaz de promociones que incluye:
# - Visualización de ofertas y descuentos disponibles
# - Carga segura de plantillas HTML estáticas
# - Manejo de errores en la visualización de promociones
class InterfazPromociones:

    # FUNC-UI-PROM-002: Sirve la página principal de promociones
    # Retorna:
    #   str: HTML completo de la página de promociones | None si hay error
    # Excepciones:
    #   - Captura y registra cualquier excepción durante la lectura
    # Características:
    #   - Utiliza plantilla específica MK-004
    #   - Codificación UTF-8 para soporte de caracteres especiales
    #   - Manejo seguro de recursos con context manager
    #   - Registra errores en consola para diagnóstico
    # Dependencias:
    #   - Requiere archivo en 'static/html/UIPromociones(MK-004).html'
    @staticmethod
    def servir_pagina_promociones():
        try:
            with open('static/html/UIPromociones(MK-004).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de promociones: {e}")
            return None