# Clase que maneja la interfaz para administrar clientes, mostrando la interfaz principal y mensajes de error cuando ocurren problemas.
class InterfazAdministrarClientes:

    @staticmethod
    def servir_pagina_admin_clientes():
        """Sirve la página de administrar clientes"""
        try:
            with open('static/html/UIAdministrarCliente(MK-038).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin clientes: {e}")
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
                    <h2 class="form-title">Error en administración</h2>
                </div>
                <p class="error-message">{mensaje}</p>
                <a href="/admin/clientes" class="button-full">Volver</a>
            </div>
        </body>
        </html>
        """