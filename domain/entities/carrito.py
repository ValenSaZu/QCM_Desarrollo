from infrastructure.bd.conexion import obtener_conexion

# G-013: Clase auxiliar para representar items del carrito que incluye:
# - Información detallada de cada contenido en el carrito
# - Datos de precios originales y con descuento
# - Cantidad y formato del contenido
class CarritoItem:
    def __init__(self, id_contenido, nombre, autor, descripcion, precio_original, precio_con_descuento, cantidad,
                 formato):
        self.id_contenido = id_contenido
        self.nombre = nombre
        self.autor = autor
        self.descripcion = descripcion
        self.precio_original = precio_original
        self.precio_con_descuento = precio_con_descuento
        self.cantidad = cantidad
        self.formato = formato

# G-003: Entidad para gestionar operaciones del carrito de compras que incluye:
# - Obtención y modificación del estado del carrito
# - Aplicación de descuentos y promociones
# - Procesamiento de compras
# - Manejo seguro de transacciones de base de datos
class Carrito:

    # ENT-CARR-001: Obtiene el carrito completo de un usuario
    # Parámetros:
    #   id_usuario (int): Identificador único del usuario
    # Retorna:
    #   tuple: (list[CarritoItem], int) - (items del carrito, descuento aplicado)
    # Excepciones:
    #   - Captura y relanza excepciones de base de datos
    # Características:
    #   - Consulta JOIN entre múltiples tablas
    #   - Calcula precios con descuentos aplicables
    #   - Manejo seguro de conexiones con try-finally
    @classmethod
    def obtener_carrito_por_usuario(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                    SELECT contenido.id_contenido, \
                           contenido.nombre, \
                           contenido.autor,
                           contenido.descripcion, \
                           contenido.precio                                            AS precio_original,
                           contenido.precio * (1 - COALESCE(
                                                           CASE \
                                                               WHEN p.fecha_inicio <= CURRENT_DATE AND p.fecha_fin >= CURRENT_DATE \
                                                                   THEN p.descuento \
                                                               ELSE 0 END, 0) / 100.0) AS precio_con_descuento,
                           cc.cantidad, \
                           carrito.descuento_aplicado, \
                           t.formato                                                   AS tipo_formato
                    FROM CARRITO carrito
                             JOIN CONTENIDO_CARRITO cc ON carrito.id_carrito = cc.id_carrito
                             JOIN CONTENIDO contenido ON cc.id_contenido = contenido.id_contenido
                             LEFT JOIN PROMOCION p ON contenido.id_promocion = p.id_promocion
                             LEFT JOIN TIPO_ARCHIVO t ON contenido.id_tipo_archivo = t.id_tipo_archivo
                    WHERE carrito.id_usuario = %s; \
                    """
            cursor.execute(query, (id_usuario,))

            carrito = []
            descuento_aplicado = 0

            for i, row in enumerate(cursor.fetchall()):
                item = CarritoItem(
                    id_contenido=row[0],
                    nombre=row[1],
                    autor=row[2],
                    descripcion=row[3],
                    precio_original=row[4],
                    precio_con_descuento=row[5],
                    cantidad=row[6],
                    formato=row[8] if row[8] else 'imagen'
                )
                carrito.append(item)

                if i == 0:
                    descuento_aplicado = row[7]

            return carrito, descuento_aplicado

        except Exception:
            raise Exception("Error al obtener carrito")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CARR-002: Vacía el carrito de un usuario
    # Parámetros:
    #   id_usuario (int): Identificador único del usuario
    # Excepciones:
    #   - Maneja rollback en caso de error
    # Características:
    #   - Elimina todos los items del carrito
    #   - Resetea los descuentos aplicados
    #   - Transacción atómica
    @classmethod
    def vaciar_carrito(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT id_carrito FROM CARRITO WHERE id_usuario = %s", (id_usuario,))
            resultado = cursor.fetchone()

            if not resultado:
                raise Exception("Usuario sin carrito")

            id_carrito = resultado[0]

            cursor.execute("DELETE FROM CONTENIDO_CARRITO WHERE id_carrito = %s", (id_carrito,))
            cursor.execute("UPDATE CARRITO SET descuento_aplicado = 0 WHERE id_carrito = %s", (id_carrito,))

            conexion.commit()
        except Exception:
            conexion.rollback()
            raise Exception("Error al vaciar carrito")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CARR-003: Agrega un contenido al carrito
    # Parámetros:
    #   id_usuario (int): Identificador del usuario
    #   id_contenido (int): Identificador del contenido
    #   cantidad (int): Cantidad a agregar (default: 1)
    # Retorna:
    #   bool: True si la operación fue exitosa
    # Características:
    #   - Crea carrito si no existe
    #   - Incrementa cantidad si el item ya existe
    #   - Transacción atómica
    @classmethod
    def agregar_contenido(cls, id_usuario, id_contenido, cantidad=1):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT id_carrito FROM CARRITO WHERE id_usuario = %s", (id_usuario,))
            resultado = cursor.fetchone()

            if not resultado:
                cursor.execute("""
                               INSERT INTO CARRITO (descuento_aplicado, id_usuario)
                               VALUES (0, %s) RETURNING id_carrito;
                               """, (id_usuario,))
                id_carrito_row = cursor.fetchone()
                if id_carrito_row:
                    id_carrito = id_carrito_row[0]
                else:
                    raise Exception("No se pudo crear el carrito")
            else:
                id_carrito = resultado[0]

            cursor.execute("""
                           SELECT cantidad
                           FROM CONTENIDO_CARRITO
                           WHERE id_carrito = %s
                             AND id_contenido = %s;
                           """, (id_carrito, id_contenido))

            if (existente := cursor.fetchone()):
                cursor.execute("""
                               UPDATE CONTENIDO_CARRITO
                               SET cantidad = %s
                               WHERE id_carrito = %s
                                 AND id_contenido = %s;
                               """, (existente[0] + cantidad, id_carrito, id_contenido))
            else:
                cursor.execute("""
                               INSERT INTO CONTENIDO_CARRITO (id_contenido, id_carrito, cantidad)
                               VALUES (%s, %s, %s);
                               """, (id_contenido, id_carrito, cantidad))

            conexion.commit()
            return True
        except Exception:
            conexion.rollback()
            raise Exception("Error al agregar contenido")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CARR-004: Procesa la compra y vacía el carrito
    # Parámetros:
    #   id_usuario (int): Identificador del usuario
    #   items_comprados (list[CarritoItem]): Items a comprar
    #   total_compra (float): Total de la compra
    # Retorna:
    #   bool: True si la compra fue exitosa
    # Características:
    #   - Verifica saldo suficiente
    #   - Registra cada item comprado
    #   - Transacción atómica con bloqueo de fila
    @classmethod
    def registrar_compra_y_vaciar_carrito(cls, id_usuario, items_comprados, total_compra):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT saldo FROM CLIENTE WHERE id_usuario = %s FOR UPDATE", (id_usuario,))
            saldo_row = cursor.fetchone()
            if not saldo_row:
                raise ValueError("Cliente no encontrado")
            saldo = saldo_row[0]

            if saldo < total_compra:
                raise ValueError("Saldo insuficiente")

            cursor.execute("UPDATE CLIENTE SET saldo = %s WHERE id_usuario = %s",
                           (saldo - total_compra, id_usuario))

            for item in items_comprados:
                cursor.executemany(
                    "INSERT INTO COMPRA (id_usuario, id_contenido) VALUES (%s, %s)",
                    [(id_usuario, item.id_contenido)] * item.cantidad
                )

            cursor.execute("SELECT id_carrito FROM CARRITO WHERE id_usuario = %s", (id_usuario,))
            resultado = cursor.fetchone()
            if resultado:
                id_carrito = resultado[0]
                cursor.execute("DELETE FROM CONTENIDO_CARRITO WHERE id_carrito = %s", (id_carrito,))

            conexion.commit()
            return True
        except Exception:
            conexion.rollback()
            raise Exception("Error en transacción de compra")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CARR-005: Elimina un contenido específico del carrito
    # Parámetros:
    #   id_usuario (int): Identificador del usuario
    #   id_contenido (int): Identificador del contenido
    # Retorna:
    #   bool: True si la eliminación fue exitosa
    # Características:
    #   - Transacción atómica
    @classmethod
    def eliminar_contenido(cls, id_usuario, id_contenido):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           DELETE
                           FROM CONTENIDO_CARRITO
                           WHERE id_carrito = (SELECT id_carrito FROM CARRITO WHERE id_usuario = %s)
                             AND id_contenido = %s
                           """, (id_usuario, id_contenido))

            conexion.commit()
            return True
        except Exception:
            conexion.rollback()
            raise Exception("Error al eliminar contenido")
        finally:
            cursor.close()
            conexion.close()

    # ENT-CARR-006: Calcula descuentos disponibles basados en saldo
    # Parámetros:
    #   id_usuario (int): Identificador del usuario
    # Retorna:
    #   int: Número de descuentos disponibles
    # Características:
    #   - Calcula descuentos como saldo//30
    @classmethod
    def calcular_descuentos_disponibles(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT saldo FROM CLIENTE WHERE id_usuario = %s", (id_usuario,))
            saldo_row = cursor.fetchone()
            if saldo_row:
                return int(saldo_row[0] // 30)
            return 0
        except Exception:
            return 0
        finally:
            cursor.close()
            conexion.close()

    # ENT-CARR-007: Aplica o remueve descuento de un contenido
    # Parámetros:
    #   id_usuario (int): Identificador del usuario
    #   id_contenido (int): Identificador del contenido
    #   aplicar (bool): True para aplicar, False para remover
    # Retorna:
    #   dict: {'success': bool, 'error/message': str}
    # Características:
    #   - Verifica límite de descuentos
    #   - Transacción atómica
    @classmethod
    def aplicar_descuento_contenido(cls, id_usuario, id_contenido, aplicar=True):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("""
                           SELECT cc.id_contenido
                           FROM CARRITO c
                                    JOIN CONTENIDO_CARRITO cc ON c.id_carrito = cc.id_carrito
                           WHERE c.id_usuario = %s
                             AND cc.id_contenido = %s
                           """, (id_usuario, id_contenido))

            if not cursor.fetchone():
                return {"success": False, "error": "Contenido no encontrado"}

            if aplicar:
                disponibles = cls.calcular_descuentos_disponibles(id_usuario)
                cursor.execute("""
                               SELECT COUNT(*)
                               FROM CARRITO c
                                        JOIN CONTENIDO_CARRITO cc ON c.id_carrito = cc.id_carrito
                               WHERE c.id_usuario = %s
                                 AND cc.descuento_aplicado = 1
                               """, (id_usuario,))

                count_row = cursor.fetchone()
                if count_row and count_row[0] >= disponibles:
                    return {"success": False, "error": "Límite de descuentos alcanzado"}

            cursor.execute("""
                           UPDATE CONTENIDO_CARRITO
                           SET descuento_aplicado = %s
                           WHERE id_carrito = (SELECT id_carrito FROM CARRITO WHERE id_usuario = %s)
                             AND id_contenido = %s
                           """, (1 if aplicar else 0, id_usuario, id_contenido))

            conexion.commit()
            return {"success": True, "message": "Operación exitosa"}
        except Exception:
            conexion.rollback()
            return {"success": False, "error": "Error al aplicar descuento"}
        finally:
            cursor.close()
            conexion.close()

    # ENT-CARR-008: Obtiene información sobre descuentos aplicados
    # Parámetros:
    #   id_usuario (int): Identificador del usuario
    # Retorna:
    #   dict: Información detallada de descuentos
    # Características:
    #   - Incluye contadores y lista de items con descuento
    @classmethod
    def obtener_descuentos_aplicados(cls, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            disponibles = cls.calcular_descuentos_disponibles(id_usuario)

            cursor.execute("""
                           SELECT COUNT(*)
                           FROM CARRITO c
                                    JOIN CONTENIDO_CARRITO cc ON c.id_carrito = cc.id_carrito
                           WHERE c.id_usuario = %s
                             AND cc.descuento_aplicado = 1
                           """, (id_usuario,))
            aplicados_row = cursor.fetchone()
            aplicados = aplicados_row[0] if aplicados_row else 0

            cursor.execute("""
                           SELECT cc.id_contenido, c.nombre, c.precio
                           FROM CARRITO car
                                    JOIN CONTENIDO_CARRITO cc ON car.id_carrito = cc.id_carrito
                                    JOIN CONTENIDO c ON cc.id_contenido = c.id_contenido
                           WHERE car.id_usuario = %s
                             AND cc.descuento_aplicado = 1
                           """, (id_usuario,))

            return {
                "descuentos_disponibles": disponibles,
                "descuentos_aplicados": aplicados,
                "descuentos_restantes": disponibles - aplicados,
                "contenidos_con_descuento": [
                    {"id_contenido": row[0], "nombre": row[1], "precio": row[2]}
                    for row in cursor.fetchall()
                ]
            }
        except Exception:
            return {
                "descuentos_disponibles": 0,
                "descuentos_aplicados": 0,
                "descuentos_restantes": 0,
                "contenidos_con_descuento": []
            }
        finally:
            cursor.close()
            conexion.close()