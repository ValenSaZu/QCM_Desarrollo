# Clase que maneja la interfaz para administrar contenidos, permitiendo gestionar y visualizar los contenidos disponibles.
class InterfazAdministrarContenidos:

    def mostrar_interfaz(self):
        """Carga y retorna el contenido del archivo HTML de la interfaz de administración de contenidos.

        Returns:
            str: HTML completo de la interfaz de administración de contenidos.
        """
        with open('static/html/UIAdministrarContenidos(MK-034).html', 'r', encoding='utf-8') as file:
            html = file.read()
        return html