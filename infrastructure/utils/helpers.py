import json
# Para aayudar con las funcionidades base de hanler.py

# Para mostrar un html en el navegador
def responder_html(handler, contenido_html):
    handler.send_response(200)
    handler.send_header('Content-Type', 'text/html')
    handler.end_headers()
    handler.wfile.write(contenido_html.encode())

# Para enviar datos al fetch de JS y poder usarlos para mostrarlos en el navegador
def responder_json(handler, data, status_code=200):
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode())
