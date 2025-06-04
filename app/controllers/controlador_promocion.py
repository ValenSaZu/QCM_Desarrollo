# Controlador para gestionar las operaciones relacionadas con promociones
from domain.entities.promocion import Promocion
from datetime import datetime


class ControladorPromocion:

    def obtener_todas_promociones(self):
        """Obtiene todas las promociones disponibles"""
        promociones = Promocion.obtener_todas_promociones()
        return [{
            "id": promocion.id_promocion,
            "nombre": promocion.nombre,
            "porcentaje": promocion.descuento,
            "fecha_inicio": promocion.fecha_inicio.isoformat(),
            "fecha_fin": promocion.fecha_fin.isoformat()
        } for promocion in promociones]

    def obtener_promocion_por_id(self, id_promocion):
        """Obtiene los detalles de una promoción específica por su ID"""
        try:
            promocion = Promocion.obtener_promocion_por_id(id_promocion)
            if not promocion:
                return None

            contenidos = Promocion.obtener_contenido_promocion(id_promocion)
            return {
                "id": promocion.id_promocion,
                "nombre": promocion.nombre,
                "porcentaje": promocion.descuento,
                "fecha_inicio": promocion.fecha_inicio.isoformat() if hasattr(promocion.fecha_inicio,
                                                                              'isoformat') else promocion.fecha_inicio,
                "fecha_fin": promocion.fecha_fin.isoformat() if hasattr(promocion.fecha_fin,
                                                                        'isoformat') else promocion.fecha_fin,
                "contenidos": [{
                    "id": contenido.get('id_contenido'),
                    "nombre": contenido.get('nombre', ''),
                    "codigo": contenido.get('id_contenido', ''),
                    "formato": contenido.get('formato', ''),
                    "precio": 0
                } for contenido in (contenidos or [])]
            }
        except Exception as e:
            return None

    def agregar_promocion(self, form_data):
        """Crea una nueva promoción con sus contenidos asociados"""
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

            contenidos = form_data.getlist('contenidos[]')
            for id_contenido in contenidos:
                Promocion.agregar_contenido_a_promocion(id_promocion, int(id_contenido))

            return {"success": True, "message": "Promoción agregada correctamente"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def editar_promocion(self, id_promocion, form_data):
        """Actualiza una promoción existente y sus contenidos asociados"""
        try:
            nombre = form_data.get('nombre')
            porcentaje = float(form_data.get('porcentaje'))
            fecha_inicio = datetime.strptime(form_data.get('fecha_inicio'), '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(form_data.get('fecha_fin'), '%Y-%m-%d').date()

            Promocion.actualizar_promocion(
                id_promocion=id_promocion,
                nombre=nombre,
                descuento=porcentaje,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            contenidos_actuales = {c.get('id_contenido') for c in
                                   Promocion.obtener_contenido_promocion(id_promocion) or []}
            contenidos_nuevos = set()

            if 'contenidos[]' in form_data:
                if isinstance(form_data['contenidos[]'], list):
                    contenidos_nuevos = {int(id) for id in form_data['contenidos[]'] if id}
                elif form_data['contenidos[]']:
                    contenidos_nuevos = {int(form_data['contenidos[]'])}

            for id_contenido in contenidos_actuales - contenidos_nuevos:
                Promocion.eliminar_contenido_de_promocion(id_promocion, id_contenido)

            for id_contenido in contenidos_nuevos - contenidos_actuales:
                Promocion.agregar_contenido_a_promocion(id_promocion, id_contenido)

            return {"success": True, "message": "Promoción actualizada correctamente"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def eliminar_promocion(self, id_promocion):
        """Elimina una promoción del sistema"""
        try:
            Promocion.eliminar_promocion(id_promocion)
            return {"success": True, "message": "Promoción eliminada correctamente"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def obtener_contenidos_promocion(self, id_promocion):
        """Obtiene los contenidos asociados a una promoción específica"""
        try:
            promocion = self.obtener_promocion_por_id(id_promocion)
            if not promocion:
                return {"success": False, "error": "Promoción no encontrada"}, 404

            return {
                "success": True,
                "contenidos": promocion.get("contenidos", []),
                "promocion": {
                    "porcentaje": promocion.get("porcentaje", 0)
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}, 500