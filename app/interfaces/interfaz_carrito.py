# UI-CARR-001: Clase que maneja la interfaz del carrito de compras que incluye:
# - Visualización de productos en el carrito
# - Generación de páginas de error personalizadas
# - Carga segura de plantillas HTML estáticas
# - Manejo de redireccionamiento en casos de error
class InterfazCarrito:

    # FUNC-UI-CARR-001: Sirve el archivo HTML de la página principal del carrito de compras
    # Retorna:
    #   str: Contenido HTML completo del carrito | None si hay error
    # Excepciones:
    #   - Captura y registra errores de lectura de archivos
    # Características:
    #   - Usa archivo HTML estático con ruta específica
    #   - Codificación UTF-8 para soporte multilingüe
    #   - Manejo seguro de recursos con context manager
    #   - Registra errores en consola para diagnóstico
    # Dependencias:
    #   - Requiere archivo HTML en ruta 'static/html/UICarrito(MK-015).html'
    @staticmethod
    def servir_pagina_carrito():
        try:
            with open('static/html/UICarrito(MK-015).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de carrito: {e}")
            return None

    # FUNC-UI-CARR-002: Genera página de error personalizada para el carrito
    # Parámetros:
    #   mensaje (str): Descripción del error a mostrar al usuario
    # Retorna:
    #   str: Contenido HTML completo de la página de error
    # Características:
    #   - Diseño responsive usando clases CSS existentes
    #   - Incluye opciones de navegación para recuperación
    #   - Muestra mensaje de error claramente identificado
    #   - Mantiene consistencia estilística con el resto de la aplicación
    # Dependencias:
    #   - Requiere el archivo CSS en '/css/style.css'
    #   - Asume estructura de rutas '/cliente/carrito' y '/cliente/inicio'
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
                    <h2 class="form-title">Error en el carrito</h2>
                </div>
                <p class="error-message">{mensaje}</p>
                <a href="/cliente/carrito" class="button-full">Volver al carrito</a>
                <a href="/cliente/inicio" class="button-full">Volver al inicio</a>
            </div>
        </body>
        </html>
        """