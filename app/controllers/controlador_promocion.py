from domain.entities.promocion import Promocion
from datetime import datetime
from domain.entities.contenido import Contenido

# G-008: Controlador para gestionar todas las operaciones de promociones
class ControladorPromocion:

    # CTRL-PROM-001: Obtiene todas las promociones activas del sistema
    def obtener_todas_promociones(self):
        try:
            promociones = Promocion.obtener_todas_promociones()
            return [{
                "id": promocion.id_promocion,
                "nombre": promocion.nombre,
                "porcentaje": float(promocion.descuento) if promocion.descuento is not None else 0.0,
                "fecha_inicio": promocion.fecha_inicio.isoformat(),
                "fecha_fin": promocion.fecha_fin.isoformat()
            } for promocion in promociones] if promociones else []
        except Exception:
            raise Exception("Error al obtener promociones")

    # CTRL-PROM-002: Obtiene los detalles completos de una promoción específica
    def obtener_promocion_por_id(self, id_promocion):
        try:
            if not id_promocion:
                return {"error": "ID de promoción requerido", "success": False}

            promocion = Promocion.obtener_promocion_por_id(id_promocion)
            if not promocion:
                return {"error": "Promoción no encontrada", "success": False}

            contenidos = Promocion.obtener_contenido_promocion(id_promocion)
            return {
                "id": promocion.id_promocion,
                "nombre": promocion.nombre,
                "porcentaje": float(promocion.descuento),
                "fecha_inicio": promocion.fecha_inicio.isoformat(),
                "fecha_fin": promocion.fecha_fin.isoformat(),
                "contenidos": [{
                    "id": c.get('id_contenido'),
                    "nombre": c.get('nombre', 'Sin nombre'),
                    "precio": float(c.get('precio', 0.0)),
                    "formato": c.get('formato', 'Desconocido')
                } for c in (contenidos or []) if c],
                "success": True
            }
        except Exception:
            return {"error": "Error al obtener promoción", "success": False}

    # CTRL-PROM-003: Crea una nueva promoción con sus contenidos asociados
    def agregar_promocion(self, form_data):
        try:
            nombre = form_data.get('nombre')
            porcentaje = float(form_data.get('porcentaje'))
            fecha_inicio = datetime.strptime(form_data.get('fecha_inicio'), '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(form_data.get('fecha_fin'), '%Y-%m-%d').date()

            id_promocion = Promocion.agregar_promocion(
                nombre=nombre,
                descuento=porcentaje,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            contenidos = {int(id) for id in form_data.get('contenidos', []) if id}
            for id_contenido in contenidos:
                Promocion.agregar_contenido_a_promocion(id_promocion, id_contenido)

            return {"success": True, "message": "Promoción creada", "id_promocion": id_promocion}
        except Exception:
            return {"success": False, "error": "Error al crear promoción"}

    # CTRL-PROM-004: Actualiza los datos de una promoción existente
    def editar_promocion(self, id_promocion, promocion_data):
        try:
            nombre = promocion_data['nombre']
            porcentaje = float(promocion_data['porcentaje'])
            fecha_inicio = datetime.strptime(promocion_data['fecha_inicio'], '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(promocion_data['fecha_fin'], '%Y-%m-%d').date()

            Promocion.actualizar_promocion(
                id_promocion=id_promocion,
                nombre=nombre,
                descuento=porcentaje,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            for c in Promocion.obtener_contenido_promocion(id_promocion) or []:
                if c and c.get('id_contenido') not in (None, ''):
                    Promocion.eliminar_contenido_de_promocion(id_promocion, c.get('id_contenido'))

            ids_nuevos = [id for id in promocion_data.get('contenidos', []) if id not in (None, '')]
            contenidos_nuevos = {int(id) for id in ids_nuevos}

            for id_contenido in contenidos_nuevos:
                Promocion.agregar_contenido_a_promocion(id_promocion, id_contenido)

            return {"success": True, "message": "Promoción actualizada"}
        except Exception:
            return {"success": False, "error": "Error al actualizar promoción"}

    # CTRL-PROM-005: Elimina permanentemente una promoción
    def eliminar_promocion(self, id_promocion):
        try:
            Promocion.eliminar_promocion(id_promocion)
            return {"success": True, "message": "Promoción eliminada"}
        except Exception:
            return {"success": False, "error": "Error al eliminar promoción"}

    # CTRL-PROM-006: Obtiene los contenidos con promociones activas
    def obtener_contenidos_con_promociones(self):
        try:
            contenidos = Contenido.obtener_contenidos_con_promociones()
            return {
                "success": True,
                "data": [{
                    "id_contenido": c.get('id_contenido'),
                    "nombre": c.get('nombre'),
                    "precio_original": float(c.get('precio', 0.0)),
                    "porcentaje_descuento": float(c.get('descuento', 0.0)),
                    "precio_descuento": round(float(c.get('precio', 0.0)) * (1 - float(c.get('descuento', 0.0)) / 100), 2) if c.get('descuento', 0.0) else float(c.get('precio', 0.0)),
                    "tipo_contenido": self._determinar_tipo_contenido(c.get('formato')),
                    "autor": c.get('autor', ''),
                    "categoria": c.get('categoria', ''),
                    "descripcion": c.get('descripcion', ''),
                    "tamano": c.get('tamano', 0),
                    "formato": c.get('formato', ''),
                    "mime_type": c.get('mime_type', ''),
                    "calificacion": c.get('calificacion', 0.0),
                    "miniatura_url": f"/api/contenido/{c.get('id_contenido')}/miniatura"
                } for c in (contenidos or [])] if contenidos else []
            }
        except Exception:
            return {"success": False, "error": "Error al obtener contenidos", "data": []}

    # CTRL-PROM-007: Determina el tipo de contenido basado en su formato
    def _determinar_tipo_contenido(self, formato):
        if not formato:
            return 'otro'
        formato = formato.lower()
        if any(ext in formato for ext in ['mp4', 'avi', 'mov', 'video']):
            return 'video'
        elif any(ext in formato for ext in ['jpg', 'png', 'gif', 'jpeg', 'imagen', 'image']):
            return 'imagen'
        elif any(ext in formato for ext in ['mp3', 'wav', 'ogg', 'audio']):
            return 'audio'
        return 'otro'