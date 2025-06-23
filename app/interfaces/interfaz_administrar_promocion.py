# Clase que maneja la interfaz para administrar promociones, permitiendo gestionar descuentos y ofertas especiales.
class InterfazAdministrarPromocion:

    @staticmethod
    def servir_pagina_admin_promociones():
        """Sirve la página de administrar promociones"""
        try:
            with open('static/html/UIAdministrarPromocion(MK-025).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de admin promociones: {e}")
            return None