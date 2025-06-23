# Clase que maneja la interfaz de inicio del cliente, mostrando la página principal y mensajes de error cuando ocurren problemas.
class InterfazInicio:

    def mostrar_interfaz(self):
        """Carga y retorna el contenido del archivo HTML de la interfaz de inicio del cliente."""
        try:
            with open('static/html/UIInicioCliente(MK-012).html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return self.mostrar_error("No se pudo cargar la página de inicio.")

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
                    <h2 class="form-title">Error en la página de inicio</h2>
                </div>
                <p class="error-message">{mensaje}</p>
                <a href="/cliente/inicio" class="button-full">Reintentar</a>
                <a href="/" class="button-full">Volver al inicio de sesión</a>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def servir_pagina_inicio():
        """Sirve la página de inicio"""
        try:
            with open('static/html/UIAccesoAlPortal(MK-001).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de inicio: {e}")
            return None

    @staticmethod
    def servir_pagina_admin():
        """Sirve la página de inicio del administrador"""
        try:
            with open('static/html/UIInicioAdmin.html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin: {e}")
            return None

    @staticmethod
    def servir_pagina_cliente():
        """Sirve la página de inicio del cliente"""
        try:
            with open('static/html/UIInicioCliente(MK-012).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de cliente: {e}")
            return None