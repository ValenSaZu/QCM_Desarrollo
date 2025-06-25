# UI-PERF-001: Clase para manejar la interfaz de perfil del cliente que incluye:
# - Visualización de datos personales del usuario
# - Gestión de información de perfil
# - Manejo de errores en la carga del perfil
# - Generación de páginas de error personalizadas
class InterfazPerfilCliente:

    # FUNC-UI-PERF-001: Carga y muestra la interfaz principal del perfil del cliente
    # Retorna:
    #   str: HTML completo de la página de perfil | Página de error si falla
    # Excepciones:
    #   - Maneja específicamente FileNotFoundError
    # Características:
    #   - Utiliza plantilla específica MK-006
    #   - Codificación UTF-8 garantizada
    #   - Fallback a página de error integrada
    #   - Manejo seguro de recursos con context manager
    # Dependencias:
    #   - Requiere archivo en 'static/html/UIPerfilCliente (MK-006).html'
    def mostrar_interfaz(self):
        try:
            with open('static/html/UIPerfilCliente (MK-006).html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return self.mostrar_error("No se pudo cargar la interfaz del perfil del cliente.")

    # FUNC-UI-PERF-002: Genera página de error personalizada para el perfil
    # Parámetros:
    #   mensaje (str): Descripción del error a mostrar al usuario
    # Retorna:
    #   str: HTML completo de la página de error
    # Características:
    #   - Diseño consistente con el sistema
    #   - Opción única de retorno al perfil
    #   - Integración con CSS centralizado
    #   - Mensaje de error claramente destacado
    # Dependencias:
    #   - Requiere archivo CSS en '/css/style.css'
    #   - Asume ruta válida '/cliente/perfil'
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
                    <h2 class="form-title">Error en el perfil</h2>
                </div>
                <p class="error-message">{mensaje}</p>
                <a href="/cliente/perfil" class="button-full">Volver</a>
            </div>
        </body>
        </html>
        """