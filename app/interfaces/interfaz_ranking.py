# UI-RANK-001: Clase para manejar la interfaz de rankings de contenidos que incluye:
# - Visualización de contenidos más populares y valorados
# - Manejo de errores en la carga de rankings
# - Generación de páginas de error personalizadas
# - Carga segura de plantillas HTML estáticas
class InterfazRanking:

    # FUNC-UI-RANK-001: Sirve la página principal de rankings de contenidos
    # Retorna:
    #   str: HTML completo de la página de rankings | None si hay error
    # Excepciones:
    #   - Captura y registra cualquier excepción durante la lectura
    # Características:
    #   - Utiliza plantilla específica MK-054
    #   - Codificación UTF-8 para soporte multilingüe
    #   - Manejo seguro de recursos con context manager
    #   - Registra errores en consola para diagnóstico
    # Dependencias:
    #   - Requiere archivo en 'static/html/UIRankings(MK-054).html'
    @staticmethod
    def servir_pagina_ranking():
        try:
            with open('static/html/UIRankings(MK-054).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de ranking: {e}")
            return None

    # FUNC-UI-RANK-002: Genera página de error personalizada para rankings
    # Parámetros:
    #   mensaje (str): Descripción del error a mostrar al usuario
    # Retorna:
    #   str: HTML completo de la página de error
    # Características:
    #   - Diseño responsive usando CSS centralizado
    #   - Proporciona opciones de recuperación contextuales
    #   - Muestra mensaje de error claramente destacado
    #   - Mantiene consistencia estilística con el sistema
    # Dependencias:
    #   - Requiere archivo CSS en '/css/style.css'
    #   - Asume rutas válidas '/cliente/rankings' y '/cliente/inicio'
    def mostrar_error(self, mensaje):
        return f"""
        <html>
        <head>
            <link rel="stylesheet" href="/css/style.css">
            <title>Error</title>
        </head>
        <body>
            <div class="form">
                <div class="header">
                    <h2 class="form-title">Error en Rankings</h2>
                </div>
                <p class="error-message">{mensaje}</p>
                <a href="/cliente/rankings" class="button-full">Reintentar</a>
                <a href="/cliente/inicio" class="button-full">Volver al inicio</a>
            </div>
        </body>
        </html>
        """