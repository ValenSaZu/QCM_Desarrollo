class InterfazPromociones:
    @staticmethod
    def servir_pagina_promociones():
        """Sirve la página de promociones"""
        try:
            with open('static/html/UIPromociones.html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de promociones: {e}")
            return None
