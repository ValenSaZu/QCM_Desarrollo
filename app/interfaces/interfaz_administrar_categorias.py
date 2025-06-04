# Clase que maneja la interfaz para administrar categorías, permitiendo visualizar y gestionar las categorías disponibles.
class InterfazAdministrarCategorias:

    def mostrar_interfaz(self):
        """Carga y retorna el contenido del archivo HTML de la interfaz de administración de categorías."""
        with open('static/html/UIAdministrarCategorias(MK-030).html', 'r', encoding='utf-8') as file:
            html = file.read()
        return html