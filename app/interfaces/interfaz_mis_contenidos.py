# UI-MCONT-001: Clase para manejar la interfaz de gestión de contenidos del cliente que incluye:
# - Visualización de contenidos digitales del usuario
# - Manejo de errores en la carga de contenidos
# - Generación de páginas de error personalizadas
# - Carga segura de plantillas HTML estáticas
class InterfazMisContenidos:

    # FUNC-UI-MCONT-001: Sirve la página principal de "Mis Contenidos" del cliente
    # Retorna:
    #   str: HTML completo de la página de contenidos | None si hay error
    # Excepciones:
    #   - Captura y registra cualquier excepción durante la lectura del archivo
    # Características:
    #   - Utiliza plantilla específica MK-005
    #   - Codificación UTF-8 garantizada
    #   - Manejo seguro de recursos con context manager
    #   - Registra errores en consola para diagnóstico
    # Dependencias:
    #   - Requiere archivo en 'static/html/UIMisContenidos(MK-005).html'
    @staticmethod
    def servir_pagina_mis_contenidos():
        try:
            with open('static/html/UIMisContenidos(MK-005).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de mis contenidos: {e}")
            return None

    # FUNC-UI-MCONT-002: Genera página de error personalizada para la sección de contenidos
    # Parámetros:
    #   mensaje (str): Descripción del error a mostrar al usuario
    # Retorna:
    #   str: HTML completo de la página de error
    # Características:
    #   - Diseño consistente con el sistema
    #   - Proporciona opciones de recuperación contextuales
    #   - Muestra mensaje de error claramente destacado
    #   - Integración con CSS centralizado
    # Dependencias:
    #   - Requiere archivo CSS en '/css/style.css'
    #   - Asume rutas válidas '/cliente/mis-contenidos' y '/cliente/inicio'
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
                    <h2 class="form-title">Error en Mis Contenidos</h2>
                </div>
                <p class="error-message">{mensaje}</p>
                <a href="/cliente/mis-contenidos" class="button-full">Reintentar</a>
                <a href="/cliente/inicio" class="button-full">Volver al inicio</a>
            </div>
        </body>
        </html>
        """