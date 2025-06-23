from domain.entities.ranking import Ranking

# G-007: Controlador para gestionar todas las operaciones de rankings
class ControladorRanking:

    # CTRL-RANK-001: Obtiene el top 10 de contenidos más descargados
    def ranking_contenidos_mas_descargados(self):
        try:
            resultados = Ranking.ranking_contenidos_mas_descargados()
            return [{
                "id_contenido": row[0],
                "nombre": row[1],
                "autor": row[2],
                "formato": row[3],
                "total_descargas": row[4],
                "ranking_anterior": row[5] if row[5] is not None else "Nuevo"
            } for row in resultados]
        except Exception:
            raise Exception("Error al obtener ranking de descargas")

    # CTRL-RANK-002: Obtiene el top 10 de contenidos mejor calificados
    def ranking_contenidos_mejor_calificados(self):
        try:
            resultados = Ranking.ranking_contenidos_mejor_calificados()
            return [{
                "id_contenido": row[0],
                "nombre": row[1],
                "autor": row[2],
                "formato": row[3],
                "promedio_calificacion": float(row[4]),
                "ranking_anterior": row[5] if row[5] is not None else "Nuevo"
            } for row in resultados]
        except Exception:
            raise Exception("Error al obtener ranking de calificaciones")

    # CTRL-RANK-003: Obtiene el ranking de clientes por descargas
    def ranking_clientes_por_descargas(self):
        try:
            resultados = Ranking.ranking_clientes_por_descargas()
            return [{
                "id_usuario": row[0],
                "username": row[1],
                "nombre": row[2],
                "apellido": row[3],
                "total_descargas": row[4],
                "ranking_anterior": "Nuevo"
            } for row in resultados]
        except Exception:
            raise Exception("Error al obtener ranking de clientes")

    # CTRL-RANK-004: Obtiene un ranking específico según el tipo solicitado
    def obtener_contenido_por_tipo(self, tipo_ranking):
        try:
            if tipo_ranking == 'descargas':
                return {"success": True, "data": self.ranking_contenidos_mas_descargados()}
            elif tipo_ranking == 'valoracion':
                return {"success": True, "data": self.ranking_contenidos_mejor_calificados()}
            elif tipo_ranking == 'clientes':
                return {"success": True, "data": self.ranking_clientes_por_descargas()}
            return {"success": False, "error": f"Tipo de ranking no válido: {tipo_ranking}"}
        except Exception as e:
            return {"success": False, "error": str(e)}