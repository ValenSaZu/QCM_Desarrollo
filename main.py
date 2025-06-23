from http.server import HTTPServer
from handler import MyHandler

# SERVER-001: Configuración e inicio del servidor HTTP

# SERVER-RUN-001: Inicia y ejecuta el servidor web
def run():
    server_address = ('', 8000)  # Escucha en todas las interfaces
    httpd = HTTPServer(server_address, MyHandler)
    print('Servidor iniciado en http://localhost:8000')
    httpd.serve_forever()

if __name__ == '__main__':
    run()