# UI-REG-001: Clase para manejar la interfaz de registro de clientes que incluye:
# - Formulario de registro con validación de datos
# - Página de confirmación post-registro exitoso
# - Manejo de errores en el proceso de registro
# - Carga segura de plantillas HTML estáticas
class InterfazRegistro:

    # FUNC-UI-REG-001: Sirve la página principal de registro de clientes
    # Retorna:
    #   str: HTML completo del formulario de registro | None si hay error
    # Excepciones:
    #   - Captura y registra cualquier excepción durante la lectura
    # Características:
    #   - Utiliza plantilla específica MK-002
    #   - Codificación UTF-8 para soporte multilingüe
    #   - Manejo seguro de recursos con context manager
    #   - Registra errores en consola para diagnóstico
    # Dependencias:
    #   - Requiere archivo en 'static/html/UIRegistroCliente(MK-002).html'
    @staticmethod
    def servir_pagina_registro():
        try:
            with open('static/html/UIRegistroCliente(MK-002).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de registro: {e}")
            return None

    # FUNC-UI-REG-002: Muestra el formulario completo de registro
    # Retorna:
    #   str: HTML completo del formulario de registro
    # Características:
    #   - Utiliza plantilla MK-002 estándar
    #   - Codificación UTF-8 garantizada
    #   - No incluye manejo de errores (asume archivo existe)
    # Dependencias:
    #   - Requiere archivo en 'static/html/UIRegistroCliente(MK-002).html'
    def mostrar_formulario(self):
        with open('static/html/UIRegistroCliente(MK-002).html', 'r', encoding='utf-8') as f:
            return f.read()

    # FUNC-UI-REG-003: Genera página de confirmación post-registro exitoso
    # Parámetros:
    #   datos (dict): Información del usuario registrado con estructura:
    #     {
    #       'mensaje': str,  # Mensaje de bienvenida
    #       'usuario': {
    #         'nombre': str,
    #         'apellido': str
    #       }
    #     }
    # Retorna:
    #   str: HTML completo de la página de bienvenida
    # Características:
    #   - Muestra datos personales del nuevo usuario
    #   - Diseño consistente con el sistema
    #   - Incluye opción para volver al inicio
    # Dependencias:
    #   - Requiere archivo CSS en '/css/style.css'
    #   - Asume ruta '/' válida para redirección
    def mostrar_bienvenida(self, datos):
        return f"""
        <html>
        <head>
            <link rel="stylesheet" href="/css/style.css">
            <title>Bienvenido</title>
        </head>
        <body>
            <div class="form">
                <div class="header">
                    <h2 class="form-title">¡Registro Completo, inicia sesión!</h2>
                </div>
                <p>{datos['mensaje']}</p>
                <p>Nombre: {datos['usuario']['nombre']}</p>
                <p>Apellido: {datos['usuario']['apellido']}</p>
                <a href="/" class="button-full">Volver al inicio</a>
            </div>
        </body>
        </html>
        """

    # FUNC-UI-REG-004: Genera página de error para fallos en el registro
    # Parámetros:
    #   mensaje_error (str): Descripción específica del error ocurrido
    # Retorna:
    #   str: HTML completo de la página de error
    # Características:
    #   - Diseño responsive usando CSS centralizado
    #   - Mensaje de error claramente destacado
    #   - Opción para reintentar el registro
    # Dependencias:
    #   - Requiere archivo CSS en '/css/style.css'
    #   - Asume ruta '/registro' válida para reintento
    def mostrar_error(self, mensaje_error):
        return f"""
        <html>
        <head>
            <link rel="stylesheet" href="/css/style.css">
            <title>Error en registro</title>
        </head>
        <body>
            <div class="form">
                <div class="header">
                    <h2 class="form-title">Error</h2>
                </div>
                <p class="error-message">{mensaje_error}</p>
                <a href="/registro" class="button-full">Intentar nuevamente</a>
            </div>
        </body>
        </html>
        """