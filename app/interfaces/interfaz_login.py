# UI-LOGIN-001: Clase para manejar la interfaz de autenticación del sistema que incluye:
# - Formulario de inicio de sesión con validación
# - Pantalla de bienvenida post-autenticación exitosa
# - Manejo de errores de credenciales
# - Carga segura de plantillas HTML estáticas
class InterfazLogin:

    # FUNC-UI-LOGIN-001: Muestra el formulario principal de inicio de sesión
    # Retorna:
    #   str: HTML completo del formulario de login
    # Características:
    #   - Utiliza plantilla MK-001 estándar
    #   - Codificación UTF-8 garantizada
    #   - No incluye manejo de errores (asume archivo existe)
    # Dependencias:
    #   - Requiere archivo en 'static/html/UIAccesoAlPortal(MK-001).html'
    def mostrar_formulario(self):
        with open('static/html/UIAccesoAlPortal(MK-001).html', 'r', encoding='utf-8') as f:
            return f.read()

    # FUNC-UI-LOGIN-002: Muestra la pantalla de bienvenida post-autenticación exitosa
    # Parámetros:
    #   datos (dict): Información del usuario para personalización (no implementado)
    # Retorna:
    #   str: HTML de la pantalla de bienvenida/promociones
    # Características:
    #   - Utiliza plantilla de promociones (MK-025)
    #   - Diseño consistente con el sistema
    # Dependencias:
    #   - Requiere archivo en 'static/html/UIAdministrarPromocion(MK-025).html'
    def mostrar_bienvenida(self, datos):
        with open('static/html/UIAdministrarPromocion(MK-025).html', 'r', encoding='utf-8') as f:
            return f.read()

    # FUNC-UI-LOGIN-003: Genera página de error personalizada para fallos de autenticación
    # Parámetros:
    #   mensaje_error (str): Descripción específica del error de autenticación
    # Retorna:
    #   str: HTML completo de la página de error
    # Características:
    #   - Diseño responsive usando CSS centralizado
    #   - Mensaje de error claramente destacado
    #   - Opción para reintentar el login
    # Dependencias:
    #   - Requiere '/css/style.css' para estilos
    #   - Asume ruta '/' válida para redirección
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
    # Retorna:
    #   str: HTML del formulario de login | None si hay error
    # Excepciones:
    #   - Captura y registra cualquier excepción durante la lectura
    # Características:
    #   - Manejo seguro de recursos con try-except
    #   - Logging de errores en consola
    #   - Reutiliza plantilla MK-001
    # Dependencias:
    #   - Requiere archivo en 'static/html/UIAccesoAlPortal(MK-001).html'
    @staticmethod
    def servir_pagina_login():
        try:
            with open('static/html/UIAccesoAlPortal(MK-001).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de login: {e}")
            return None