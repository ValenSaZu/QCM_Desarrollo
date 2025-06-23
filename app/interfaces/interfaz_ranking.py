# UI-RANK-001: Clase para manejar la interfaz de rankings de contenidos, incluyendo visualización y manejo de errores
class InterfazRanking:

    # FUNC-UI-RANK-001: Sirve la página principal de rankings de contenidos
    @staticmethod
    def servir_pagina_ranking():
        try:
            with open('static/html/UIRankings(MK-054).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de ranking: {e}")
            return None

    # FUNC-UI-RANK-002: Genera página de error personalizada con opciones de navegación
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
                    <h2 class="form-title">Error en Rankings</h2>
                </div>
                <p class="error-message">{mensaje}</p>
                <a href="/cliente/rankings" class="button-full">Reintentar</a>
                <a href="/cliente/inicio" class="button-full">Volver al inicio</a>
            </div>
        </body>
        </html>
        """