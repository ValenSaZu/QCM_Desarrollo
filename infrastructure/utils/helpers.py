import json
# Para aayudar con las funcionidades base de hanler.py

# Para mostrar un html en el navegador
def responder_html(handler, contenido_html):
    handler.send_response(200)
    handler.send_header('Content-Type', 'text/html')
    handler.end_headers()
    handler.wfile.write(contenido_html.encode())

# Para enviar datos al fetch de JS y poder usarlos para mostrarlos en el navegador
def responder_json(handler, data, status_code=200, is_array=False):
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json')
    # Permitir solicitudes desde cualquier origen durante el desarrollo
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    handler.send_header('Access-Control-Allow-Credentials', 'true')
    handler.send_header('Vary', 'Origin')
    handler.end_headers()
    
    # Si se solicita una respuesta de matriz directa, devolver la lista como está
    if is_array and isinstance(data, list):
        handler.wfile.write(json.dumps(data, default=str).encode('utf-8'))
        return
        
    # Si los datos ya son un diccionario con una estructura de respuesta estándar, los enviamos tal cual
    if isinstance(data, dict) and ('success' in data or 'error' in data or 'data' in data):
        pass
    # Si es una lista, la enviamos en un campo 'data' con success: true
    elif isinstance(data, list):
        data = {'success': True, 'data': data}
    # Para cualquier otro caso, lo enviamos en un campo 'data' con success: true
    else:
        data = {'success': True, 'data': data}
    
    # Aseguramos que siempre haya un campo 'data' para consistencia
    if 'data' not in data and data.get('success') is not False:
        data['data'] = data.get('data', [])
    
    handler.wfile.write(json.dumps(data, default=str).encode('utf-8'))
