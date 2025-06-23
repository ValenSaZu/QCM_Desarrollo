from infrastructure.bd.conexion import obtener_conexion

class CarritoItem:
    """Clase auxiliar para representar un item del carrito"""
    def __init__(self, id_contenido, nombre, autor, descripcion, precio_original, precio_con_descuento, cantidad, formato):
        self.id_contenido = id_contenido
        self.nombre = nombre
        self.autor = autor
        self.descripcion = descripcion
        self.precio_original = precio_original
        self.precio_con_descuento = precio_con_descuento
        self.cantidad = cantidad
        self.formato = formato

class Carrito:
    def __init__(self, id_carrito, descuento_aplicado, id_usuario):
        self.id_carrito = id_carrito
        self.descuento_aplicado = descuento_aplicado
        self.id_usuario = id_usuario

    @classmethod
    def obtener_carrito_por_usuario(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            print(f"Ejecutando consulta de carrito para usuario: {id_usuario}")
            query = """
                    SELECT contenido.id_contenido, \
                           contenido.nombre, \
                           contenido.autor, \
                           contenido.descripcion, \
                           contenido.precio                                          AS precio_original, \
                           contenido.precio * (1 - COALESCE(CASE WHEN p.fecha_inicio <= CURRENT_DATE AND p.fecha_fin >= CURRENT_DATE THEN p.descuento ELSE 0 END, 0) / 100.0) AS precio_con_descuento, \
                           cc.cantidad, \
                           carrito.descuento_aplicado, \
                           t.formato                                                 AS tipo_formato
                    FROM CARRITO carrito
                             JOIN CONTENIDO_CARRITO cc ON carrito.id_carrito = cc.id_carrito
                             JOIN CONTENIDO contenido ON cc.id_contenido = contenido.id_contenido
                             LEFT JOIN PROMOCION p ON contenido.id_promocion = p.id_promocion
                             LEFT JOIN TIPO_ARCHIVO t ON contenido.id_tipo_archivo = t.id_tipo_archivo
                    WHERE carrito.id_usuario = %s; \
                    """
            print(f"Query SQL: {query}")
            cursor.execute(query, (id_usuario,))
            filas = cursor.fetchall()
            print(f"Filas obtenidas: {filas}")

            carrito = []
            descuento_aplicado = 0

            for i, row in enumerate(filas):
                print(f"Procesando fila {i}: {row}")
                contenidoCarrito = CarritoItem(
                    id_contenido=row[0] if len(row) > 0 else None,
                    nombre=row[1] if len(row) > 1 else '',
                    autor=row[2] if len(row) > 2 else '',
                    descripcion=row[3] if len(row) > 3 else '',
                    precio_original=row[4] if len(row) > 4 else 0,
                    precio_con_descuento=row[5] if len(row) > 5 else 0,
                    cantidad=row[6] if len(row) > 6 else 1,
                    formato=row[8] if len(row) > 8 and row[8] else 'imagen'
                )
                print(f"CarritoItem creado: {contenidoCarrito.__dict__}")
                carrito.append(contenidoCarrito)

                # Guardar descuento_aplicado solo una vez
                if i == 0 and len(row) > 7:
                    descuento_aplicado = row[7]

            print(f"Carrito final: {len(carrito)} items")
            return carrito, descuento_aplicado

        except Exception as e:
            print(f"Error en obtener_carrito_por_usuario: {str(e)}")
            raise Exception(f"Error al obtener carrito del usuario: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def vaciar_carrito(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT id_carrito
                           FROM CARRITO
                           WHERE id_usuario = %s;
                           """, (id_usuario,))
            resultado = cursor.fetchone()

            if not resultado:
                raise Exception("El usuario no tiene un carrito.")

            id_carrito = resultado[0]

            cursor.execute("""
                           DELETE
                           FROM CONTENIDO_CARRITO
                           WHERE id_carrito = %s;
                           """, (id_carrito,))

            cursor.execute("""
                           UPDATE CARRITO
                           SET descuento_aplicado = 0
                           WHERE id_carrito = %s;
                           """, (id_carrito,))

            conexion.commit()

        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al vaciar el carrito: {str(e)}")

        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def agregar_contenido(cls, id_usuario, id_contenido, cantidad=1):
        """Agrega un contenido al carrito de un usuario"""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            # Verificar si el usuario tiene un carrito, si no, crearlo
            cursor.execute("""
                SELECT id_carrito
                FROM CARRITO
                WHERE id_usuario = %s;
            """, (id_usuario,))
            
            resultado = cursor.fetchone()
            
            if not resultado:
                # Crear carrito para el usuario
                cursor.execute("""
                    INSERT INTO CARRITO (descuento_aplicado, id_usuario)
                    VALUES (0, %s)
                    RETURNING id_carrito;
                """, (id_usuario,))
                carrito_result = cursor.fetchone()
                if not carrito_result:
                    raise Exception("No se pudo crear el carrito")
                id_carrito = carrito_result[0]
            else:
                id_carrito = resultado[0]

            # Verificar si el contenido ya está en el carrito
            cursor.execute("""
                SELECT cantidad
                FROM CONTENIDO_CARRITO
                WHERE id_carrito = %s AND id_contenido = %s;
            """, (id_carrito, id_contenido))
            
            contenido_existente = cursor.fetchone()
            
            if contenido_existente:
                # Actualizar cantidad
                nueva_cantidad = contenido_existente[0] + cantidad
                cursor.execute("""
                    UPDATE CONTENIDO_CARRITO
                    SET cantidad = %s
                    WHERE id_carrito = %s AND id_contenido = %s;
                """, (nueva_cantidad, id_carrito, id_contenido))
            else:
                # Agregar nuevo contenido
                cursor.execute("""
                    INSERT INTO CONTENIDO_CARRITO (id_contenido, id_carrito, cantidad)
                    VALUES (%s, %s, %s);
                """, (id_contenido, id_carrito, cantidad))

            conexion.commit()
            return True

        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al agregar contenido al carrito: {str(e)}")

        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def registrar_compra_y_vaciar_carrito(cls, id_usuario, items_comprados, total_compra):
        """
        Realiza la transacción de compra completa:
        1. Verifica el saldo del cliente con bloqueo para seguridad.
        2. Actualiza el saldo del cliente.
        3. Registra cada item comprado en la tabla COMPRA.
        4. Vacía el carrito del usuario.
        Todo se ejecuta en una sola transacción.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            # 1. Verificar saldo (con bloqueo para evitar race conditions)
            cursor.execute("SELECT saldo FROM CLIENTE WHERE id_usuario = %s FOR UPDATE", (id_usuario,))
            saldo_result = cursor.fetchone()
            if not saldo_result:
                raise ValueError("Cliente no encontrado.")
            
            saldo_actual = saldo_result[0]
            
            if saldo_actual < total_compra:
                raise ValueError(f"Saldo insuficiente. Necesitas S/.{total_compra:.2f} y tienes S/.{saldo_actual:.2f}")

            # 2. Actualizar saldo del cliente
            nuevo_saldo = saldo_actual - total_compra
            cursor.execute("UPDATE CLIENTE SET saldo = %s WHERE id_usuario = %s", (nuevo_saldo, id_usuario))

            # 3. Registrar cada compra
            for item in items_comprados:
                for _ in range(item.cantidad):
                    cursor.execute(
                        "INSERT INTO COMPRA (id_usuario, id_contenido) VALUES (%s, %s)",
                        (id_usuario, item.id_contenido)
                    )
                    print(f"Compra registrada: Usuario {id_usuario}, Contenido {item.id_contenido}")

            # 4. Vaciar el carrito
            cursor.execute("SELECT id_carrito FROM CARRITO WHERE id_usuario = %s", (id_usuario,))
            id_carrito_result = cursor.fetchone()
            if id_carrito_result:
                id_carrito = id_carrito_result[0]
                cursor.execute("DELETE FROM CONTENIDO_CARRITO WHERE id_carrito = %s", (id_carrito,))

            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error transaccional en la compra: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def eliminar_contenido(cls, id_usuario, id_contenido):
        """Elimina un contenido específico del carrito de un usuario."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            # Primero, obtener el id_carrito del usuario
            cursor.execute("SELECT id_carrito FROM CARRITO WHERE id_usuario = %s", (id_usuario,))
            carrito_result = cursor.fetchone()

            if not carrito_result:
                # Si no hay carrito, no hay nada que eliminar
                return True

            id_carrito = carrito_result[0]

            # Eliminar el item de la tabla de relación CONTENIDO_CARRITO
            cursor.execute(
                "DELETE FROM CONTENIDO_CARRITO WHERE id_carrito = %s AND id_contenido = %s",
                (id_carrito, id_contenido)
            )

            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al eliminar contenido del carrito (entidad): {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def calcular_descuentos_disponibles(cls, id_usuario):
        """
        Calcula la cantidad de descuentos disponibles basado en el saldo acumulado.
        1 descuento por cada S/30 acumulados.
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            int: Número de descuentos disponibles
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # Obtener el saldo actual del usuario
            cursor.execute("SELECT saldo FROM CLIENTE WHERE id_usuario = %s", (id_usuario,))
            saldo_result = cursor.fetchone()
            
            if not saldo_result:
                return 0
            
            saldo_actual = saldo_result[0]
            
            # Calcular descuentos disponibles: 1 por cada S/30
            descuentos_disponibles = int(saldo_actual // 30)
            
            return descuentos_disponibles
            
        except Exception as e:
            print(f"Error al calcular descuentos disponibles: {str(e)}")
            return 0
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def aplicar_descuento_contenido(cls, id_usuario, id_contenido, aplicar=True):
        """
        Aplica o remueve el descuento de un contenido específico en el carrito.
        
        Args:
            id_usuario (int): ID del usuario
            id_contenido (int): ID del contenido
            aplicar (bool): True para aplicar descuento, False para remover
            
        Returns:
            dict: Resultado de la operación
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # Verificar que el contenido está en el carrito del usuario
            cursor.execute("""
                SELECT cc.id_contenido, cc.descuento_aplicado
                FROM CARRITO c
                JOIN CONTENIDO_CARRITO cc ON c.id_carrito = cc.id_carrito
                WHERE c.id_usuario = %s AND cc.id_contenido = %s
            """, (id_usuario, id_contenido))
            
            resultado = cursor.fetchone()
            if not resultado:
                return {"success": False, "error": "Contenido no encontrado en el carrito"}
            
            descuento_actual = resultado[1] or 0
            
            if aplicar:
                # Verificar descuentos disponibles
                descuentos_disponibles = cls.calcular_descuentos_disponibles(id_usuario)
                
                # Contar cuántos descuentos ya están aplicados
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM CARRITO c
                    JOIN CONTENIDO_CARRITO cc ON c.id_carrito = cc.id_carrito
                    WHERE c.id_usuario = %s AND cc.descuento_aplicado = 1
                """, (id_usuario,))
                
                descuentos_aplicados = cursor.fetchone()[0]
                
                if descuentos_aplicados >= descuentos_disponibles:
                    return {"success": False, "error": f"No tienes suficientes descuentos disponibles. Tienes {descuentos_disponibles} descuentos y ya has aplicado {descuentos_aplicados}"}
                
                # Aplicar descuento (10%)
                nuevo_descuento = 1
            else:
                # Remover descuento
                nuevo_descuento = 0
            
            # Actualizar el descuento en el contenido
            cursor.execute("""
                UPDATE CONTENIDO_CARRITO 
                SET descuento_aplicado = %s
                WHERE id_carrito = (SELECT id_carrito FROM CARRITO WHERE id_usuario = %s)
                AND id_contenido = %s
            """, (nuevo_descuento, id_usuario, id_contenido))
            
            conexion.commit()
            
            accion = "aplicado" if aplicar else "removido"
            return {
                "success": True, 
                "message": f"Descuento {accion} correctamente",
                "descuento_aplicado": nuevo_descuento
            }
            
        except Exception as e:
            conexion.rollback()
            print(f"Error al aplicar descuento: {str(e)}")
            return {"success": False, "error": f"Error al aplicar descuento: {str(e)}"}
        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def obtener_descuentos_aplicados(cls, id_usuario):
        """
        Obtiene información sobre los descuentos aplicados en el carrito.
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            dict: Información sobre descuentos
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # Calcular descuentos disponibles
            descuentos_disponibles = cls.calcular_descuentos_disponibles(id_usuario)
            
            # Contar descuentos aplicados
            cursor.execute("""
                SELECT COUNT(*) 
                FROM CARRITO c
                JOIN CONTENIDO_CARRITO cc ON c.id_carrito = cc.id_carrito
                WHERE c.id_usuario = %s AND cc.descuento_aplicado = 1
            """, (id_usuario,))
            
            descuentos_aplicados = cursor.fetchone()[0]
            
            # Obtener contenidos con descuento aplicado
            cursor.execute("""
                SELECT cc.id_contenido, c.nombre, c.precio
                FROM CARRITO car
                JOIN CONTENIDO_CARRITO cc ON car.id_carrito = cc.id_carrito
                JOIN CONTENIDO c ON cc.id_contenido = c.id_contenido
                WHERE car.id_usuario = %s AND cc.descuento_aplicado = 1
            """, (id_usuario,))
            
            contenidos_con_descuento = []
            for row in cursor.fetchall():
                contenidos_con_descuento.append({
                    "id_contenido": row[0],
                    "nombre": row[1],
                    "precio": row[2]
                })
            
            return {
                "descuentos_disponibles": descuentos_disponibles,
                "descuentos_aplicados": descuentos_aplicados,
                "descuentos_restantes": descuentos_disponibles - descuentos_aplicados,
                "contenidos_con_descuento": contenidos_con_descuento
            }
            
        except Exception as e:
            print(f"Error al obtener descuentos aplicados: {str(e)}")
            return {
                "descuentos_disponibles": 0,
                "descuentos_aplicados": 0,
                "descuentos_restantes": 0,
                "contenidos_con_descuento": []
            }
        finally:
            cursor.close()
            conexion.close()
