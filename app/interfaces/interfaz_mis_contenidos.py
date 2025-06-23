# UI-MCONT-001: Clase para manejar la interfaz de gestión de contenidos del cliente, incluyendo visualización y manejo de errores
class InterfazMisContenidos:

    # FUNC-UI-MCONT-001: Sirve la página principal de "Mis Contenidos" del cliente
    @staticmethod
    def servir_pagina_mis_contenidos():
        try:
            with open('static/html/UIMisContenidos(MK-005).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de mis contenidos: {e}")
            return None

    # FUNC-UI-MCONT-002: Genera página de error personalizada con opciones de navegación
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