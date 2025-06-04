# Clase que maneja la interfaz para administrar clientes, mostrando la interfaz principal y mensajes de error cuando ocurren problemas.
class InterfazClientes:

    def mostrar_interfaz(self):
        """Carga y retorna el contenido del archivo HTML de la interfaz de administración de clientes."""
        with open('static/html/UIAdministrarCliente(MK-038).html', 'r', encoding='utf-8') as f:
            return f.read()

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