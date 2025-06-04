# Clase que maneja la interfaz de registro de nuevos clientes, incluyendo formulario de registro, confirmación y manejo de errores
class InterfazRegistro:

    def mostrar_formulario(self):
        """Muestra el formulario de registro para nuevos clientes

        Returns:
            str: HTML completo del formulario de registro
        """
        with open('static/html/UIRegistroCliente(MK-002).html', 'r', encoding='utf-8') as f:
            return f.read()

    def mostrar_bienvenida(self, datos):
        """Muestra mensaje de confirmación tras un registro exitoso con los datos del usuario

        Args:
            datos (dict): Diccionario con información del usuario registrado y mensaje de confirmación
                         Debe contener:
                         - 'mensaje': Mensaje de bienvenida
                         - 'usuario': Diccionario con 'nombre' y 'apellido' del usuario

        Returns:
            str: HTML con la página de bienvenida y datos del usuario registrado
        """
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

    def mostrar_error(self, mensaje_error):
        """Muestra página de error cuando falla el registro

        Args:
            mensaje_error (str): Descripción del error ocurrido durante el registro

        Returns:
            str: HTML con la página de error y opción para reintentar el registro
        """
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