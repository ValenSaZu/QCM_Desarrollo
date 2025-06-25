# UI-PERF-001: Clase para manejar la interfaz de perfil del cliente que incluye:
# - Visualización de datos personales del usuario
# - Gestión y actualización de información de perfil
# - Carga segura de plantillas HTML estáticas
# - Manejo de errores en la visualización del perfil
class InterfazPerfil:

    # FUNC-UI-PERF-001: Sirve la página principal de perfil del cliente
    # Retorna:
    #   str: HTML completo de la página de perfil | None si hay error
    # Excepciones:
    #   - Captura y registra cualquier excepción durante la lectura del archivo
    # Características:
    #   - Utiliza plantilla específica MK-006
    #   - Codificación UTF-8 para soporte de caracteres especiales
    #   - Manejo seguro de recursos con context manager
    #   - Registra errores en consola para diagnóstico
    # Dependencias:
    #   - Requiere archivo en 'static/html/UIPerfilCliente(MK-006).html'
    @staticmethod
    def servir_pagina_perfil():
        try:
            with open('static/html/UIPerfilCliente(MK-006).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de perfil: {e}")
            return None