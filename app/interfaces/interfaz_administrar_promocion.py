# Clase que maneja la interfaz para administrar promociones, permitiendo gestionar descuentos y ofertas especiales.
class InterfazAdministrarPromocion:

    def mostrar_interfaz(self):
        """Carga y retorna el contenido HTML de la interfaz de administración de promociones.

        Returns:
            str: Contenido completo del archivo HTML de la interfaz.
        """
        with open('static/html/UIAdministrarPromocion(MK-025).html', 'r', encoding='utf-8') as f:
            return f.read()