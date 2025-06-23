import json

# UTIL-002: Funciones utilitarias para manejo de respuestas HTTP

# UTIL-HANDLER-001: Envía una respuesta HTML al cliente
def responder_html(handler, contenido_html):
    handler.send_response(200)
    handler.send_header('Content-Type', 'text/html')
    handler.end_headers()
    handler.wfile.write(contenido_html.encode())


# UTIL-HANDLER-002: Envía una respuesta JSON estandarizada al cliente
def responder_json(handler, data, status_code=200, is_array=False):
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    handler.send_header('Access-Control-Allow-Credentials', 'true')
    handler.send_header('Vary', 'Origin')
    handler.end_headers()

    if is_array and isinstance(data, list):
        handler.wfile.write(json.dumps(data, default=str).encode('utf-8'))
        return

    if isinstance(data, dict) and ('success' in data or 'error' in data or 'data' in data):
        pass
    elif isinstance(data, list):
        data = {'success': True, 'data': data}
    else:
        data = {'success': True, 'data': data}

    if 'data' not in data and data.get('success') is not False:
        data['data'] = data.get('data', [])

    handler.wfile.write(json.dumps(data, default=str).encode('utf-8'))