from infrastructure.utils.router import route_get, route_post, route_put
from app.controllers.controlador_usuarios import ControladorUsuarios
from app.controllers.controlador_clientes import ControladorClientes
from app.controllers.controlador_contenido import ControladorContenido
from app.controllers.controlador_categoria import ControladorCategoria
from app.controllers.controlador_promocion import ControladorPromocion
from domain.entities.contenido import Contenido
from app.interfaces.interfaz_login import InterfazLogin
from app.interfaces.interfaz_registro import InterfazRegistro
from app.interfaces.interfaz_administrar_clientes import InterfazClientes
from app.interfaces.interfaz_administrar_contenidos import InterfazAdministrarContenidos
from app.interfaces.interfaz_administrar_promocion import InterfazAdministrarPromocion
from app.interfaces.interfaz_administrar_categorias import InterfazAdministrarCategorias

controladorUsuarios = ControladorUsuarios()
controladorClientes = ControladorClientes()
controladorContenido = ControladorContenido()
controladorCategoria = ControladorCategoria()
controladorPromocion = ControladorPromocion()
interfazLogin = InterfazLogin()
interfazRegistro = InterfazRegistro()
interfazClientes = InterfazClientes()
interfazContenidos = InterfazAdministrarContenidos()
interfazPromocion = InterfazAdministrarPromocion()
interfazCategorias = InterfazAdministrarCategorias()

from http.server import BaseHTTPRequestHandler
from infrastructure.utils.router import routes_get, routes_post
from infrastructure.utils.helpers import responder_html, responder_json

class MyHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/css/') or self.path.startswith('/html/') or self.path.startswith('/js/'):
            self.servir_archivo_estatico('static' + self.path)
        else:
            # Check exact matches first
            if self.path in routes_get:
                routes_get[self.path](self)
                return
                
            # Check path with query parameters
            path_without_query = self.path.split('?')[0]
            if path_without_query in routes_get:
                routes_get[path_without_query](self)
                return
                
            # Handle specific API routes
            if self.path.startswith('/api/clientes/') and self.path.endswith('/historial'):
                try:
                    id_usuario = int(self.path.split('/')[3])
                    obtener_historial_cliente(self, id_usuario)
                except Exception as e:
                    responder_json(self, {"error": str(e)}, 500)
            elif self.path.startswith('/api/promociones/') and self.path.endswith('/contenidos'):
                try:
                    id_promocion = int(self.path.split('/')[3])
                    obtener_contenidos_promocion(self, id_promocion)
                except Exception as e:
                    responder_json(self, {"error": str(e)}, 500)
            else:
                self.not_found()

    def do_POST(self):
        if self.path.startswith('/api/clientes/') and self.path.endswith('/saldo'):
            try:
                id_usuario = int(self.path.split('/')[3])
                datos = self.leer_json()
                resultado = controladorClientes.actualizar_saldo_cliente(
                    id_usuario,
                    datos['nuevo_saldo']
                )
                responder_json(self, resultado)
            except Exception as e:
                responder_json(self, {"error": str(e)}, 500)
        # Nueva condición para editar promoción
        elif self.path.startswith('/api/promociones/') and self.path.endswith('/editar'):
            try:
                id_promocion = int(self.path.split('/')[3])
                form_data = self.leer_form_data()
                resultado = controladorPromocion.editar_promocion(id_promocion, form_data)
                responder_json(self, resultado)
            except Exception as e:
                responder_json(self, {"success": False, "error": str(e)}, 500)
        else:
            handler_func = routes_post.get(self.path)
            if handler_func:
                handler_func(self)
            else:
                self.not_found()

    def leer_json(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        import json
        return json.loads(post_data)

    def leer_form_data(self):
        print("Reading form data...")  # Debug
        content_type = self.headers.get('Content-Type')
        if not content_type:
            raise Exception("Content-Type header is required")

        boundary = None
        if 'boundary=' in content_type:
            boundary = content_type.split('boundary=')[1]
        if not boundary:
            raise Exception("Invalid Content-Type header")

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            raise Exception("Content-Length header is required")

        body = self.rfile.read(content_length)
        print(f"Read body of length: {len(body)}")  # Debug

        parts = body.split(b'--' + boundary.encode())
        print(f"Found {len(parts)} parts")  # Debug

        form_data = {}

        for part in parts:
            if not part.strip():
                continue

            headers, _, content = part.partition(b'\r\n\r\n')
            print(f"Processing part with headers: {headers.decode()}")  # Debug

            headers = headers.decode()
            header_lines = headers.split('\r\n')

            content_disposition = None
            content_type = None

            for line in header_lines:
                if line.lower().startswith('content-disposition:'):
                    content_disposition = line
                elif line.lower().startswith('content-type:'):
                    content_type = line

            if content_disposition:
                name = None
                filename = None

                for param in content_disposition.split(';')[1:]:
                    param = param.strip()
                    if param.startswith('name='):
                        name = param.split('=')[1].strip('"')
                    elif param.startswith('filename='):
                        filename = param.split('=')[1].strip('"')

                if name:
                    if filename:
                        print(f"Found file upload: {filename}")  # Debug
                        # Create a proper file-like object with the content
                        class FileObject:
                            def __init__(self, content, filename, content_type=None):
                                self.content = content
                                self.filename = filename
                                self.content_type = content_type.split(':', 1)[1].strip() if content_type else None
                                self.size = len(content)
                                
                            def read(self, size=-1):
                                # Return the entire content regardless of size for simplicity
                                return self.content
                                
                            def __len__(self):
                                return self.size
                                
                        form_data[name] = FileObject(content, filename, content_type)
                    else:
                        print(f"Found form field: {name}={content.decode().strip()}")  # Debug
                        form_data[name] = content.decode().strip()

        print("Form data parsed successfully")  # Debug
        return form_data

    def servir_archivo_estatico(self, ruta_archivo):
        try:
            if ruta_archivo.endswith('.css'):
                content_type = 'text/css'
            elif ruta_archivo.endswith('.js'):
                content_type = 'application/javascript'
            elif ruta_archivo.endswith('.html'):
                content_type = 'text/html'
            else:
                content_type = 'application/octet-stream'

            with open(ruta_archivo, 'rb') as f:
                contenido = f.read()

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(contenido)

        except FileNotFoundError:
            self.not_found()

    def not_found(self):
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')

@route_get('/')
def mostrar_formulario_login(handler):
    contenido = interfazLogin.mostrar_formulario()
    responder_html(handler, contenido)

@route_get('/registro')
def mostrar_formulario_registro(handler):
    contenido = interfazRegistro.mostrar_formulario()
    responder_html(handler, contenido)

@route_post('/api/login')
def autenticar_usuario(handler):
    try:
        datos = handler.leer_json()
        resultado = controladorUsuarios.autenticar_usuario(datos)
        # Devolver éxito y redirigir al frontend
        return responder_json(handler, {
            "success": True,
            "redirect": "/promociones"
        })
    except Exception as e:
        return responder_json(handler, {
            "success": False,
            "error": str(e)
        }, 400)

@route_post('/api/registro')
def registrar_usuario(handler):
    try:
        datos = handler.leer_json()
        resultado = controladorUsuarios.registrar_usuario(datos)
        html = interfazRegistro.mostrar_bienvenida({
            "mensaje": resultado["mensaje"],
            "usuario": {
                "nombre": resultado["nombre"],
                "apellido": resultado["apellido"]
            }
        })
        responder_html(handler, html)
    except Exception as e:
        html = interfazRegistro.mostrar_error(str(e))
        responder_html(handler, html)

@route_get('/clientes')
def mostrar_interfaz_clientes(handler):
    contenido = interfazClientes.mostrar_interfaz()
    responder_html(handler, contenido)

@route_get('/api/clientes')
def obtener_clientes(handler):
    try:
        clientes = controladorClientes.obtener_todos_clientes()
        responder_json(handler, clientes)
    except Exception as e:
        responder_json(handler, {"error": str(e)}, status_code=500)

@route_get('/api/clientes/buscar')
def buscar_clientes(handler):
    try:
        termino = handler.headers.get('Search-Term', '')
        clientes = controladorClientes.buscar_clientes(termino)
        responder_json(handler, clientes)
    except Exception as e:
        responder_json(handler, {"error": str(e)}, 500)

@route_get('/api/clientes/<int:id_usuario>/historial')
def obtener_historial_cliente(handler, id_usuario):
    try:
        historial = controladorClientes.obtener_historial_cliente(id_usuario)
        responder_json(handler, historial)
    except Exception as e:
        responder_json(handler, {"error": str(e)}, 500)

@route_post('/api/clientes/<int:id_usuario>/saldo')
def actualizar_saldo_cliente(handler, id_usuario):
    try:
        datos = handler.leer_json()
        resultado = controladorClientes.actualizar_saldo_cliente(
            id_usuario,
            datos['nuevo_saldo']
        )
        responder_json(handler, resultado)
    except Exception as e:
        responder_json(handler, {"error": str(e)}, status_code=500)

@route_get('/contenidos')
def mostrar_interfaz_contenidos(handler):
    contenido = interfazContenidos.mostrar_interfaz()
    responder_html(handler, contenido)



@route_post('/api/contenidos/agregar_contenido')
def agregar_contenido(handler):
    print("\n=== Inicio de agregar_contenido ===")
    try:
        print("Leyendo datos del formulario...")
        form_data = handler.leer_form_data()
        print(f"Datos del formulario recibidos: {list(form_data.keys())}")
        print(f"Valor de categoria_id: {form_data.get('categoria_id', 'No encontrado')}")
        
        # Verificar que se proporcionó un archivo
        if 'archivo' not in form_data:
            print("Error: No se encontró el archivo en los datos del formulario")
            return responder_json(handler, {"success": False, "error": "No se proporcionó ningún archivo"}, status_code=400)
        
        # Verificar que se proporcionó un ID de categoría
        if 'categoria_id' not in form_data or not form_data['categoria_id']:
            print("Error: No se proporcionó un ID de categoría")
            return responder_json(handler, {"success": False, "error": "Debe seleccionar una categoría"}, status_code=400)
            
        print("Procesando archivo...")
        try:
            # Obtener el objeto de archivo de form_data
            file_obj = form_data['archivo']
            
            # Leer el contenido del archivo
            if hasattr(file_obj, 'read'):
                file_content = file_obj.read()
                file_name = getattr(file_obj, 'filename', 'archivo')
                file_size = getattr(file_obj, 'size', len(file_content))
            else:
                file_content = b''
                file_name = 'archivo'
                file_size = 0
            
            print(f"Archivo leído: {file_name}, tamaño: {len(file_content)} bytes")
                
            # Crear la estructura de archivo procesado
            form_data['archivo'] = {
                'nombre': file_name,
                'contenido': file_content,
                'tamano': file_size
            }
        except Exception as e:
            print(f"Error al procesar el archivo: {str(e)}")
            return responder_json(handler, {"success": False, "error": f"Error al procesar el archivo: {str(e)}"}, status_code=400)
            
        print("Procesando datos con el controlador...")
        resultado = controladorContenido.manejar_agregar_contenido(form_data)
        print(f"Resultado del controlador: {resultado}")
        
        return responder_json(handler, resultado)
    except Exception as e:
        print(f"Error en agregar_contenido: {str(e)}")
        import traceback
        traceback.print_exc()
        return responder_json(handler, {"success": False, "error": str(e)}, status_code=500)

@route_get('/api/contenidos')
def obtener_contenidos(handler):
    try:
        print("Obteniendo lista de contenidos...")
        contenidos = controladorContenido.obtener_contenidos()
        print(f"Contenidos obtenidos: {len(contenidos)} items")
        return responder_json(handler, {"success": True, "data": contenidos})
    except Exception as e:
        print(f"Error en obtener_contenidos: {str(e)}")
        return responder_json(handler, {"success": False, "error": str(e)}, status_code=500)

@route_get('/api/contenido')
def obtener_contenido(handler):
    try:
        id_contenido = int(handler.path.split('=')[1])
        print(f"Obteniendo contenido con ID: {id_contenido}")
        contenido = controladorContenido.obtener_contenido(id_contenido)
        if not contenido:
            return responder_json(handler, {"success": False, "error": "Contenido no encontrado"}, status_code=404)
        return responder_json(handler, {"success": True, "contenido": contenido})
    except Exception as e:
        print(f"Error al obtener contenido: {str(e)}")
        return responder_json(handler, {"success": False, "error": str(e)}, status_code=500)

@route_post('/api/contenidos/editar')
def editar_contenido_handler(handler):
    try:
        # Leer los datos del formulario (esto incluye archivos si los hay)
        form_data = handler.leer_form_data()
        
        # Verificar si se envió un archivo
        file_item = form_data.get('archivo')
        file_data = None
        file_size = 0
        
        if file_item and hasattr(file_item, 'file'):
            # Leer el contenido del archivo
            file_data = file_item.file.read()
            file_size = len(file_data)
            # Agregar la información del archivo al form_data
            form_data['archivo'] = file_data
            form_data['tamano_archivo'] = file_size
        
        id_contenido = int(form_data.get('contenido_id'))
        print(f"Editando contenido con ID: {id_contenido}")
        
        # Llamar al controlador con los datos del formulario
        resultado = controladorContenido.manejar_editar_contenido(id_contenido, form_data)
        
        if resultado.get('success'):
            return responder_json(handler, resultado)
        else:
            return responder_json(handler, resultado, status_code=400)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error al editar contenido: {str(e)}\n{error_details}")
        return responder_json(handler, {"success": False, "error": str(e)}, status_code=500)

@route_post('/api/contenidos/eliminar')
def eliminar_contenido_handler(handler):
    try:
        # Leer el cuerpo de la petición directamente
        content_length = int(handler.headers.get('Content-Length', 0))
        post_data = handler.rfile.read(content_length).decode('utf-8')
        
        print(f"Datos recibidos: {post_data}")  # Debug
        
        # Parsear los datos del formulario codificados en URL
        from urllib.parse import parse_qs
        form_data = parse_qs(post_data)
        
        # Obtener el ID del contenido
        id_contenido = form_data.get('contenido_id', [None])[0]
        
        if not id_contenido:
            return responder_json(handler, {
                "success": False, 
                "error": "Se requiere el ID del contenido"
            }, status_code=400)
            
        try:
            id_contenido = int(id_contenido)
        except (ValueError, TypeError):
            return responder_json(handler, {
                "success": False, 
                "error": "ID de contenido no válido"
            }, status_code=400)
        
        print(f"Eliminando contenido con ID: {id_contenido}")
        
        # Verificar si el contenido existe antes de intentar eliminarlo
        contenido_existente = controladorContenido.obtener_contenido(id_contenido)
        if not contenido_existente:
            return responder_json(handler, {
                "success": False,
                "error": f"No se encontró el contenido con ID {id_contenido}"
            }, status_code=404)
        
        # Intentar eliminar el contenido
        resultado = controladorContenido.eliminar_contenido(id_contenido)
        
        if resultado.get('success'):
            print(f"Contenido {id_contenido} eliminado exitosamente")
            return responder_json(handler, {
                "success": True,
                "message": "Contenido eliminado correctamente"
            })
        else:
            error_msg = resultado.get('error', 'Error desconocido al eliminar el contenido')
            print(f"Error al eliminar contenido {id_contenido}: {error_msg}")
            return responder_json(handler, {
                "success": False,
                "error": error_msg
            }, status_code=400)
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"Error inesperado al eliminar contenido: {str(e)}"
        print(f"{error_msg}\n{error_details}")
        return responder_json(handler, {
            "success": False,
            "error": "Ocurrió un error al procesar la solicitud"
        }, status_code=500)

@route_get('/obtener_contenidos')
def obtener_contenidos_legacy(handler):
    try:
        print("Obteniendo lista de contenidos (legacy endpoint)...")
        contenidos = controladorContenido.obtener_contenidos()
        print(f"Contenidos obtenidos (legacy): {len(contenidos)} items")
        return responder_json(handler, {"success": True, "data": contenidos})
    except Exception as e:
        print(f"Error en obtener_contenidos_legacy: {str(e)}")
        return responder_json(handler, {"success": False, "error": str(e)}, status_code=500)



@route_get('/api/contenidos/categorias')
def obtener_categorias_contenido(handler):
    try:
        categorias = controladorCategoria.obtener_todas_categorias()
        responder_json(handler, categorias)
    except Exception as e:
        responder_json(handler, {"error": str(e)}, status_code=500)

@route_get('/promociones')
def mostrar_interfaz_promociones(handler):
    contenido = interfazPromocion.mostrar_interfaz()
    responder_html(handler, contenido)

@route_get('/obtener_promociones')
def obtener_promociones(handler):
    try:
        promociones = controladorPromocion.obtener_todas_promociones()
        responder_json(handler, {"success": True, "promociones": promociones})
    except Exception as e:
        responder_json(handler, {"success": False, "error": str(e)}, 500)

@route_get('/obtener_promocion')
def obtener_promocion(handler):
    try:
        from urllib.parse import parse_qs, urlparse
        query_components = parse_qs(urlparse(handler.path).query)
        id_promocion = int(query_components.get('id', [None])[0])
        
        if not id_promocion:
            return responder_json(handler, {"success": False, "error": "ID de promoción no proporcionado"}, 400)
        
        print(f"Buscando promoción con ID: {id_promocion}")
        promocion = controladorPromocion.obtener_promocion_por_id(id_promocion)
        
        if promocion:
            print(f"Promoción encontrada: {promocion}")
            # Asegurarnos de que los contenidos estén en el formato correcto
            if 'contenidos' not in promocion:
                promocion['contenidos'] = []
            # Asegurarse de que las fechas estén en el formato correcto
            if 'fecha_inicio' in promocion and promocion['fecha_inicio']:
                if isinstance(promocion['fecha_inicio'], str):
                    from datetime import datetime
                    try:
                        fecha = datetime.strptime(promocion['fecha_inicio'], '%Y-%m-%d %H:%M:%S')
                        promocion['fecha_inicio'] = fecha.strftime('%Y-%m-%dT%H:%M')
                    except ValueError:
                        pass
            if 'fecha_fin' in promocion and promocion['fecha_fin']:
                if isinstance(promocion['fecha_fin'], str):
                    from datetime import datetime
                    try:
                        fecha = datetime.strptime(promocion['fecha_fin'], '%Y-%m-%d %H:%M:%S')
                        promocion['fecha_fin'] = fecha.strftime('%Y-%m-%dT%H:%M')
                    except ValueError:
                        pass
            responder_json(handler, {"success": True, "promocion": promocion})
        else:
            print(f"Promoción con ID {id_promocion} no encontrada")
            responder_json(handler, {"success": False, "error": "Promoción no encontrada"}, 404)
            print(f"Promoción con ID {id_promocion} no encontrada")
            responder_json(handler, {"success": False, "error": "Promoción no encontrada"}, 404)
    except Exception as e:
        import traceback
        error_msg = f"Error en obtener_promocion: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        responder_json(handler, {"success": False, "error": "Error al obtener la promoción"}, 500)


@route_get('/api/promociones/<int:id_promocion>/contenidos')
def obtener_contenidos_promocion(handler, id_promocion):
    try:
        print(f"Buscando contenidos para promoción ID: {id_promocion}")
        promocion = controladorPromocion.obtener_promocion_por_id(id_promocion)

        if not promocion:
            print(f"Promoción con ID {id_promocion} no encontrada")
            return responder_json(handler, {"success": False, "error": "Promoción no encontrada"}, 404)

        print(f"Contenidos encontrados: {promocion.get('contenidos', [])}")

        responder_json(handler, {
            "success": True,
            "contenidos": promocion.get("contenidos", []),
            "promocion": {
                "porcentaje": promocion.get("porcentaje", 0)
            }
        })
    except Exception as e:
        import traceback
        error_msg = f"Error en obtener_contenidos_promocion: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        responder_json(handler, {"success": False, "error": "Error al obtener los contenidos de la promoción"}, 500)

@route_post('/agregar_promocion')
def agregar_promocion(handler):
    try:
        form_data = handler.leer_form_data()
        resultado = controladorPromocion.agregar_promocion(form_data)
        responder_json(handler, resultado)
    except Exception as e:
        responder_json(handler, {"success": False, "error": str(e)}, 500)

@route_post('/api/promociones/<int:id_promocion>/editar')
def editar_promocion(handler, id_promocion):
    try:
        form_data = handler.leer_form_data()
        resultado = controladorPromocion.editar_promocion(id_promocion, form_data)
        responder_json(handler, resultado)
    except Exception as e:
        responder_json(handler, {"success": False, "error": str(e)}, 500)

@route_post('/eliminar_promocion')
def eliminar_promocion(handler):
    try:
        form_data = handler.leer_form_data()
        id_promocion = int(form_data.get('promocion_id'))
        resultado = controladorPromocion.eliminar_promocion(id_promocion)
        responder_json(handler, resultado)
    except Exception as e:
        responder_json(handler, {"success": False, "error": str(e)}, 500)

@route_get('/categorias')
def mostrar_interfaz_categorias(handler):
    contenido = interfazCategorias.mostrar_interfaz()
    responder_html(handler, contenido)

@route_get('/api/categorias')
def obtener_todas_categorias(handler):
    try:
        categorias = controladorCategoria.obtener_todas_categorias()
        responder_json(handler, categorias)
    except Exception as e:
        responder_json(handler, {"error": str(e)}, status_code=500)

@route_post('/api/categorias')
def crear_categoria(handler):
    try:
        datos = handler.leer_json()
        resultado = controladorCategoria.crear_categoria(
            datos['nombre'],
            datos.get('id_categoria_padre')
        )
        responder_json(handler, {
            "message": "Categoría creada exitosamente",
            "categoria": resultado
        })
    except Exception as e:
        responder_json(handler, {"error": str(e)}, 500)

@route_put('/api/categorias/<int:id_categoria>')
def actualizar_categoria(handler, id_categoria):
    try:
        datos = handler.leer_json()
        resultado = controladorCategoria.actualizar_categoria(
            id_categoria,
            datos['nombre']
        )
        responder_json(handler, {
            "message": "Categoría actualizada exitosamente",
            "categoria": resultado
        })
    except Exception as e:
        responder_json(handler, {"error": str(e)}, 500)

@route_get('/api/categorias/buscar')
def buscar_categorias(handler):
    try:
        termino = handler.headers.get('Search-Term', '')
        categorias = controladorCategoria.buscar_categorias(termino)
        responder_json(handler, categorias)
    except Exception as e:
        responder_json(handler, {"error": str(e)}, 500)