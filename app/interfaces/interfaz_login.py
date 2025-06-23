# UI-LOGIN-001: Clase para manejar la interfaz de autenticación del sistema, incluyendo formulario de acceso, bienvenida y manejo de errores
class InterfazLogin:

    # FUNC-UI-LOGIN-001: Muestra el formulario principal de inicio de sesión
    def mostrar_formulario(self):
        with open('static/html/UIAccesoAlPortal(MK-001).html', 'r', encoding='utf-8') as f:
            return f.read()

    # FUNC-UI-LOGIN-002: Muestra la pantalla de bienvenida post-autenticación exitosa
    def mostrar_bienvenida(self, datos):
        with open('static/html/UIAdministrarPromocion(MK-025).html', 'r', encoding='utf-8') as f:
            return f.read()

    # FUNC-UI-LOGIN-003: Genera página de error personalizada para fallos de autenticación
    def mostrar_error(self, mensaje_error):
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

    # FUNC-UI-LOGIN-004: Sirve la página estática de login del sistema
    @staticmethod
    def servir_pagina_login():
        try:
            with open('static/html/UIAccesoAlPortal(MK-001).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de login: {e}")
            return None