# Controlador para gestionar las operaciones relacionadas con clientes
from domain.entities.cliente import Cliente

class ControladorClientes:
    def obtener_todos_clientes(self):
        """Obtiene todos los clientes registrados y los retorna en formato JSON"""
        try:
            clientes = Cliente.obtener_todos()
            # Asegurarse de que siempre devolvemos una lista
            if not clientes:
                return []
                
            # Convertir los clientes a diccionarios
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

    def obtener_historial_cliente(self, id_usuario):
        """Obtiene el historial de transacciones de un cliente específico"""
        try:
            historial = Cliente.obtener_historial(id_usuario)
            if not historial:
                return {"mensaje": "No hay registros", "historial": []}
            return historial
        except Exception as e:
            print(f"Error en obtener_historial_cliente: {str(e)}")
            raise Exception(f"Error al obtener historial de cliente: {str(e)}")

    def obtener_historial_compras_cliente(self, id_usuario):
        """Obtiene el historial de compras de un cliente específico"""
        try:
            historial_compras = Cliente.obtener_historial_compras(id_usuario)
            if not historial_compras or not historial_compras.get('success'):
                return []
            return historial_compras.get('data', [])
        except Exception as e:
            print(f"Error en obtener_historial_compras_cliente: {str(e)}")
            raise Exception(f"Error al obtener historial de compras de cliente: {str(e)}")

    def actualizar_saldo_cliente(self, id_usuario, nuevo_saldo):
        """Actualiza el saldo de un cliente y retorna el nuevo saldo"""
        try:
            saldo_actualizado = Cliente.actualizar_saldo(id_usuario, nuevo_saldo)
            return {
                "success": True,
                "nuevo_saldo": saldo_actualizado,
                "message": "Saldo actualizado correctamente"
            }
        except Exception as e:
            raise Exception(str(e))

    def buscar_clientes(self, termino_busqueda):
        """Busca clientes que coincidan con el término de búsqueda"""
        try:
            clientes = Cliente.buscar_por_termino(termino_busqueda)
            # Asegurarse de que siempre devolvemos una lista
            if not clientes:
                return []
                
            # Convertir los clientes a diccionarios
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

    def marcar_como_excliente(self, id_usuario):
        """
        Marca un cliente como excliente (eliminado).
        Este método es usado por administradores para eliminar clientes.
        
        Args:
            id_usuario (int): ID del usuario a marcar como excliente
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Verificar que el cliente existe
            cliente = Cliente.obtener_por_id(id_usuario)
            if not cliente:
                return {"success": False, "error": "Cliente no encontrado"}
            
            # Verificar que no esté ya marcado como excliente
            if cliente.excliente:
                return {"success": False, "error": "El cliente ya está marcado como excliente"}
            
            # Marcar como excliente
            Cliente.marcar_como_excliente(id_usuario, True)
            
            return {
                "success": True, 
                "message": f"Cliente {cliente.nombre} {cliente.apellido} marcado como excliente correctamente"
            }
            
        except Exception as e:
            print(f"Error en marcar_como_excliente: {str(e)}")
            return {"success": False, "error": f"Error al marcar cliente como excliente: {str(e)}"}

    def reactivar_cliente(self, id_usuario):
        """
        Reactiva un cliente que estaba marcado como excliente.
        
        Args:
            id_usuario (int): ID del usuario a reactivar
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Verificar que el cliente existe
            cliente = Cliente.obtener_por_id(id_usuario)
            if not cliente:
                return {"success": False, "error": "Cliente no encontrado"}
            
            # Verificar que esté marcado como excliente
            if not cliente.excliente:
                return {"success": False, "error": "El cliente no está marcado como excliente"}
            
            # Reactivar cliente
            Cliente.marcar_como_excliente(id_usuario, False)
            
            return {
                "success": True, 
                "message": f"Cliente {cliente.nombre} {cliente.apellido} reactivado correctamente"
            }
            
        except Exception as e:
            print(f"Error en reactivar_cliente: {str(e)}")
            return {"success": False, "error": f"Error al reactivar cliente: {str(e)}"}