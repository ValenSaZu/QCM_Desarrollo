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
    from infrastructure.bd.conexion import obtener_conexion

    extension = nombre_archivo.split('.')[-1].lower()
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
                       SELECT id_tipo_archivo, formato, mime_type
                       FROM TIPO_ARCHIVO
                       WHERE extension = %s
                       """, (extension,))

        tipo_archivo = cursor.fetchone()
        if not tipo_archivo:
            raise Exception(f"Tipo de archivo no soportado: {extension}")

        return {
            "id": tipo_archivo[0],
            "formato": tipo_archivo[1],
            "mime_type": tipo_archivo[2]
        }
    finally:
        cursor.close()
        conexion.close()