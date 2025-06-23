# UI-CARR-001: Clase que maneja la interfaz del carrito de compras, incluyendo visualización de productos y manejo de errores
class InterfazCarrito:

    # FUNC-UI-CARR-001: Sirve el archivo HTML de la página principal del carrito de compras
    @staticmethod
    def servir_pagina_carrito():
        try:
            with open('static/html/UICarrito(MK-015).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de carrito: {e}")
            return None

    # FUNC-UI-CARR-002: Genera página de error personalizada con opciones para volver al carrito o al inicio
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