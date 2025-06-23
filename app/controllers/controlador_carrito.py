from domain.entities.carrito import Carrito

class ControladorCarrito:
    def obtener_carrito(self, id_usuario):
        """Obtiene los contenidos del carrito de un usuario en formato JSON"""
        try:
            print(f"Obteniendo carrito para usuario ID: {id_usuario}")
            carrito, descuento_aplicado = Carrito.obtener_carrito_por_usuario(id_usuario)
            print(f"Carrito obtenido: {carrito}")
            print(f"Descuento aplicado: {descuento_aplicado}")

            if not carrito:
                print("Carrito vacío, devolviendo respuesta vacía")
                return {
                    "success": True,
                    "items": [],
                    "total": 0.0
                }

            # Convertir a la estructura que espera el frontend
            items = []
            total = 0.0
            
            for contenido in carrito:
                print(f"Procesando contenido: {contenido.__dict__}")
                # Determinar el tipo de contenido basado en el formato
                tipo_contenido = self._determinar_tipo_contenido(contenido.formato if hasattr(contenido, 'formato') else 'imagen')
                print(f"Tipo determinado: {tipo_contenido}")
                
                # Calcular precio final (con descuento si aplica)
                precio_final = float(contenido.precio_con_descuento) if hasattr(contenido, 'precio_con_descuento') else float(contenido.precio_original)
                print(f"Precio final: {precio_final}")
                
                item = {
                    "id": contenido.id_contenido,
                    "nombre": contenido.nombre,
                    "autor": contenido.autor,
                    "descripcion": contenido.descripcion,
                    "precio_original": float(contenido.precio_original),
                    "precio_final": precio_final,
                    "cantidad": contenido.cantidad,
                    "tipo": tipo_contenido,
                    "descuento_aplicado": hasattr(contenido, 'precio_con_descuento') and contenido.precio_con_descuento < contenido.precio_original
                }
                print(f"Item creado: {item}")
                
                items.append(item)
                total += precio_final * contenido.cantidad

            print(f"Total de items: {len(items)}")
            print(f"Total calculado: {total}")
            
            resultado = {
                "success": True,
                "items": items,
                "total": total
            }
            print(f"Resultado final: {resultado}")
            return resultado

        except Exception as e:
            print(f"Error en obtener_carrito: {str(e)}")
            raise Exception(f"Error al obtener el carrito: {str(e)}")

    def _determinar_tipo_contenido(self, formato):
        """Determina el tipo de contenido basado en el formato"""
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
            return 'imagen'  # Por defecto

    def vaciar_carrito(self, id_usuario):
        """Vacía por completo el carrito de un usuario"""
        try:
            Carrito.vaciar_carrito(id_usuario)
            return {
                "success": True,
                "message": "Carrito vaciado correctamente"
            }
        except Exception as e:
            print(f"Error en vaciar_carrito: {str(e)}")
            raise Exception(f"Error al vaciar el carrito: {str(e)}")

    def agregar_contenido(self, id_usuario, id_contenido, cantidad=1):
        """Agrega un contenido al carrito de un usuario"""
        try:
            Carrito.agregar_contenido(id_usuario, id_contenido, cantidad)
            return {
                "success": True,
                "message": "Contenido agregado al carrito correctamente"
            }
        except Exception as e:
            print(f"Error en agregar_contenido: {str(e)}")
            raise Exception(f"Error al agregar contenido al carrito: {str(e)}")

    def eliminar_contenido(self, id_usuario, id_contenido):
        """Maneja la lógica para eliminar un contenido del carrito."""
        try:
            Carrito.eliminar_contenido(id_usuario, id_contenido)
            return {
                "success": True,
                "message": "Contenido eliminado del carrito correctamente"
            }
        except Exception as e:
            print(f"Error en eliminar_contenido (controlador): {str(e)}")
            return {"success": False, "error": str(e)}

    def procesar_compra(self, id_usuario):
        """Maneja la lógica de alto nivel para procesar la compra."""
        try:
            # Obtener los items del carrito para calcular el total
            items_a_comprar, _ = Carrito.obtener_carrito_por_usuario(id_usuario)
            if not items_a_comprar:
                return {"success": False, "error": "El carrito está vacío."}
            
            # Calcular el total usando los precios con descuento (ya corregidos para promociones activas)
            total_compra = sum(item.precio_con_descuento * item.cantidad for item in items_a_comprar)

            # Llamar al método transaccional de la entidad
            Carrito.registrar_compra_y_vaciar_carrito(id_usuario, items_a_comprar, total_compra)
            
            return {
                "success": True,
                "message": "¡Compra realizada con éxito! Tus contenidos ya están en 'Mis Contenidos'."
            }
        except ValueError as ve: # Captura errores específicos como "Saldo insuficiente"
             return {"success": False, "error": str(ve)}
        except Exception as e:
            print(f"Error en procesar_compra (controlador): {str(e)}")
            return {"success": False, "error": "Ocurrió un error inesperado durante la compra."}
