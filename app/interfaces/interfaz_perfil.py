class InterfazPerfil:
    @staticmethod
    def servir_pagina_perfil():
        """Sirve la página de perfil"""
        try:
            with open('static/html/UIPerfilCliente (MK-006).html', 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error leyendo archivo de perfil: {e}")
            return None 