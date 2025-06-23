# UTIL-001: Funciones utilitarias para procesamiento de archivos

# UTIL-FILE-001: Procesa un archivo y extrae su información básica
def procesar_archivo(archivo):
    try:
        contenido = archivo.read()
        return {
            'nombre': archivo.filename,
            'contenido': contenido,
            'tamano': len(contenido)
        }
    except Exception:
        raise Exception("Error al procesar archivo")


# UTIL-FILE-002: Determina el tipo de archivo basado en su extensión
def determinar_tipo_archivo(nombre_archivo):
    try:
        extension = nombre_archivo.split('.')[-1].lower()

        from domain.entities.tipo_archivo import TipoArchivo
        tipo_archivo = TipoArchivo.obtener_por_extension(extension)

        if not tipo_archivo:
            raise Exception(f"Tipo de archivo no soportado: {extension}")

        return {
            "id": tipo_archivo.id_tipo_archivo,
            "formato": tipo_archivo.formato,
            "mime_type": tipo_archivo.mime_type
        }
    except Exception:
        raise Exception("Error al determinar tipo de archivo")