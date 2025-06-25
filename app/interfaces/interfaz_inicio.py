# UI-INIC-001: Clase para manejar la interfaz de inicio del sistema que incluye:
# - Páginas de inicio para clientes y administradores
# - Manejo centralizado de errores de interfaz
# - Carga segura de plantillas HTML estáticas
# - Redireccionamiento y recuperación ante fallos
class InterfazInicio:

    # FUNC-UI-INIC-001: Carga y muestra la interfaz principal del cliente
    # Retorna:
    #   str: Contenido HTML del inicio cliente | Página de error si falla
    # Excepciones:
    #   - Maneja específicamente FileNotFoundError
    # Características:
    #   - Fallback a página de error integrada
    #   - Codificación UTF-8 garantizada
    #   - Ruta específica del template MK-012
    # Dependencias:
    #   - Archivo en 'static/html/UIInicioCliente(MK-012).html'
    def mostrar_interfaz(self):
        try:
            with open('static/html/UIInicioCliente(MK-012).html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return self.mostrar_error("No se pudo cargar la página de inicio.")

    # FUNC-UI-INIC-002: Genera página de error personalizada con opciones de navegación
    # Parámetros:
    #   mensaje (str): Descripción del error para mostrar al usuario
    # Retorna:
    #   str: HTML completo de la página de error
    # Características:
    #   - Diseño consistente con el sistema
    #   - Opciones de recuperación contextuales
    #   - Estilos CSS centralizados
    # Dependencias:
    #   - Requiere '/css/style.css'
    #   - Asume rutas '/cliente/inicio' y '/' válidas
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
    # Retorna:
    #   str: HTML del portal de acceso | None si hay error
    # Excepciones:
    #   - Captura y registra cualquier excepción
    # Características:
    #   - Template MK-001 específico
    #   - Manejo seguro de archivos
    #   - Logging de errores en consola
    # Dependencias:
    #   - Archivo en 'static/html/UIAccesoAlPortal(MK-001).html'
    @staticmethod
    def servir_pagina_inicio():
        try:
            with open('static/html/UIAccesoAlPortal(MK-001).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de inicio: {e}")
            return None

    # FUNC-UI-INIC-004: Sirve la página de inicio del administrador
    # Retorna:
    #   str: HTML del dashboard admin | None si hay error
    # Excepciones:
    #   - Captura y registra cualquier excepción
    # Características:
    #   - Versión específica para administradores
    #   - Mismo manejo seguro que otras páginas
    # Dependencias:
    #   - Archivo en 'static/html/UIInicioAdmin.html'
    @staticmethod
    def servir_pagina_admin():
        try:
            with open('static/html/UIInicioAdmin.html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin: {e}")
            return None

    # FUNC-UI-INIC-005: Sirve la página de inicio del cliente
    # Retorna:
    #   str: HTML del dashboard cliente | None si hay error
    # Excepciones:
    #   - Captura y registra cualquier excepción
    # Características:
    #   - Reutiliza template MK-012
    #   - Mecanismo consistente de manejo de errores
    # Dependencias:
    #   - Archivo en 'static/html/UIInicioCliente(MK-012).html'
    @staticmethod
    def servir_pagina_cliente():
        try:
            with open('static/html/UIInicioCliente(MK-012).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de cliente: {e}")
            return None