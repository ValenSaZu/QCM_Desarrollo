# Clase que maneja la interfaz para el carrito de compras, mostrando la interfaz principal y mensajes de error cuando ocurren problemas.
class InterfazCarrito:

    @staticmethod
    def servir_pagina_carrito():
        """Sirve la página del carrito"""
        try:
            with open('static/html/UICarrito(MK-015).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de carrito: {e}")
            return None

    def mostrar_error(self, mensaje):
        """Genera y retorna una página HTML de error con un mensaje personalizado y un botón para volver.

        Args:
            mensaje (str): Mensaje de error que se mostrará al usuario.
        """
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