# UI-PROM-001: Clase para manejar la interfaz de administración de promociones, incluyendo gestión de descuentos y ofertas especiales
class InterfazAdministrarPromocion:

    # FUNC-UI-PROM-001: Sirve el archivo HTML de la página de administración de promociones
    @staticmethod
    def servir_pagina_admin_promociones():
        try:
            with open('static/html/UIAdministrarPromocion(MK-025).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin promociones: {e}")
            return None