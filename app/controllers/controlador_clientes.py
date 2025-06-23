from domain.entities.cliente import Cliente

# G-009: Controlador para gestionar todas las operaciones relacionadas con clientes
class ControladorClientes:
    # CTRL-CLI-001: Obtiene todos los clientes registrados en formato JSON
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

    # CTRL-CLI-002: Obtiene el historial de transacciones de un cliente específico
    def obtener_historial_cliente(self, id_usuario):
        try:
            historial = Cliente.obtener_historial(id_usuario)
            if not historial:
                return {"mensaje": "No hay registros", "historial": []}
            return historial
        except Exception as e:
            print(f"Error en obtener_historial_cliente: {str(e)}")
            raise Exception(f"Error al obtener historial de cliente: {str(e)}")

    # CTRL-CLI-003: Obtiene el historial de compras de un cliente (solo transacciones exitosas)
    def obtener_historial_compras_cliente(self, id_usuario):
        try:
            historial_compras = Cliente.obtener_historial_compras(id_usuario)
            if not historial_compras or not historial_compras.get('success'):
                return []
            return historial_compras.get('data', [])
        except Exception as e:
            print(f"Error en obtener_historial_compras_cliente: {str(e)}")
            raise Exception(f"Error al obtener historial de compras de cliente: {str(e)}")

    # CTRL-CLI-004: Actualiza el saldo de un cliente y devuelve el nuevo valor
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

    # CTRL-CLI-005: Busca clientes por nombre, apellido o username
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

    # CTRL-CLI-007: Reactiva un cliente previamente marcado como excliente
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