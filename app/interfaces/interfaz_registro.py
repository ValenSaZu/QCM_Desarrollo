# UI-REG-001: Clase para manejar la interfaz de registro de clientes, incluyendo formulario, confirmación y manejo de errores
class InterfazRegistro:

    # FUNC-UI-REG-001: Sirve la página principal de registro de clientes
    @staticmethod
    def servir_pagina_registro():
        try:
            with open('static/html/UIRegistroCliente(MK-002).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de registro: {e}")
            return None

    # FUNC-UI-REG-002: Muestra el formulario completo de registro para nuevos clientes
    def mostrar_formulario(self):
        with open('static/html/UIRegistroCliente(MK-002).html', 'r', encoding='utf-8') as f:
            return f.read()

    # FUNC-UI-REG-003: Genera página de confirmación con datos del usuario tras registro exitoso
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

    # FUNC-UI-REG-004: Genera página de error personalizada para fallos en el registro
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