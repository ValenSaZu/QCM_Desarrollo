from http.server import HTTPServer
from handler import MyHandler

def run():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHandler)
    print('Servidor corriendo en http://localhost:8000')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
