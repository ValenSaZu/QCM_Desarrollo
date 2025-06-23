# UI-INIC-001: Clase para manejar la interfaz de inicio del sistema, incluyendo páginas para clientes, administradores y manejo de errores
class InterfazInicio:

    # FUNC-UI-INIC-001: Carga y muestra la interfaz principal del cliente
    def mostrar_interfaz(self):
        try:
            with open('static/html/UIInicioCliente(MK-012).html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return self.mostrar_error("No se pudo cargar la página de inicio.")

    # FUNC-UI-INIC-002: Genera página de error personalizada con opciones de navegación
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
                    <h2 class="form-title">Error en la página de inicio</h2>
                </div>
                <p class="error-message">{mensaje}</p>
                <a href="/cliente/inicio" class="button-full">Reintentar</a>
                <a href="/" class="button-full">Volver al inicio de sesión</a>
            </div>
        </body>
        </html>
        """

    # FUNC-UI-INIC-003: Sirve la página principal de acceso al portal
    @staticmethod
    def servir_pagina_inicio():
        try:
            with open('static/html/UIAccesoAlPortal(MK-001).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de inicio: {e}")
            return None

    # FUNC-UI-INIC-004: Sirve la página de inicio del administrador
    @staticmethod
    def servir_pagina_admin():
        try:
            with open('static/html/UIInicioAdmin.html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin: {e}")
            return None

    # FUNC-UI-INIC-005: Sirve la página de inicio del cliente
    @staticmethod
    def servir_pagina_cliente():
        try:
            with open('static/html/UIInicioCliente(MK-012).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de cliente: {e}")
            return None