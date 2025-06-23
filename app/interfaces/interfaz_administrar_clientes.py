# UI-CLI-001: Clase que maneja la interfaz para administrar clientes, mostrando la interfaz principal y mensajes de error
class InterfazAdministrarClientes:

    # FUNC-UI-CLI-001: Sirve el archivo HTML de la página de administración de clientes
    @staticmethod
    def servir_pagina_admin_clientes():
        try:
            with open('static/html/UIAdministrarCliente(MK-038).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin clientes: {e}")
            return None

    # FUNC-UI-CLI-002: Genera y retorna una página HTML de error con mensaje personalizado
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
                    <h2 class="form-title">Error en administración</h2>
                </div>
                <p class="error-message">{mensaje}</p>
                <a href="/admin/clientes" class="button-full">Volver</a>
            </div>
        </body>
        </html>
        """