# HTTP-001: Manejador principal de peticiones HTTP para la aplicación
import json
import os
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote_plus, urlparse

from infrastructure.utils.router import routes_get, routes_post, routes_put, routes_delete, sessions
from infrastructure.utils.helpers import responder_html, responder_json
from infrastructure.utils.router import route_get, route_post, route_put, route_delete, sessions, obtener_usuario_actual

from app.controllers.controlador_usuarios import ControladorUsuarios
from app.controllers.controlador_clientes import ControladorClientes
from app.controllers.controlador_contenido import ControladorContenido
from app.controllers.controlador_categoria import ControladorCategoria
from app.controllers.controlador_promocion import ControladorPromocion
from app.controllers.controlador_ranking import ControladorRanking
from app.controllers.controlador_carrito import ControladorCarrito
from app.controllers.controlador_contenidos_adquiridos import ControladorContenidosAdquiridos
from app.controllers.controlador_perfil import ControladorPerfil

from app.interfaces.interfaz_login import InterfazLogin
from app.interfaces.interfaz_registro import InterfazRegistro
from app.interfaces.interfaz_administrar_clientes import InterfazAdministrarClientes
from app.interfaces.interfaz_administrar_contenidos import InterfazAdministrarContenidos
from app.interfaces.interfaz_administrar_promocion import InterfazAdministrarPromocion
from app.interfaces.interfaz_administrar_categorias import InterfazAdministrarCategorias
from app.interfaces.interfaz_perfil_cliente import InterfazPerfilCliente
from app.interfaces.interfaz_carrito import InterfazCarrito
from app.interfaces.interfaz_inicio import InterfazInicio
from app.interfaces.interfaz_mis_contenidos import InterfazMisContenidos
from app.interfaces.interfaz_ranking import InterfazRanking
from app.interfaces.interfaz_promociones import InterfazPromociones

# Diccionario para almacenar sesiones activas
sesiones_activas = {}

# Inicialización de controladores
controladorUsuarios = ControladorUsuarios()
controladorClientes = ControladorClientes()
controladorContenido = ControladorContenido()
controladorCategoria = ControladorCategoria()
controladorPromocion = ControladorPromocion()
controladorCarrito = ControladorCarrito()
controladorRanking = ControladorRanking()
controladorContenidosAdquiridos = ControladorContenidosAdquiridos()
controladorPerfil = ControladorPerfil()

# Inicialización de interfaces
interfazLogin = InterfazLogin()
interfazRegistro = InterfazRegistro()
interfazClientes = InterfazAdministrarClientes()
interfazContenidos = InterfazAdministrarContenidos()
interfazPromocion = InterfazAdministrarPromocion()
interfazCategorias = InterfazAdministrarCategorias()
interfazPerfilCliente = InterfazPerfilCliente()
interfazCarrito = InterfazCarrito()
interfazInicioCliente = InterfazInicio()
interfazMisContenidos = InterfazMisContenidos()
interfazRanking = InterfazRanking()
interfazPromociones = InterfazPromociones()


# HTTP-002: Clase principal para manejar todas las peticiones HTTP
class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.controlador_usuarios = controladorUsuarios
        self.controlador_clientes = controladorClientes
        self.controlador_perfil = controladorPerfil
        self.controlador_carrito = controladorCarrito
        super().__init__(*args, **kwargs)

    # HTTP-003: Envía una respuesta JSON al cliente
    def send_json_response(self, data, status_code=200):
        origin = self.headers.get('Origin', '*')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Vary', 'Origin')
        if status_code == 200 and isinstance(data, dict):
            data['success'] = data.get('success', True)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    # HTTP-004: Sirve la página de inicio
    def servir_pagina_inicio(self):
        return InterfazInicio.servir_pagina_inicio()

    # HTTP-005: Sirve la página de login
    def servir_pagina_login(self):
        return InterfazLogin.servir_pagina_login()

    # HTTP-006: Sirve la página de registro
    def servir_pagina_registro(self):
        return InterfazRegistro.servir_pagina_registro()

    # HTTP-007: Sirve la página de administrador
    def servir_pagina_admin(self):
        return InterfazInicio.servir_pagina_admin()

    # HTTP-008: Sirve la página de cliente
    def servir_pagina_cliente(self):
        return InterfazInicio.servir_pagina_cliente()

    # HTTP-009: Sirve la página del carrito
    def servir_pagina_carrito(self):
        return InterfazCarrito.servir_pagina_carrito()

    # HTTP-010: Sirve la página de perfil del cliente
    def servir_pagina_perfil(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                self.redirect_to('/login')
                return None

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                self.redirect_to('/login')
                return None

            if session_data.get('tipo') != 'cliente':
                self.redirect_to('/login')
                return None

            return InterfazPerfilCliente().mostrar_interfaz()

        except Exception:
            self.redirect_to('/login')
            return None

    # HTTP-011: Sirve la página de mis contenidos
    def servir_pagina_mis_contenidos(self):
        return InterfazMisContenidos.servir_pagina_mis_contenidos()

    # HTTP-012: Sirve la página de ofertas (promociones para cliente)
    def servir_pagina_ofertas(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                self.redirect_to('/login')
                return None

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                self.redirect_to('/login')
                return None

            return InterfazPromociones.servir_pagina_promociones()

        except Exception:
            self.redirect_to('/login')
            return None

    # HTTP-013: Sirve la página de ranking
    def servir_pagina_ranking(self):
        return InterfazRanking.servir_pagina_ranking()

    # HTTP-014: Sirve la página de administración de categorías
    def servir_pagina_administrar_categorias(self):
        return InterfazAdministrarCategorias.servir_pagina_admin_categorias()

    # HTTP-015: Sirve la página de administración de clientes
    def servir_pagina_administrar_clientes(self):
        return InterfazAdministrarClientes.servir_pagina_admin_clientes()

    # HTTP-016: Sirve la página de administración de contenidos
    def servir_pagina_administrar_contenidos(self):
        return InterfazAdministrarContenidos.servir_pagina_admin_contenidos()

    # HTTP-017: Sirve la página de administración de promociones
    def servir_pagina_administrar_promociones(self):
        return InterfazAdministrarPromocion.servir_pagina_admin_promociones()

    # HTTP-018: Maneja la obtención de datos de sesión
    def obtener_sesion_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)
            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)
            if not session_data:
                return self.send_json_response({"error": "No autenticado"}, 401)
            return self.send_json_response({
                "username": session_data.get('username', ''),
                "nombre": session_data.get('nombre', ''),
                "es_admin": session_data.get('es_admin', False)
            })
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-019: Maneja la API de contenidos
    def api_contenidos_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)
            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)
            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)
            contenidos = controladorContenido.obtener_contenidos()
            return self.send_json_response(contenidos)
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-020: Maneja la API de inicio
    def api_inicio_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)
            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)
            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)
            contenidos = controladorContenido.obtener_contenidos()
            return self.send_json_response(contenidos)
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-021: Maneja la API de categorías de contenido
    def api_categorias_contenido_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)
            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)
            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)
            categorias = controladorCategoria.obtener_todas_categorias()
            return self.send_json_response(categorias)
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-022: Maneja la API de búsqueda de categorías
    def api_categorias_buscar_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            termino = self.headers.get('Search-Term', '')

            if not termino:
                categorias = controladorCategoria.obtener_todas_categorias()
            else:
                categorias = controladorCategoria.buscar_categorias(termino)

            return self.send_json_response(categorias)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-023: Envía headers CORS
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    # HTTP-024: Envía una respuesta de error
    def send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_response = json.dumps({
            'success': False,
            'message': message
        }, ensure_ascii=False)
        self.wfile.write(error_response.encode('utf-8'))

    # HTTP-025: Maneja solicitudes GET
    def do_GET(self):
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path

            import re
            promo_match = re.match(r'/api/promociones/(\d+)', path)
            if promo_match:
                promo_id = int(promo_match.group(1))
                self.api_promocion_por_id_handler(promo_id)
                return

            routes = {
                '/': self.servir_pagina_inicio,
                '/login': self.servir_pagina_login,
                '/registro': self.servir_pagina_registro,
                '/logout': self.manejar_logout_get,
                '/admin': self.servir_pagina_admin,
                '/cliente': self.servir_pagina_cliente,
                '/cliente/carrito': self.servir_pagina_carrito,
                '/cliente/perfil': self.servir_pagina_perfil,
                '/cliente/mis-contenidos': self.servir_pagina_mis_contenidos,
                '/ofertas': self.servir_pagina_ofertas,
                '/admin/categorias': self.servir_pagina_administrar_categorias,
                '/admin/clientes': self.servir_pagina_administrar_clientes,
                '/admin/contenidos': self.servir_pagina_administrar_contenidos,
                '/admin/promociones': self.servir_pagina_administrar_promociones,
                '/api/contenidos': self.api_contenidos_handler,
                '/api/inicio': self.api_inicio_handler,
                '/api/sesion': self.obtener_sesion_handler,
                '/api/obtener_promociones': self.api_obtener_promociones_handler,
                '/api/promociones/contenidos': self.api_promociones_contenidos_handler,
                '/api/contenidos/categorias': self.api_categorias_contenido_handler,
                '/api/categorias/buscar': self.api_categorias_buscar_handler,
                '/api/clientes': self.api_clientes_handler,
                '/api/clientes/buscar': self.api_clientes_buscar_handler,
                '/api/carrito': self.api_carrito_handler,
                '/api/mis-contenidos/obtener': self.api_mis_contenidos_handler,
                '/api/usuario/perfil': self.api_usuario_perfil_handler,
                '/api/usuario/historial': self.api_usuario_historial_handler,
                '/api/usuario/historial-compras': self.api_usuario_historial_compras_handler,
                '/api/regalos/recibidos': self.api_regalos_recibidos_handler,
                '/api/descuentos/info': self.api_descuentos_info_handler,
                '/api/notificaciones/regalos': self.api_notificaciones_regalos_handler,
                '/api/usuario/buscar': self.api_usuario_buscar_handler,
                '/cliente/ranking': self.servir_pagina_ranking
            }

            import re

            download_match = re.match(r'/api/mis-contenidos/descargar/(\d+)', path)
            if download_match:
                content_id = int(download_match.group(1))
                self.api_mis_contenidos_descargar_handler(content_id)
                return

            view_match = re.match(r'/api/contenido/(\d+)/ver', path)
            if view_match:
                content_id = int(view_match.group(1))
                self.api_contenido_ver_handler(content_id)
                return

            thumbnail_match = re.match(r'/api/contenido/(\d+)/miniatura', path)
            if thumbnail_match:
                content_id = int(thumbnail_match.group(1))
                self.api_contenido_miniatura_handler(content_id)
                return

            ranking_match = re.match(r'/api/ranking/(\w+)', path)
            if ranking_match:
                tipo_ranking = ranking_match.group(1)
                self.api_ranking_handler(tipo_ranking)
                return

            if path == '/api/contenido' and parsed_url.query:
                query_params = parse_qs(parsed_url.query)
                contenido_id = query_params.get('id', [None])[0]
                if contenido_id:
                    self.api_contenido_por_id_handler(contenido_id)
                    return

            saldo_match = re.match(r'/api/clientes/(\d+)/saldo', path)
            if saldo_match:
                cliente_id = int(saldo_match.group(1))
                self.api_clientes_saldo_handler(cliente_id)
                return

            historial_match = re.match(r'/api/clientes/(\d+)/historial', path)
            if historial_match:
                cliente_id = int(historial_match.group(1))
                self.api_clientes_historial_handler(cliente_id)
                return

            promo_contenidos_match = re.match(r'/api/promociones/(\d+)/contenidos', path)
            if promo_contenidos_match:
                promo_id = int(promo_contenidos_match.group(1))
                self.api_promocion_contenidos_handler(promo_id)
                return

            arbol_match = re.match(r'/api/categorias/arbol/(\d+)', path)
            if arbol_match:
                id_categoria = int(arbol_match.group(1))
                return self.api_categoria_arbol_mermaid_handler(id_categoria)

            if path in routes:
                if path.startswith('/api/'):
                    routes[path]()
                else:
                    contenido = routes[path]()
                    if contenido:
                        contenido_bytes = contenido.encode('utf-8')
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html; charset=utf-8')
                        self.send_header('Content-Length', str(len(contenido_bytes)))
                        self.send_header('Cache-Control', 'no-cache')
                        self.end_headers()
                        self.wfile.write(contenido_bytes)
                    else:
                        self.send_error(500, "Error interno del servidor")
            else:
                self.servir_archivo_estatico(path)

        except Exception as e:
            self.send_error(500, f"Error interno del servidor: {str(e)}")

    # HTTP-026: Maneja solicitudes POST
    def do_POST(self):
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path

            routes_post = {
                '/api/login': self.autenticar_usuario,
                '/api/registro': self.registrar_usuario,
                '/api/logout': self.cerrar_sesion_handler,
                '/api/carrito/agregar': self.api_carrito_agregar_handler,
                '/api/carrito/comprar': self.api_carrito_comprar_handler,
                '/api/usuario/cambiar-contrasena': self.api_usuario_cambiar_contrasena_handler,
                '/api/usuario/eliminar-cuenta': self.api_usuario_eliminar_cuenta_handler,
                '/api/mis-contenidos/calificar': self.api_mis_contenidos_calificar_handler,
                '/api/mis-contenidos/descargas-no-valoradas': self.api_mis_contenidos_descargas_no_valoradas_handler,
                '/api/contenidos/eliminar': self.api_contenidos_eliminar_handler,
                '/api/contenidos/editar': self.api_contenidos_editar_handler,
                '/api/regalos/enviar': self.api_regalos_enviar_handler,
                '/api/descuentos/aplicar': self.api_descuentos_aplicar_handler,
                '/api/regalos/abrir': self.api_regalos_abrir_handler,
                '/api/notificaciones/marcar-leida': self.api_notificaciones_marcar_leida_handler,
                '/api/categorias': self.api_categorias_crear_handler,
                '/api/promociones': self.api_promocion_crear_handler,
                '/api/promociones/eliminar': self.api_promocion_eliminar_handler,
                '/api/promociones/crear': self.api_promocion_crear_handler,
                '/api/contenidos/agregar_contenido': self.api_contenidos_agregar_handler
            }

            import re

            saldo_match = re.match(r'/api/clientes/(\d+)/saldo', path)
            if saldo_match:
                cliente_id = int(saldo_match.group(1))
                self.api_clientes_saldo_handler(cliente_id)
                return

            if path in routes_post:
                routes_post[path]()
            else:
                self.send_error_response(404, "Endpoint no encontrado")

        except Exception as e:
            self.send_error_response(500, "Error interno del servidor")

    # HTTP-027: Maneja solicitudes PUT
    def do_PUT(self):
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path

            routes_put = {}

            import re

            categoria_match = re.match(r'/api/categorias/(\d+)', path)
            if categoria_match:
                categoria_id = int(categoria_match.group(1))
                self.api_categorias_actualizar_handler(categoria_id)
                return

            promocion_match = re.match(r'/api/promociones/(\d+)', path)
            if promocion_match:
                promocion_id = int(promocion_match.group(1))
                self.api_promocion_actualizar_handler(promocion_id)
                return

            if path in routes_put:
                routes_put[path]()
            else:
                self.send_error_response(404, "Endpoint no encontrado")

        except Exception as e:
            self.send_error_response(500, "Error interno del servidor")

    # HTTP-028: Maneja la API para actualizar categorías
    def api_categorias_actualizar_handler(self, categoria_id):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))

                nombre = datos.get('nombre')

                if not nombre:
                    return self.send_json_response({"error": "Nombre de categoría requerido"}, 400)

                resultado = controladorCategoria.actualizar_categoria(categoria_id, nombre)
                return self.send_json_response({
                    "success": True,
                    "message": "Categoría actualizada exitosamente",
                    "categoria": resultado
                })
            else:
                return self.send_json_response({"error": "Datos no proporcionados"}, 400)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-029: Maneja solicitudes DELETE
    def do_DELETE(self):
        from urllib.parse import urlparse
        import re

        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path

            match = re.match(r'/api/carrito/(\d+)', path)
            if match:
                item_id = int(match.group(1))
                self.api_carrito_eliminar_handler(item_id)
            else:
                self.send_error_response(404, "Endpoint no encontrado")

        except Exception as e:
            self.send_error_response(500, "Error interno del servidor")

    # HTTP-030: Maneja la API para eliminar items del carrito
    def api_carrito_eliminar_handler(self, item_id):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "Usuario no válido"}, 401)

            if not self.controlador_carrito:
                return self.send_json_response({"error": "Controlador no disponible"}, 500)

            resultado = self.controlador_carrito.eliminar_contenido(user_id, item_id)
            return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-031: Maneja solicitudes OPTIONS
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    # HTTP-032: Sirve archivos estáticos
    def servir_archivo_estatico(self, path):
        try:
            if path.startswith('/'):
                path = path[1:]

            ruta_completa = os.path.join('static', path)

            if not os.path.exists(ruta_completa):
                self.send_error_response(404, "Archivo no encontrado")
                return

            content_type = 'text/plain'
            if path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.js'):
                content_type = 'text/javascript'
            elif path.endswith('.png'):
                content_type = 'image/png'
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif path.endswith('.gif'):
                content_type = 'image/gif'
            elif path.endswith('.html'):
                content_type = 'text/html; charset=utf-8'

            with open(ruta_completa, 'rb') as file:
                contenido = file.read()

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-Length', str(len(contenido)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(contenido)

        except Exception as e:
            self.send_error_response(500, "Error interno del servidor")

    # HTTP-033: Autentica un usuario
    def autenticar_usuario(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))

            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))
                username = datos.get('username', '')
                password = datos.get('password', '')

                if not self.controlador_usuarios:
                    return self.send_json_response({"error": "Controlador no disponible"}, 500)

                resultado = self.controlador_usuarios.autenticar_usuario({
                    'username': username,
                    'password': password
                })

                if resultado.get('success'):
                    user_id = resultado.get('user_id')
                    nombre = resultado.get('nombre', '')

                    tipo_usuario = self.determinar_tipo_usuario_por_id(user_id, username)

                    session_id = str(uuid.uuid4())

                    session_data = {
                        'user_id': user_id,
                        'username': username,
                        'nombre': nombre,
                        'tipo': tipo_usuario,
                        'es_admin': tipo_usuario == 'admin',
                        'timestamp': datetime.now().isoformat()
                    }

                    sesiones_activas[session_id] = session_data
                    sessions[session_id] = session_data

                    if tipo_usuario == 'admin':
                        redirect_url = '/admin'
                    else:
                        redirect_url = '/cliente'

                    respuesta = {
                        "success": True,
                        "redirect": redirect_url,
                        "session_id": session_id,
                        "tipo_usuario": tipo_usuario,
                        "mensaje": f"Bienvenido de vuelta, {nombre}!"
                    }

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.send_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly; SameSite=Lax')
                    self.end_headers()

                    response_json = json.dumps(respuesta, ensure_ascii=False)
                    self.wfile.write(response_json.encode('utf-8'))
                    return

                else:
                    respuesta = {
                        "success": False,
                        "message": resultado.get('mensaje', 'Credenciales inválidas')
                    }

                    return responder_json(self, respuesta, 401)

            else:
                respuesta = {"success": False, "message": "No se recibieron datos"}
                return responder_json(self, respuesta, 400)

        except Exception as e:
            respuesta = {"success": False, "message": f"Error en la autenticación: {str(e)}"}
            return responder_json(self, respuesta, 500)

    # HTTP-034: Determina el tipo de usuario
    def determinar_tipo_usuario_por_id(self, user_id, username):
        try:
            if self.controlador_usuarios and hasattr(self.controlador_usuarios, 'determinar_tipo_usuario'):
                return self.controlador_usuarios.determinar_tipo_usuario(user_id, username)
            else:
                return 'cliente'
        except Exception:
            return 'cliente'

    # HTTP-035: Registra un nuevo usuario
    def registrar_usuario(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))
            else:
                datos = {}

            if self.controlador_usuarios and hasattr(self.controlador_usuarios, 'registrar_usuario'):
                resultado = self.controlador_usuarios.registrar_usuario(datos)
            else:
                resultado = {
                    'success': False,
                    'message': 'Error del servidor'
                }

            if resultado.get('success'):
                self.redirect_to('/login')
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

            response_json = json.dumps(resultado, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))

        except Exception as e:
            self.send_error_response(500, "Error interno del servidor")

    # HTTP-036: Obtiene el ID de sesión de las cookies
    def get_session_id(self):
        try:
            cookie_header = self.headers.get('Cookie', '')
            if cookie_header:
                cookies = dict(item.split("=") for item in cookie_header.split("; "))
                return cookies.get('session_id')
        except:
            pass
        return None

    # HTTP-037: Redirige a una URL específica
    def redirect_to(self, url):
        self.send_response(302)
        self.send_header('Location', url)
        self.end_headers()

    # HTTP-038: Redirige a la página de administrador
    def redirect_to_admin(self):
        try:
            session_id = self.get_session_id()
            if not session_id or session_id not in sesiones_activas:
                self.redirect_to('/login')
                return

            session = sesiones_activas[session_id]
            if session['tipo'] != 'admin':
                self.redirect_to('/login')
                return

            contenido = self.servir_pagina_admin()
            if contenido:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(contenido.encode('utf-8'))
        except Exception as e:
            self.send_error_response(500, "Error interno del servidor")

    # HTTP-039: Redirige a la página de cliente
    def redirect_to_cliente(self):
        try:
            session_id = self.get_session_id()
            if not session_id or session_id not in sesiones_activas:
                self.redirect_to('/login')
                return

            session = sesiones_activas[session_id]
            if session['tipo'] != 'cliente':
                self.redirect_to('/login')
                return

            contenido = self.servir_pagina_cliente()
            if contenido:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(contenido.encode('utf-8'))
        except Exception as e:
            self.send_error_response(500, "Error interno del servidor")

    # HTTP-040: Maneja la API para obtener clientes
    def api_clientes_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            clientes = controladorClientes.obtener_todos_clientes()
            return self.send_json_response({"success": True, "data": clientes})

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-041: Maneja la API para obtener el carrito
    def api_carrito_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('user_id'):
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')

            if not self.controlador_carrito:
                return self.send_json_response({"error": "Controlador no disponible"}, 500)

            resultado = self.controlador_carrito.obtener_carrito(user_id)
            return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-042: Maneja la API para obtener contenidos adquiridos
    def api_mis_contenidos_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('user_id'):
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')

            resultado = controladorContenidosAdquiridos.obtener_mis_contenidos(user_id)

            return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-043: Maneja la API para obtener el perfil del usuario
    def api_usuario_perfil_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "No autenticado"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "No autenticado"}, 401)

            if not self.controlador_perfil:
                return self.send_json_response({"error": "Controlador no disponible"}, 500)

            perfil = self.controlador_perfil.obtener_datos_perfil(user_id)

            if not perfil:
                return self.send_json_response({"error": "Perfil no encontrado"}, 404)

            return self.send_json_response({"data": perfil})
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-044: Maneja la API para obtener historial de usuario
    def api_usuario_historial_handler(self, cliente_id):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            historial = controladorClientes.obtener_historial_cliente(cliente_id)

            if isinstance(historial, list):
                for item in historial:
                    if isinstance(item, dict):
                        fecha = item.get('fecha_descarga')
                        if isinstance(fecha, datetime):
                            item['fecha_descarga'] = fecha.strftime('%Y-%m-%d %H:%M:%S')
                return self.send_json_response({"success": True, "data": historial})
            elif isinstance(historial, dict):
                return self.send_json_response({"success": True, "data": historial.get("data", [])})
            else:
                return self.send_json_response({"success": True, "data": []})

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-045: Maneja la API para obtener historial de compras
    def api_usuario_historial_compras_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "Usuario no válido"}, 401)

            historial_compras = controladorClientes.obtener_historial_compras_cliente(user_id)

            if isinstance(historial_compras, list):
                for item in historial_compras:
                    if isinstance(item, dict) and 'fecha_y_hora' in item:
                        fecha = item['fecha_y_hora']
                        if isinstance(fecha, datetime):
                            item['fecha_y_hora'] = fecha.strftime('%Y-%m-%d %H:%M:%S')
                return self.send_json_response({"success": True, "data": historial_compras})
            elif isinstance(historial_compras, dict):
                return self.send_json_response({"success": True, "data": []})
            else:
                return self.send_json_response({"success": True, "data": []})

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-046: Maneja el cierre de sesión
    def cerrar_sesion_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if 'session_id=' in cookie:
                session_id = cookie.split('session_id=')[1].split(';')[0]

                if session_id in sessions:
                    del sessions[session_id]
                if session_id in sesiones_activas:
                    del sesiones_activas[session_id]

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Set-Cookie',
                             'session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; SameSite=Lax')
            self.end_headers()

            response_data = {
                "success": True,
                "message": "Sesión cerrada correctamente",
                "redirect": "/"
            }

            response_json = json.dumps(response_data, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_response = {
                "success": False,
                "error": str(e)
            }

            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    # HTTP-047: Maneja la API para cambiar contraseña
    def api_usuario_cambiar_contrasena_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "No autenticado"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "No autenticado"}, 401)

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))

                contrasena_actual = datos.get('contrasena_actual', '')
                nueva_contrasena = datos.get('nueva_contrasena', '')

                if not contrasena_actual or not nueva_contrasena:
                    return self.send_json_response({"error": "Datos incompletos"}, 400)

                if not self.controlador_perfil:
                    return self.send_json_response({"error": "Controlador no disponible"}, 500)

                resultado = self.controlador_perfil.cambiar_contrasena(user_id, contrasena_actual, nueva_contrasena)
                return self.send_json_response(resultado)
            else:
                return self.send_json_response({"error": "Datos no proporcionados"}, 400)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-048: Maneja la API para eliminar cuenta
    def api_usuario_eliminar_cuenta_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "No autenticado"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "No autenticado"}, 401)

            content_length = int(self.headers.get('Content-Length', 0))
            contrasena = ""
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))
                contrasena = datos.get('contrasena', '')

            if not contrasena:
                return self.send_json_response({"error": "Contraseña requerida"}, 400)

            if not self.controlador_perfil:
                return self.send_json_response({"error": "Controlador no disponible"}, 500)

            resultado = self.controlador_perfil.eliminar_cuenta(user_id, contrasena)
            return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-049: Maneja la API para agregar al carrito
    def api_carrito_agregar_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('user_id'):
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))

                contenido_id = datos.get('contenido_id')
                cantidad = datos.get('cantidad', 1)

                if not contenido_id:
                    return self.send_json_response({"error": "ID de contenido requerido"}, 400)

                if not self.controlador_carrito:
                    return self.send_json_response({"error": "Controlador no disponible"}, 500)

                resultado = self.controlador_carrito.agregar_contenido(user_id, contenido_id, cantidad)
                return self.send_json_response(resultado)
            else:
                return self.send_json_response({"error": "Datos no proporcionados"}, 400)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-050: Maneja la API para comprar el carrito
    def api_carrito_comprar_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('user_id'):
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')

            if not self.controlador_carrito:
                return self.send_json_response({"error": "Controlador no disponible"}, 500)

            resultado = self.controlador_carrito.procesar_compra(user_id)
            return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": "Error interno del servidor"}, 500)

    # HTTP-051: Maneja la API para descargar contenido
    def api_mis_contenidos_descargar_handler(self, content_id):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('user_id'):
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')

            resultado = controladorContenidosAdquiridos.descargar_contenido(user_id, content_id)

            if resultado.get('success'):
                nombre = resultado.get('nombre', f'contenido_{content_id}')
                archivo_binario = resultado.get('archivo')
                mime_type = resultado.get('mime_type', 'application/octet-stream')

                if archivo_binario:
                    self.send_response(200)
                    self.send_header('Content-Type', mime_type)
                    self.send_header('Content-Disposition', f'attachment; filename="{nombre}"')
                    self.send_header('Content-Length', str(len(archivo_binario)))
                    self.end_headers()
                    self.wfile.write(archivo_binario)
                else:
                    return self.send_json_response({"error": "Archivo no encontrado"}, 404)
            else:
                return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-052: Maneja la API para ver contenido
    def api_contenido_ver_handler(self, content_id):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('user_id'):
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')

            contenido = controladorContenido.obtener_contenido(content_id)

            if contenido:
                return self.send_json_response(contenido)
            else:
                return self.send_json_response({"error": "Contenido no encontrado"}, 404)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-053: Maneja la API para obtener miniaturas de contenido
    def api_contenido_miniatura_handler(self, content_id):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('user_id'):
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')

            from domain.entities.contenido import Contenido
            contenido = Contenido.obtener_por_id(content_id)

            if not contenido:
                return self.send_json_response({"error": "Contenido no encontrado"}, 404)

            if contenido.formato and 'imagen' in contenido.formato.lower():
                if contenido.archivo:
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', str(len(contenido.archivo)))
                    self.send_header('Cache-Control', 'public, max-age=3600')
                    self.end_headers()
                    self.wfile.write(contenido.archivo)
                    return
                else:
                    self._generar_placeholder_imagen()
            elif contenido.formato and ('video' in contenido.formato.lower() or 'mp4' in contenido.formato.lower()):
                self._generar_placeholder_video()
            elif contenido.formato and ('audio' in contenido.formato.lower() or 'mp3' in contenido.formato.lower()):
                self._generar_placeholder_audio()
            else:
                self._generar_placeholder_generico()

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-054: Genera placeholder para imágenes
    def _generar_placeholder_imagen(self):
        svg_content = '''
        <svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#f0f0f0"/>
            <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-family="Arial" font-size="16" fill="#666">
                Imagen
            </text>
        </svg>
        '''

        self.send_response(200)
        self.send_header('Content-Type', 'image/svg+xml')
        self.send_header('Content-Length', str(len(svg_content)))
        self.send_header('Cache-Control', 'public, max-age=3600')
        self.end_headers()
        self.wfile.write(svg_content.encode('utf-8'))

    # HTTP-055: Genera placeholder para videos
    def _generar_placeholder_video(self):
        svg_content = '''
        <svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#e0e0e0"/>
            <circle cx="150" cy="100" r="40" fill="#333" opacity="0.8"/>
            <polygon points="140,85 140,115 165,100" fill="white"/>
            <text x="50%" y="85%" text-anchor="middle" font-family="Arial" font-size="14" fill="#666">
                Video
            </text>
        </svg>
        '''

        self.send_response(200)
        self.send_header('Content-Type', 'image/svg+xml')
        self.send_header('Content-Length', str(len(svg_content)))
        self.send_header('Cache-Control', 'public, max-age=3600')
        self.end_headers()
        self.wfile.write(svg_content.encode('utf-8'))

    # HTTP-056: Genera placeholder para audios
    def _generar_placeholder_audio(self):
        svg_content = '''
        <svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#f8f8f8"/>
            <circle cx="150" cy="100" r="30" fill="#4CAF50"/>
            <text x="150" y="105" text-anchor="middle" font-family="Arial" font-size="20" fill="white">♪</text>
            <rect x="200" y="80" width="4" height="40" fill="#666"/>
            <rect x="210" y="70" width="4" height="60" fill="#666"/>
            <rect x="220" y="85" width="4" height="30" fill="#666"/>
            <rect x="230" y="75" width="4" height="50" fill="#666"/>
            <rect x="240" y="90" width="4" height="20" fill="#666"/>
            <text x="50%" y="85%" text-anchor="middle" font-family="Arial" font-size="14" fill="#666">
                Audio
            </text>
        </svg>
        '''

        self.send_response(200)
        self.send_header('Content-Type', 'image/svg+xml')
        self.send_header('Content-Length', str(len(svg_content)))
        self.send_header('Cache-Control', 'public, max-age=3600')
        self.end_headers()
        self.wfile.write(svg_content.encode('utf-8'))

    # HTTP-057: Genera placeholder genérico
    def _generar_placeholder_generico(self):
        svg_content = '''
        <svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#f5f5f5"/>
            <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-family="Arial" font-size="16" fill="#999">
                Contenido
            </text>
        </svg>
        '''

        self.send_response(200)
        self.send_header('Content-Type', 'image/svg+xml')
        self.send_header('Content-Length', str(len(svg_content)))
        self.send_header('Cache-Control', 'public, max-age=3600')
        self.end_headers()
        self.wfile.write(svg_content.encode('utf-8'))

    # HTTP-058: Maneja la API para calificar contenido
    def api_mis_contenidos_calificar_handler(self):
        from app.controllers.controlador_contenidos_adquiridos import ControladorContenidosAdquiridos
        user_id = self.get_user_id_from_session()
        if not user_id:
            self.send_json_response({'success': False, 'error': 'No autenticado'}, status_code=401)
            return
        data = self.get_json_body()
        id_contenido = data.get('id_contenido')
        puntuacion = data.get('puntuacion')
        id_descarga = data.get('id_descarga')
        ctrl = ControladorContenidosAdquiridos()
        result = ctrl.calificar_contenido(user_id, id_contenido, puntuacion, id_descarga)
        self.send_json_response(result)

    # HTTP-059: Maneja la API para obtener contenidos de promoción
    def api_promocion_contenidos_handler(self, promo_id):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)
            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)
            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            resultado = controladorPromocion.obtener_promocion_por_id(promo_id)

            if isinstance(resultado, tuple):
                datos, status_code = resultado
                return self.send_json_response(datos, status_code)
            else:
                return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-060: Maneja la API para obtener ranking
    def api_ranking_handler(self, tipo_ranking):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            contenido = controladorRanking.obtener_contenido_por_tipo(tipo_ranking)
            return self.send_json_response(contenido)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-061: Maneja el logout GET
    def manejar_logout_get(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if 'session_id=' in cookie:
                session_id = cookie.split('session_id=')[1].split(';')[0]

                if session_id in sessions:
                    del sessions[session_id]
                if session_id in sesiones_activas:
                    del sesiones_activas[session_id]

            self.send_response(302)
            self.send_header('Location', '/')
            self.send_header('Set-Cookie',
                             'session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; SameSite=Lax')
            self.end_headers()

        except Exception as e:
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

    # HTTP-062: Maneja la API para obtener promociones
    def api_obtener_promociones_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            promociones = controladorPromocion.obtener_todas_promociones()
            return self.send_json_response({"success": True, "data": promociones})

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-063: Maneja la API para eliminar contenidos
    def api_contenidos_eliminar_handler(self):
        try:
            content_type = self.headers['Content-Type']

            if 'application/json' in content_type:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body)
                content_id = data.get('id')
            elif 'application/x-www-form-urlencoded' in content_type:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length).decode('utf-8')
                from urllib.parse import parse_qs
                parsed_data = parse_qs(body)
                content_id = parsed_data.get('contenido_id', [None])[0]
            else:
                return self.send_json_response({"error": "Tipo de contenido no soportado"}, 400)

            if not content_id:
                return self.send_json_response({"error": "ID de contenido no proporcionado"}, 400)

            from app.controllers.controlador_contenido import ControladorContenido
            controlador = ControladorContenido()
            resultado = controlador.eliminar_contenido(content_id)

            if resultado['success']:
                return self.send_json_response(resultado)
            else:
                return self.send_json_response({"error": resultado.get('message', 'Error al eliminar')}, 404)
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-064: Maneja la API para agregar contenidos
    def api_contenidos_agregar_handler(self):
        try:
            import cgi
            from io import BytesIO
            form = cgi.FieldStorage(
                fp=BytesIO(self.rfile.read(int(self.headers['Content-Length']))),
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']}
            )

            contenido_data = {
                "nombre": form.getvalue("nombre"),
                "autor": form.getvalue("autor"),
                "descripcion": form.getvalue("descripcion"),
                "precio": form.getvalue("precio"),
                "id_categoria": form.getvalue("categoria_id")
            }

            if 'archivo' in form and form['archivo'].filename:
                archivo_item = form['archivo']
                contenido_data['archivo'] = {
                    'filename': archivo_item.filename,
                    'file_content': archivo_item.file.read()
                }

            from app.controllers.controlador_contenido import ControladorContenido
            controlador = ControladorContenido()
            resultado = controlador.agregar_contenido(contenido_data)

            if resultado and resultado.get('success'):
                return self.send_json_response(resultado)
            else:
                error_msg = resultado.get('error', 'Error desconocido al agregar contenido')
                return self.send_json_response({"error": error_msg}, 500)

        except Exception as e:
            return self.send_json_response({"error": f"Error en el servidor: {str(e)}"}, 500)

    # HTTP-065: Maneja la API para editar contenidos
    def api_contenidos_editar_handler(self):
        try:
            import cgi
            from io import BytesIO
            form = cgi.FieldStorage(
                fp=BytesIO(self.rfile.read(int(self.headers['Content-Length']))),
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type']}
            )

            contenido_data = {
                "id_contenido": form.getvalue("contenido_id"),
                "nombre": form.getvalue("nombre"),
                "autor": form.getvalue("autor"),
                "descripcion": form.getvalue("descripcion"),
                "precio": form.getvalue("precio"),
                "id_categoria": form.getvalue("categoria_id"),
            }

            if 'archivo' in form and form['archivo'].filename:
                archivo_item = form['archivo']
                contenido_data['archivo'] = {
                    'filename': archivo_item.filename,
                    'file_content': archivo_item.file.read()
                }

            from app.controllers.controlador_contenido import ControladorContenido
            controlador = ControladorContenido()
            resultado = controlador.actualizar_contenido(contenido_data)

            if resultado.get('success'):
                return self.send_json_response(resultado)
            else:
                return self.send_json_response({"error": resultado.get('error', 'Error al actualizar')}, 400)

        except Exception as e:
            return self.send_json_response({"error": f"Error en el servidor: {str(e)}"}, 500)

    # HTTP-066: Maneja la API para obtener contenido por ID
    def api_contenido_por_id_handler(self, content_id):
        try:
            from app.controllers.controlador_contenido import ControladorContenido
            controlador = ControladorContenido()
            contenido = controlador.obtener_contenido(content_id)

            if contenido:
                return self.send_json_response(contenido)
            else:
                return self.send_json_response({"error": "Contenido no encontrado"}, 404)
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-067: Maneja la API para actualizar saldo de cliente
    def api_clientes_saldo_handler(self, cliente_id):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))

                nuevo_saldo = datos.get('nuevo_saldo')

                if not nuevo_saldo:
                    return self.send_json_response({"error": "Nuevo saldo requerido"}, 400)

                resultado = controladorClientes.actualizar_saldo_cliente(cliente_id, nuevo_saldo)
                return self.send_json_response(resultado)
            else:
                return self.send_json_response({"error": "Datos no proporcionados"}, 400)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-068: Maneja la API para obtener historial de cliente
    def api_clientes_historial_handler(self, cliente_id):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            historial = controladorClientes.obtener_historial_cliente(cliente_id)

            if isinstance(historial, list):
                for item in historial:
                    if isinstance(item, dict):
                        fecha = item.get('fecha_descarga')
                        if isinstance(fecha, datetime):
                            item['fecha_descarga'] = fecha.strftime('%Y-%m-%d %H:%M:%S')
                return self.send_json_response({"success": True, "data": historial})
            elif isinstance(historial, dict):
                return self.send_json_response({"success": True, "data": historial.get("data", [])})
            else:
                return self.send_json_response({"success": True, "data": []})

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-069: Maneja la API para obtener regalos recibidos
    def api_regalos_recibidos_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "Usuario no válido"}, 401)

            from app.controllers.controlador_regalo import ControladorRegalo
            controlador_regalo = ControladorRegalo()
            resultado = controlador_regalo.obtener_regalos_recibidos(user_id)
            return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-070: Maneja la API para obtener información de descuentos
    def api_descuentos_info_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "Usuario no válido"}, 401)

            from domain.entities.carrito import Carrito
            info_descuentos = Carrito.obtener_descuentos_aplicados(user_id)
            return self.send_json_response({"success": True, "data": info_descuentos})

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-071: Maneja la API para enviar regalos
    def api_regalos_enviar_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "Usuario no válido"}, 401)

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))

                id_usuario_recibe = datos.get('id_usuario_recibe')
                id_contenido = datos.get('id_contenido')

                if not id_usuario_recibe or not id_contenido:
                    return self.send_json_response({"error": "Datos incompletos"}, 400)

                from app.controllers.controlador_regalo import ControladorRegalo
                controlador_regalo = ControladorRegalo()
                resultado = controlador_regalo.enviar_regalo(user_id, id_usuario_recibe, id_contenido)
                return self.send_json_response(resultado)
            else:
                return self.send_json_response({"error": "Datos no proporcionados"}, 400)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-072: Maneja la API para aplicar descuentos
    def api_descuentos_aplicar_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "Usuario no válido"}, 401)

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))

                id_contenido = datos.get('id_contenido')
                aplicar = datos.get('aplicar', True)

                if not id_contenido:
                    return self.send_json_response({"error": "ID de contenido requerido"}, 400)

                from domain.entities.carrito import Carrito
                resultado = Carrito.aplicar_descuento_contenido(user_id, id_contenido, aplicar)
                return self.send_json_response(resultado)
            else:
                return self.send_json_response({"error": "Datos no proporcionados"}, 400)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-073: Maneja la API para notificaciones de regalos
    def api_notificaciones_regalos_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "Usuario no válido"}, 401)

            from app.controllers.controlador_notificacion import ControladorNotificacion
            controlador_notificacion = ControladorNotificacion()
            resultado = controlador_notificacion.obtener_notificaciones_regalos(user_id)
            return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-074: Maneja la API para abrir regalos
    def api_regalos_abrir_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "Usuario no válido"}, 401)

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))

                id_regalo = datos.get('id_regalo')

                if not id_regalo:
                    return self.send_json_response({"error": "ID de regalo requerido"}, 400)

                from app.controllers.controlador_regalo import ControladorRegalo
                controlador_regalo = ControladorRegalo()
                resultado = controlador_regalo.abrir_regalo(id_regalo, user_id)
                return self.send_json_response(resultado)
            else:
                return self.send_json_response({"error": "Datos no proporcionados"}, 400)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-075: Maneja la API para buscar usuarios
    def api_usuario_buscar_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            username = query_params.get('username', [None])[0]

            if not username:
                return self.send_json_response({"error": "Username requerido"}, 400)

            from app.controllers.controlador_usuarios import ControladorUsuarios
            controlador_usuarios = ControladorUsuarios()
            resultado = controlador_usuarios.buscar_usuario_por_username(username)
            return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-076: Maneja la API para marcar notificaciones como leídas
    def api_notificaciones_marcar_leida_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            user_id = session_data.get('user_id')
            if not user_id:
                return self.send_json_response({"error": "Usuario no válido"}, 401)

            content_length = int(self.headers.get('Content-Length', 0))
            id_regalo = None

            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))
                id_regalo = datos.get('id_regalo')

            from app.controllers.controlador_notificacion import ControladorNotificacion
            controlador_notificacion = ControladorNotificacion()
            resultado = controlador_notificacion.marcar_notificacion_leida(user_id, id_regalo)
            return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-077: Maneja la API para crear categorías
    def api_categorias_crear_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))

                nombre = datos.get('nombre')
                id_categoria_padre = datos.get('id_categoria_padre')

                if not nombre:
                    return self.send_json_response({"error": "Nombre de categoría requerido"}, 400)

                resultado = controladorCategoria.crear_categoria(nombre, id_categoria_padre)
                return self.send_json_response({
                    "success": True,
                    "message": "Categoría creada exitosamente",
                    "categoria": resultado
                })
            else:
                return self.send_json_response({"error": "Datos no proporcionados"}, 400)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-078: Maneja la API para buscar clientes
    def api_clientes_buscar_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            termino = query_params.get('termino', [''])[0]

            resultado = controladorClientes.buscar_clientes(termino)

            return self.send_json_response(resultado)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-079: Maneja la API para crear promociones
    def api_promocion_crear_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                datos = json.loads(post_data.decode('utf-8'))

                resultado = controladorPromocion.agregar_promocion(datos)
                return self.send_json_response(resultado)
            else:
                return self.send_json_response({"error": "Datos no proporcionados"}, 400)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-080: Maneja la API para actualizar promociones
    def api_promocion_actualizar_handler(self, promocion_id):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            content_length = int(self.headers.get('Content-Length', 0))

            if content_length > 0:
                post_data = self.rfile.read(content_length)

                content_type = self.headers.get('Content-Type', '')

                if 'application/json' in content_type:
                    try:
                        datos = json.loads(post_data.decode('utf-8'))
                    except json.JSONDecodeError as e:
                        return self.send_json_response({"error": f"Error al parsear JSON: {str(e)}"}, 400)
                elif 'multipart/form-data' in content_type:
                    try:
                        datos_raw = post_data.decode('utf-8')
                        datos = {}
                        lines = datos_raw.split('\r\n')
                        current_field = None
                        for line in lines:
                            if line.startswith('Content-Disposition: form-data; name='):
                                field_name = line.split('name="')[1].split('"')[0]
                                current_field = field_name
                            elif current_field and line and not line.startswith('------'):
                                if current_field in datos:
                                    if not isinstance(datos[current_field], list):
                                        datos[current_field] = [datos[current_field]]
                                    datos[current_field].append(line)
                                else:
                                    datos[current_field] = line
                                current_field = None
                        if 'contenidos' in datos:
                            if isinstance(datos['contenidos'], list):
                                datos['contenidos'] = [int(x) for x in datos['contenidos'] if x]
                            elif datos['contenidos']:
                                datos['contenidos'] = [int(datos['contenidos'])]
                    except Exception as e:
                        return self.send_json_response({"error": f"Error al parsear multipart: {str(e)}"}, 400)
                else:
                    return self.send_json_response({"error": "Tipo de contenido no soportado"}, 400)

                resultado = controladorPromocion.editar_promocion(promocion_id, datos)
                return self.send_json_response(resultado)
            else:
                return self.send_json_response({"error": "Datos no proporcionados"}, 400)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-081: Maneja la API para eliminar promociones
    def api_promocion_eliminar_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)

                content_type = self.headers.get('Content-Type', '')

                if 'application/json' in content_type:
                    datos = json.loads(post_data.decode('utf-8'))
                elif 'multipart/form-data' in content_type:
                    datos_raw = post_data.decode('utf-8')
                    datos = {}
                    lines = datos_raw.split('\r\n')
                    current_field = None

                    for line in lines:
                        if line.startswith('Content-Disposition: form-data; name='):
                            field_name = line.split('name="')[1].split('"')[0]
                            current_field = field_name
                        elif current_field and line and not line.startswith('------'):
                            datos[current_field] = line
                            current_field = None
                else:
                    return self.send_json_response({"error": "Tipo de contenido no soportado"}, 400)

                promocion_id = datos.get('promocion_id')
                if not promocion_id:
                    return self.send_json_response({"error": "ID de promoción requerido"}, 400)

                resultado = controladorPromocion.eliminar_promocion(int(promocion_id))
                return self.send_json_response(resultado)
            else:
                return self.send_json_response({"error": "Datos no proporcionados"}, 400)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-082: Maneja la API para obtener contenidos con promociones
    def api_promociones_contenidos_handler(self):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data:
                return self.send_json_response({"error": "Sesión inválida"}, 401)

            contenidos = controladorPromocion.obtener_contenidos_con_promociones()
            return self.send_json_response(contenidos)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    # HTTP-083: Maneja la API para obtener promoción por ID
    def api_promocion_por_id_handler(self, promocion_id):
        try:
            cookie = self.headers.get('Cookie', '')
            if not cookie or 'session_id=' not in cookie:
                return self.send_json_response({"error": "No autenticado"}, 401)

            session_id = cookie.split('session_id=')[1].split(';')[0]
            session_data = sessions.get(session_id) or sesiones_activas.get(session_id)

            if not session_data or not session_data.get('es_admin', False):
                return self.send_json_response({"error": "Acceso denegado"}, 403)

            promocion = controladorPromocion.obtener_promocion_por_id(promocion_id)

            if promocion:
                return self.send_json_response({
                    "success": True,
                    "data": promocion
                })
            else:
                return self.send_json_response({
                    "success": False,
                    "error": "Promoción no encontrada"
                }, 404)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    def api_mis_contenidos_descargas_no_valoradas_handler(self):
        from app.controllers.controlador_contenidos_adquiridos import ControladorContenidosAdquiridos
        user_id = self.get_user_id_from_session()
        if not user_id:
            self.send_json_response({'success': False, 'error': 'No autenticado'}, status_code=401)
            return
        data = self.get_json_body()
        id_contenido = data.get('id_contenido')
        ctrl = ControladorContenidosAdquiridos()
        result = ctrl.obtener_descargas_no_valoradas(user_id, id_contenido)
        self.send_json_response(result)

    def get_user_id_from_session(self):
        cookie = self.headers.get('Cookie', '')
        if not cookie or 'session_id=' not in cookie:
            return None
        session_id = cookie.split('session_id=')[1].split(';')[0]
        session_data = sessions.get(session_id) or sesiones_activas.get(session_id)
        if not session_data or not session_data.get('user_id'):
            return None
        return session_data.get('user_id')

    def get_json_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                return json.loads(post_data.decode('utf-8'))
            except Exception:
                return {}
        return {}

    def api_categoria_arbol_mermaid_handler(self, id_categoria):
        try:
            from app.controllers.controlador_categoria import ControladorCategoria
            ctrl = ControladorCategoria()
            resultado = ctrl.obtener_arbol_mermaid(int(id_categoria))
            return self.send_json_response(resultado)
        except Exception as e:
            return self.send_json_response({"success": False, "error": str(e)}, 500)