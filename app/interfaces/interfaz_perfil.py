# UI-PERF-001: Clase para manejar la interfaz de perfil del cliente, incluyendo visualización y gestión de datos personales
class InterfazPerfil:

    # FUNC-UI-PERF-001: Sirve la página principal de perfil del cliente
    @staticmethod
    def servir_pagina_perfil():
        try:
            with open('static/html/UIPerfilCliente(MK-006).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de perfil: {e}")
            return None