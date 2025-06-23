# Controlador para gestionar las operaciones relacionadas con rankings
from domain.entities.ranking import Ranking

class ControladorRanking:
    def ranking_contenidos_mas_descargados(self):
        """Retorna el top 10 de contenidos más descargados con su posición anterior (si existe)"""
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
        except Exception as e:
            print(f"Error en ranking_contenidos_mas_descargados: {str(e)}")
            raise Exception("No se pudo obtener el ranking de descargas.")

    def ranking_contenidos_mejor_calificados(self):
        """Retorna el top 10 de contenidos con mejor promedio de calificación y su posición anterior"""
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
        except Exception as e:
            print(f"Error en ranking_contenidos_mejor_calificados: {str(e)}")
            raise Exception("No se pudo obtener el ranking de calificaciones.")

    def ranking_clientes_por_descargas(self):
        """Retorna los clientes ordenados por número de descargas en los últimos 6 meses"""
        try:
            resultados = Ranking.ranking_clientes_por_descargas()
            return [{
                "id_usuario": row[0],
                "username": row[1],
                "nombre": row[2],
                "apellido": row[3],
                "total_descargas": row[4],
                "ranking_anterior": "Nuevo"  # Por ahora siempre nuevo, se puede implementar después
            } for row in resultados]
        except Exception as e:
            print(f"Error en ranking_clientes_por_descargas: {str(e)}")
            raise Exception("No se pudo obtener el ranking de clientes.")

    def obtener_contenido_por_tipo(self, tipo_ranking):
        """Obtiene el ranking según el tipo especificado"""
        try:
            if tipo_ranking == 'descargas':
                return {
                    "success": True,
                    "data": self.ranking_contenidos_mas_descargados()
                }
            elif tipo_ranking == 'valoracion':
                return {
                    "success": True,
                    "data": self.ranking_contenidos_mejor_calificados()
                }
            elif tipo_ranking == 'clientes':
                return {
                    "success": True,
                    "data": self.ranking_clientes_por_descargas()
                }
            else:
                return {
                    "success": False,
                    "error": f"Tipo de ranking '{tipo_ranking}' no válido"
                }
        except Exception as e:
            print(f"Error en obtener_contenido_por_tipo: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
