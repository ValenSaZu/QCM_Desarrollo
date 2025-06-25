# UI-PROM-002: Clase para manejar la interfaz de promociones, mostrando ofertas y descuentos disponibles
class InterfazPromociones:

    # FUNC-UI-PROM-002: Sirve la página principal de promociones
    @staticmethod
    def servir_pagina_promociones():
        try:
            with open('static/html/UIPromociones(MK-004).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de promociones: {e}")
            return None