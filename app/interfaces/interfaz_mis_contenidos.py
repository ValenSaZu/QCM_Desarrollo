# Clase que maneja la interfaz para la sección de "Mis Contenidos" del cliente.
class InterfazMisContenidos:

    @staticmethod
    def servir_pagina_mis_contenidos():
        """Sirve la página de mis contenidos"""
        try:
            with open('static/html/UIMisContenidos(MK-005).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de mis contenidos: {e}")
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
                    <h2 class="form-title">Error en Mis Contenidos</h2>
                </div>
                <p class="error-message">{mensaje}</p>
                <a href="/cliente/mis-contenidos" class="button-full">Reintentar</a>
                <a href="/cliente/inicio" class="button-full">Volver al inicio</a>
            </div>
        </body>
        </html>
        """