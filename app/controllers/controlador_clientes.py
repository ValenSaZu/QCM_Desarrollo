from domain.entities.cliente import Cliente

# G-009: Controlador para gestión completa de clientes que incluye:
# - Obtención y búsqueda de clientes
# - Gestión de saldo (consultas y actualizaciones)
# - Historial de transacciones y compras
# - Manejo de estado (cliente/excliente)
class ControladorClientes:
    # CTRL-CLI-001: Obtiene todos los clientes registrados en el sistema
    # Retorna:
    #   list[dict]: Lista de clientes en formato:
    #       [{
    #           "id_usuario": int,
    #           "username": str,
    #           "nombre": str,
    #           "apellido": str,
    #           "saldo": float (default 0.0),
    #           "excliente": bool (default False)
    #       }]
    # Excepciones:
    #   Exception: Si falla la consulta a la base de datos
    # Logs:
    #   - Registra errores durante el proceso
    def obtener_todos_clientes(self):
        try:
            clientes = Cliente.obtener_todos()
            if not clientes:
                return []

            return [{
                "id_usuario": cliente.id_usuario,
                "username": cliente.username,
                "nombre": cliente.nombre,
                "apellido": cliente.apellido,
                "saldo": float(cliente.saldo) if cliente.saldo is not None else 0.0,
                "excliente": bool(cliente.excliente) if cliente.excliente is not None else False
            } for cliente in clientes]
        except Exception as e:
            print(f"Error en obtener_todos_clientes: {str(e)}")
            raise Exception(f"Error al obtener clientes: {str(e)}")

    # CTRL-CLI-002: Obtiene el historial completo de transacciones de un cliente
    # Parámetros:
    #   id_usuario (int): ID del cliente a consultar
    # Retorna:
    #   dict: {
    #       "mensaje": str (status),
    #       "historial": list (transacciones) o lista vacía si no hay registros
    #   }
    # Excepciones:
    #   Exception: Si falla la consulta del historial
    def obtener_historial_cliente(self, id_usuario):
        try:
            historial = Cliente.obtener_historial(id_usuario)
            if not historial:
                return {"mensaje": "No hay registros", "historial": []}
            return historial
        except Exception as e:
            print(f"Error en obtener_historial_cliente: {str(e)}")
            raise Exception(f"Error al obtener historial de cliente: {str(e)}")

    # CTRL-CLI-003: Obtiene el historial de compras exitosas de un cliente
    # Parámetros:
    #   id_usuario (int): ID del cliente a consultar
    # Retorna:
    #   list: Transacciones exitosas o lista vacía si no hay registros
    # Excepciones:
    #   Exception: Si falla la consulta del historial
    def obtener_historial_compras_cliente(self, id_usuario):
        try:
            historial_compras = Cliente.obtener_historial_compras(id_usuario)
            if not historial_compras or not historial_compras.get('success'):
                return []
            return historial_compras.get('data', [])
        except Exception as e:
            print(f"Error en obtener_historial_compras_cliente: {str(e)}")
            raise Exception(f"Error al obtener historial de compras de cliente: {str(e)}")

    # CTRL-CLI-004: Actualiza el saldo disponible de un cliente
    # Parámetros:
    #   id_usuario (int): ID del cliente a actualizar
    #   nuevo_saldo (float): Nuevo valor de saldo
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "nuevo_saldo": float,
    #       "message": str
    #   }
    # Excepciones:
    #   Exception: Si falla la actualización
    def actualizar_saldo_cliente(self, id_usuario, nuevo_saldo):
        try:
            saldo_actualizado = Cliente.actualizar_saldo(id_usuario, nuevo_saldo)
            return {
                "success": True,
                "nuevo_saldo": saldo_actualizado,
                "message": "Saldo actualizado correctamente"
            }
        except Exception as e:
            raise Exception(str(e))

    # CTRL-CLI-005: Busca clientes por término (nombre, apellido o username)
    # Parámetros:
    #   termino_busqueda (str): Texto para buscar coincidencias
    # Retorna:
    #   list[dict]: Lista de clientes que coinciden (mismo formato que obtener_todos_clientes)
    # Excepciones:
    #   Exception: Si falla la búsqueda
    def buscar_clientes(self, termino_busqueda):
        try:
            clientes = Cliente.buscar_por_termino(termino_busqueda)
            if not clientes:
                return []

            return [{
                "id_usuario": cliente.id_usuario,
                "username": cliente.username,
                "nombre": cliente.nombre,
                "apellido": cliente.apellido,
                "saldo": float(cliente.saldo) if cliente.saldo is not None else 0.0,
                "excliente": bool(cliente.excliente) if cliente.excliente is not None else False
            } for cliente in clientes]
        except Exception as e:
            print(f"Error en buscar_clientes: {str(e)}")
            raise Exception(f"Error al buscar clientes: {str(e)}")

    # CTRL-CLI-006: Marca un cliente como excliente (eliminación lógica)
    # Parámetros:
    #   id_usuario (int): ID del cliente a marcar
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "message": str|error
    #   }
    # Validaciones:
    #   - Cliente debe existir
    #   - No debe estar ya marcado como excliente
    def marcar_como_excliente(self, id_usuario):
        try:
            cliente = Cliente.obtener_por_id(id_usuario)
            if not cliente:
                return {"success": False, "error": "Cliente no encontrado"}

            if cliente.excliente:
                return {"success": False, "error": "El cliente ya está marcado como excliente"}

            Cliente.marcar_como_excliente(id_usuario, True)

            return {
                "success": True,
                "message": f"Cliente {cliente.nombre} {cliente.apellido} marcado como excliente correctamente"
            }

        except Exception as e:
            print(f"Error en marcar_como_excliente: {str(e)}")
            return {"success": False, "error": f"Error al marcar cliente como excliente: {str(e)}"}

    # CTRL-CLI-007: Reactiva un cliente marcado previamente como excliente
    # Parámetros:
    #   id_usuario (int): ID del cliente a reactivar
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "message": str|error
    #   }
    # Validaciones:
    #   - Cliente debe existir
    #   - Debe estar marcado como excliente previamente
    def reactivar_cliente(self, id_usuario):
        try:
            cliente = Cliente.obtener_por_id(id_usuario)
            if not cliente:
                return {"success": False, "error": "Cliente no encontrado"}

            if not cliente.excliente:
                return {"success": False, "error": "El cliente no está marcado como excliente"}

            Cliente.marcar_como_excliente(id_usuario, False)

            return {
                "success": True,
                "message": f"Cliente {cliente.nombre} {cliente.apellido} reactivado correctamente"
            }

        except Exception as e:
            print(f"Error en reactivar_cliente: {str(e)}")
            return {"success": False, "error": f"Error al reactivar cliente: {str(e)}"}