# Controlador para gestionar las operaciones relacionadas con clientes
from domain.entities.cliente import Cliente

class ControladorClientes:
    def obtener_todos_clientes(self):
        """Obtiene todos los clientes registrados y los retorna en formato JSON"""
        clientes = Cliente.obtener_todos()
        return [{
            "id_usuario": cliente.id_usuario,
            "username": cliente.username,
            "nombre": cliente.nombre,
            "apellido": cliente.apellido,
            "saldo": float(cliente.saldo),
            "excliente": bool(cliente.excliente)
        } for cliente in clientes]

    def obtener_historial_cliente(self, id_usuario):
        """Obtiene el historial de transacciones de un cliente específico"""
        historial = Cliente.obtener_historial(id_usuario)
        if not historial:
            return {"mensaje": "No hay registros", "historial": []}
        return historial

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
        clientes = Cliente.buscar_por_termino(termino_busqueda)
        return [{
            "id_usuario": cliente.id_usuario,
            "username": cliente.username,
            "nombre": cliente.nombre,
            "apellido": cliente.apellido,
            "saldo": cliente.saldo
        } for cliente in clientes]