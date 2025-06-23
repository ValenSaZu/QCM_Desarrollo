def procesar_archivo(archivo):
    try:
        contenido = archivo.read()

        return {
            'nombre': archivo.filename,
            'contenido': contenido,
            'tamano': len(contenido)
        }
    except Exception as e:
        raise Exception(f"Error al procesar archivo: {str(e)}")


def determinar_tipo_archivo(nombre_archivo):
    """Determina el tipo de archivo usando la entidad TipoArchivo"""
    try:
        extension = nombre_archivo.split('.')[-1].lower()
        
        # Usar la entidad TipoArchivo
        from domain.entities.tipo_archivo import TipoArchivo
        tipo_archivo = TipoArchivo.obtener_por_extension(extension)
        
        if not tipo_archivo:
            raise Exception(f"Tipo de archivo no soportado: {extension}")

        return {
            "id": tipo_archivo.id_tipo_archivo,
            "formato": tipo_archivo.formato,
            "mime_type": tipo_archivo.mime_type
        }
    except Exception as e:
        raise Exception(f"Error al determinar tipo de archivo: {str(e)}")