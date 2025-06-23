from functools import wraps
from http import HTTPStatus
from infrastructure.utils.helpers import responder_json

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

def obtener_usuario_actual(handler):
    """Obtiene el usuario actual basado en la cookie de sesión"""
    cookie = handler.headers.get('Cookie', '')
    if not cookie or 'session_id=' not in cookie:
        return None
    
    session_id = cookie.split('session_id=')[1].split(';')[0]
    return sessions.get(session_id)

def requiere_autenticacion(func):
    """Decorador para rutas que requieren autenticación"""
    @wraps(func)
    def wrapper(handler, *args, **kwargs):
        usuario = obtener_usuario_actual(handler)
        if not usuario:
            handler.send_response(HTTPStatus.UNAUTHORIZED)
            responder_json(handler, {"error": "Se requiere autenticación"})
            return
        return func(handler, *args, **kwargs)
    return wrapper

def requiere_rol(rol_requerido):
    """Decorador para rutas que requieren un rol específico"""
    def decorator(func):
        @wraps(func)
        def wrapper(handler, *args, **kwargs):
            usuario = obtener_usuario_actual(handler)
            if not usuario:
                handler.send_response(HTTPStatus.UNAUTHORIZED)
                responder_json(handler, {"error": "Se requiere autenticación"})
                return
                
            # Verificar si el usuario es administrador
            from domain.entities.administrador import Administrador
            es_admin = bool(Administrador.buscar_por_username(usuario['username']))
            
            if rol_requerido == 'admin' and not es_admin:
                handler.send_response(HTTPStatus.FORBIDDEN)
                responder_json(handler, {"error": "Se requieren permisos de administrador"})
                return
                
            return func(handler, *args, **kwargs)
        return wrapper
    return decorator

def route_get(path, auth_required=False, roles=None):
    """Decorador para rutas GET"""
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

def route_post(path, auth_required=False, roles=None):
    """Decorador para rutas POST"""
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

def route_put(path, auth_required=False, roles=None):
    """Decorador para rutas PUT"""
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

def route_delete(path, auth_required=False, roles=None):
    """Decorador para rutas DELETE"""
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
        
        # Registrar la ruta
        routes_delete[path] = wrapper
        return wrapper
    return decorator
