# UI-PERF-001: Clase para manejar la interfaz de perfil del cliente, incluyendo visualización de datos y manejo de errores
class InterfazPerfilCliente:

    # FUNC-UI-PERF-001: Carga y muestra la interfaz principal del perfil del cliente
    def mostrar_interfaz(self):
        try:
            with open('static/html/UIPerfilCliente (MK-006).html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return self.mostrar_error("No se pudo cargar la interfaz del perfil del cliente.")

    # FUNC-UI-PERF-002: Genera página de error personalizada con opción para volver al perfil
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