# UI-CLI-001: Clase para la interfaz de administración de clientes que incluye:
# - Visualización de la interfaz principal de administración
# - Manejo de errores con mensajes personalizados
# - Generación dinámica de páginas de error
class InterfazAdministrarClientes:

    # FUNC-UI-CLI-001: Sirve la página principal de administración de clientes
    # Retorna:
    #   str: Contenido HTML del archivo estático | None si hay error
    # Excepciones:
    #   - Captura y registra errores de lectura de archivo
    # Características:
    #   - Usa archivo HTML estático en ruta específica
    #   - Encoding UTF-8 para soporte multilingüe
    #   - Manejo seguro de recursos con 'with'
    @staticmethod
    def servir_pagina_admin_clientes():
        try:
            with open('static/html/UIAdministrarCliente(MK-038).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin clientes: {e}")
            return None

    # FUNC-UI-CLI-002: Genera página de error personalizada
    # Parámetros:
    #   mensaje (str): Mensaje de error a mostrar al usuario
    # Retorna:
    #   str: Página HTML completa con:
    #       - Estilos CSS incorporados
    #       - Mensaje de error proporcionado
    #       - Botón de retorno a la página principal
    # Características:
    #   - Diseño consistente con la interfaz principal
    #   - Mensajes claros para el usuario final
    #   - Integración con hoja de estilos CSS
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