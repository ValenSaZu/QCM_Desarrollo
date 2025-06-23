# Clase que maneja la interfaz de login del sistema, incluyendo formulario de acceso, mensaje de bienvenida y errores de autenticación
class InterfazLogin:

    def mostrar_formulario(self):
        """Muestra el formulario de inicio de sesión del sistema.

        Returns:
            str: HTML completo del formulario de login
        """
        with open('static/html/UIAccesoAlPortal(MK-001).html', 'r', encoding='utf-8') as f:
            return f.read()

    def mostrar_bienvenida(self, datos):
        """Muestra la interfaz de administración de promociones tras un login exitoso.

        Args:
            datos: Información del usuario autenticado (no utilizado actualmente)

        Returns:
            str: HTML de la interfaz de administración de promociones
        """
        with open('static/html/UIAdministrarPromocion(MK-025).html', 'r', encoding='utf-8') as f:
            return f.read()

    def mostrar_error(self, mensaje_error):
        """Genera una página de error personalizada cuando falla el login.

        Args:
            mensaje_error (str): Descripción del error a mostrar al usuario

        Returns:
            str: HTML completo de la página de error con opción para reintentar
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
                    <h2 class="form-title">Error en inicio de sesión</h2>
                </div>
                <p class="error-message">{mensaje_error}</p>
                <a href="/" class="button-full">Volver a intentar</a>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def servir_pagina_login():
        """Sirve la página de login"""
        try:
            with open('static/html/UIAccesoAlPortal(MK-001).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de login: {e}")
            return None