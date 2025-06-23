from functools import wraps
from http import HTTPStatus
from infrastructure.utils.helpers import responder_json

# ROUTE-001: Módulo para manejo de rutas y autenticación

# Diccionarios para almacenar las rutas
routes_get = {}
routes_post = {}
routes_put = {}
routes_delete = {}

# Diccionario para almacenar sesiones de usuario
sessions = {}


class UnauthorizedError(Exception):
    pass


class ForbiddenError(Exception):
    pass


# ROUTE-AUTH-001: Obtiene el usuario actual basado en la sesión
def obtener_usuario_actual(handler):
    cookie = handler.headers.get('Cookie', '')
    if not cookie or 'session_id=' not in cookie:
        return None

    session_id = cookie.split('session_id=')[1].split(';')[0]
    return sessions.get(session_id)


# ROUTE-AUTH-002: Decorador para rutas que requieren autenticación
def requiere_autenticacion(func):
    @wraps(func)
    def wrapper(handler, *args, **kwargs):
        usuario = obtener_usuario_actual(handler)
        if not usuario:
            handler.send_response(HTTPStatus.UNAUTHORIZED)
            responder_json(handler, {"error": "Se requiere autenticación"})
            return
        return func(handler, *args, **kwargs)

    return wrapper


# ROUTE-AUTH-003: Decorador para rutas que requieren un rol específico
def requiere_rol(rol_requerido):
    def decorator(func):
        @wraps(func)
        def wrapper(handler, *args, **kwargs):
            usuario = obtener_usuario_actual(handler)
            if not usuario:
                handler.send_response(HTTPStatus.UNAUTHORIZED)
                responder_json(handler, {"error": "Se requiere autenticación"})
                return

            from domain.entities.administrador import Administrador
            es_admin = bool(Administrador.buscar_por_username(usuario['username']))

            if rol_requerido == 'admin' and not es_admin:
                handler.send_response(HTTPStatus.FORBIDDEN)
                responder_json(handler, {"error": "Se requieren permisos de administrador"})
                return

            return func(handler, *args, **kwargs)

        return wrapper

    return decorator


# ROUTE-GET-001: Decorador para registrar rutas GET
def route_get(path, auth_required=False, roles=None):
    def decorator(func):
        @wraps(func)
        def wrapper(handler, *args, **kwargs):
            if auth_required:
                usuario = obtener_usuario_actual(handler)
                if not usuario:
                    handler.send_response(HTTPStatus.UNAUTHORIZED)
                    responder_json(handler, {"error": "Se requiere autenticación"})
                    return

                if roles:
                    from domain.entities.administrador import Administrador
                    es_admin = bool(Administrador.buscar_por_username(usuario['username']))
                    if 'admin' in roles and not es_admin:
                        handler.send_response(HTTPStatus.FORBIDDEN)
                        responder_json(handler, {"error": "Se requieren permisos de administrador"})
                        return

            return func(handler, *args, **kwargs)

        routes_get[path] = wrapper
        return func

    return decorator


# ROUTE-POST-001: Decorador para registrar rutas POST
def route_post(path, auth_required=False, roles=None):
    def decorator(func):
        @wraps(func)
        def wrapper(handler, *args, **kwargs):
            if auth_required:
                usuario = obtener_usuario_actual(handler)
                if not usuario:
                    handler.send_response(HTTPStatus.UNAUTHORIZED)
                    responder_json(handler, {"error": "Se requiere autenticación"})
                    return

                if roles:
                    from domain.entities.administrador import Administrador
                    es_admin = bool(Administrador.buscar_por_username(usuario['username']))
                    if 'admin' in roles and not es_admin:
                        handler.send_response(HTTPStatus.FORBIDDEN)
                        responder_json(handler, {"error": "Se requieren permisos de administrador"})
                        return

            return func(handler, *args, **kwargs)

        routes_post[path] = wrapper
        return func

    return decorator


# ROUTE-PUT-001: Decorador para registrar rutas PUT
def route_put(path, auth_required=False, roles=None):
    def decorator(func):
        @wraps(func)
        def wrapper(handler, *args, **kwargs):
            if auth_required:
                usuario = obtener_usuario_actual(handler)
                if not usuario:
                    handler.send_response(HTTPStatus.UNAUTHORIZED)
                    responder_json(handler, {"error": "Se requiere autenticación"})
                    return

                if roles and usuario.get('rol') not in roles:
                    handler.send_response(HTTPStatus.FORBIDDEN)
                    responder_json(handler, {"error": "No tiene permisos para acceder a este recurso"})
                    return

            return func(handler, *args, **kwargs)

        routes_put[path] = wrapper
        return wrapper

    return decorator


# ROUTE-DELETE-001: Decorador para registrar rutas DELETE
def route_delete(path, auth_required=False, roles=None):
    def decorator(func):
        @wraps(func)
        def wrapper(handler, *args, **kwargs):
            if auth_required:
                usuario = obtener_usuario_actual(handler)
                if not usuario:
                    handler.send_response(HTTPStatus.UNAUTHORIZED)
                    responder_json(handler, {"error": "Se requiere autenticación"})
                    return
                if roles and usuario.get('rol') not in roles:
                    handler.send_response(HTTPStatus.FORBIDDEN)
                    responder_json(handler, {"error": "No tiene permisos para acceder a este recurso"})
                    return
            return func(handler, *args, **kwargs)

        routes_delete[path] = wrapper
        return wrapper

    return decorator