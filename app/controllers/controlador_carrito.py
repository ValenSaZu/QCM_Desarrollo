from domain.entities.carrito import Carrito

# G-006: Controlador para gestionar operaciones del carrito de compras:
# - Obtener contenido del carrito
# - Agregar/eliminar contenidos
# - Vaciar carrito
# - Procesar compra
# - Calcular totales y aplicar descuentos
class ControladorCarrito:
    # CTRL-CARR-001: Obtiene todos los items del carrito de un usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario cuyo carrito se consulta
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "items": list[dict] (detalle de cada contenido),
    #       "total": float (suma total con descuentos aplicados)
    #   }
    # Excepciones:
    #   Exception: Si ocurre algún error al acceder a la base de datos
    def obtener_carrito(self, id_usuario):
        try:
            carrito, descuento_aplicado = Carrito.obtener_carrito_por_usuario(id_usuario)

            if not carrito:
                return {
                    "success": True,
                    "items": [],
                    "total": 0.0
                }

            items = []
            total = 0.0

            for contenido in carrito:
                tipo_contenido = self._determinar_tipo_contenido(
                    contenido.formato if hasattr(contenido, 'formato') else 'imagen')
                precio_final = float(contenido.precio_con_descuento) if hasattr(contenido,
                                                                                'precio_con_descuento') else float(
                    contenido.precio_original)

                item = {
                    "id": contenido.id_contenido,
                    "nombre": contenido.nombre,
                    "autor": contenido.autor,
                    "descripcion": contenido.descripcion,
                    "precio_original": float(contenido.precio_original),
                    "precio_final": precio_final,
                    "cantidad": contenido.cantidad,
                    "tipo": tipo_contenido,
                    "descuento_aplicado": hasattr(contenido,
                                                  'precio_con_descuento') and contenido.precio_con_descuento < contenido.precio_original
                }

                items.append(item)
                total += precio_final * contenido.cantidad

            return {
                "success": True,
                "items": items,
                "total": total
            }

        except Exception as e:
            raise Exception(f"Error al obtener el carrito: {str(e)}")

    # CTRL-CARR-002: Determina el tipo de contenido (imagen/video/audio)
    # basado en su formato de archivo
    # Parámetros:
    #   formato (str): Extensión o tipo de archivo (ej: 'mp4', 'jpg')
    # Retorna:
    #   str: 'imagen', 'video' o 'audio' (default: 'imagen')
    def _determinar_tipo_contenido(self, formato):
        if not formato:
            return 'imagen'

        formato_lower = formato.lower()
        if 'imagen' in formato_lower or 'jpg' in formato_lower or 'png' in formato_lower or 'gif' in formato_lower:
            return 'imagen'
        elif 'video' in formato_lower or 'mp4' in formato_lower or 'avi' in formato_lower or 'mov' in formato_lower:
            return 'video'
        elif 'audio' in formato_lower or 'mp3' in formato_lower or 'wav' in formato_lower or 'ogg' in formato_lower:
            return 'audio'
        else:
            return 'imagen'

    # CTRL-CARR-003: Elimina todos los contenidos del carrito de un usuario
    # Parámetros:
    #   id_usuario (int): ID del usuario cuyo carrito se vaciará
    # Retorna:
    #   dict: {"success": bool, "message": str}
    # Excepciones:
    #   Exception: Si ocurre error al vaciar el carrito
    def vaciar_carrito(self, id_usuario):
        try:
            Carrito.vaciar_carrito(id_usuario)
            return {
                "success": True,
                "message": "Carrito vaciado correctamente"
            }
        except Exception as e:
            raise Exception(f"Error al vaciar el carrito: {str(e)}")

    # CTRL-CARR-004: Agrega un contenido al carrito con cantidad especificada
    # Parámetros:
    #   id_usuario (int): ID del usuario dueño del carrito
    #   id_contenido (int): ID del contenido a agregar
    #   cantidad (int): Cantidad a agregar (default: 1)
    # Retorna:
    #   dict: {"success": bool, "message": str}
    # Excepciones:
    #   Exception: Si no se puede agregar el contenido
    def agregar_contenido(self, id_usuario, id_contenido, cantidad=1):
        try:
            Carrito.agregar_contenido(id_usuario, id_contenido, cantidad)
            return {
                "success": True,
                "message": "Contenido agregado al carrito correctamente"
            }
        except Exception as e:
            raise Exception(f"Error al agregar contenido al carrito: {str(e)}")

    # CTRL-CARR-005: Elimina un contenido específico del carrito
    # Parámetros:
    #   id_usuario (int): ID del usuario dueño del carrito
    #   id_contenido (int): ID del contenido a eliminar
    # Retorna:
    #   dict: {"success": bool, "message": str/error}
    def eliminar_contenido(self, id_usuario, id_contenido):
        try:
            Carrito.eliminar_contenido(id_usuario, id_contenido)
            return {
                "success": True,
                "message": "Contenido eliminado del carrito correctamente"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # CTRL-CARR-006: Realiza el checkout del carrito:
    # 1. Valida que el carrito no esté vacío
    # 2. Calcula el total de la compra
    # 3. Registra la transacción
    # 4. Vacía el carrito
    # Parámetros:
    #   id_usuario (int): ID del usuario que realiza la compra
    # Retorna:
    #   dict: {"success": bool, "message": str/error}
    def procesar_compra(self, id_usuario):
        try:
            items_a_comprar, _ = Carrito.obtener_carrito_por_usuario(id_usuario)
            if not items_a_comprar:
                return {"success": False, "error": "El carrito está vacío"}

            total_compra = sum(
                item.precio_con_descuento * item.cantidad
                for item in items_a_comprar
            )

            Carrito.registrar_compra_y_vaciar_carrito(
                id_usuario,
                items_a_comprar,
                total_compra
            )

            return {
                "success": True,
                "message": "Compra realizada exitosamente"
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al procesar compra: {str(e)}"
            }