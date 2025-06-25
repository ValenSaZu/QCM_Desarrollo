from domain.entities.ranking import Ranking

# G-007: Controlador para gestión de rankings que incluye:
# - Rankings de contenidos por descargas y calificaciones
# - Ranking de clientes más activos
# - Obtención de rankings por tipo
# - Comparación con rankings anteriores
class ControladorRanking:

    # CTRL-RANK-001: Obtiene el top 10 de contenidos más descargados
    # Retorna:
    #   list[dict]: Lista ordenada de contenidos con estructura:
    #       {
    #           "id_contenido": int,
    #           "nombre": str,
    #           "autor": str,
    #           "formato": str,
    #           "total_descargas": int,
    #           "ranking_anterior": int|"Nuevo" (posición en ranking anterior)
    #       }
    # Excepciones:
    #   Exception: Si falla la consulta a la base de datos
    # Nota: Incluye comparación con ranking anterior para análisis de tendencias
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
    # Retorna:
    #   list[dict]: Lista ordenada de contenidos con estructura:
    #       {
    #           "id_contenido": int,
    #           "nombre": str,
    #           "autor": str,
    #           "formato": str,
    #           "promedio_calificacion": float (1-10),
    #           "ranking_anterior": int|"Nuevo" (posición en ranking anterior)
    #       }
    # Excepciones:
    #   Exception: Si falla la consulta a la base de datos
    # Nota: Calificaciones normalizadas a escala de 1-10
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

    # CTRL-RANK-003: Obtiene el top 10 de clientes con más descargas
    # Retorna:
    #   list[dict]: Lista ordenada de clientes con estructura:
    #       {
    #           "id_usuario": int,
    #           "username": str,
    #           "nombre": str,
    #           "apellido": str,
    #           "total_descargas": int,
    #           "ranking_anterior": "Nuevo" (implementación futura)
    #       }
    # Excepciones:
    #   Exception: Si falla la consulta a la base de datos
    # Nota: Actualmente marca todos como "Nuevo" (pendiente implementar comparación)
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

    # CTRL-RANK-004: Obtiene un ranking específico según tipo solicitado
    # Parámetros:
    #   tipo_ranking (str): Tipo de ranking a obtener:
    #       'descargas' - Contenidos más descargados
    #       'valoracion' - Contenidos mejor calificados
    #       'clientes' - Clientes con más descargas
    # Retorna:
    #   dict: {
    #       "success": bool,
    #       "data": list[dict] (según ranking solicitado),
    #       "error": str (si success=False)
    #   }
    # Validaciones:
    #   - Tipo de ranking debe ser válido
    # Rutas:
    #   - Delega a métodos específicos según tipo de ranking
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