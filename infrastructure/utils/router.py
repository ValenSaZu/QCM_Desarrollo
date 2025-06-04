routes_get = {}
routes_post = {}
routes_put = {}

# Para generar las APIREST de modo que no necesitamos una clase con mil if de GET y POST en handler.py

def route_get(path):
    def decorator(func):
        routes_get[path] = func
        return func
    return decorator

def route_post(path):
    def decorator(func):
        routes_post[path] = func
        return func
    return decorator

def route_put(path):
    def decorator(func):
        routes_put[path] = func
        return func
    return decorator
