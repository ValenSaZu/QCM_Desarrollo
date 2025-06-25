from infrastructure.bd.conexion import obtener_conexion
from datetime import datetime, timedelta

# BD-010: Entidad para gestionar operaciones de rankings y estadísticas que incluye:
# - Generación de rankings de contenidos más descargados
# - Generación de rankings de contenidos mejor calificados
# - Generación de rankings de clientes más activos
# - Consulta de posiciones anteriores en rankings
# - Manejo de periodos temporales para estadísticas
class Ranking:
    # ENT-RANK-001: Obtiene ranking de los contenidos más descargados
    # Retorna:
    #   list[dict]: Lista de diccionarios con información de contenidos y sus descargas
    # Excepciones:
    #   - Lanza excepción si hay error en la consulta
    # Características:
    #   - Limita resultados a top 10
    #   - Incluye posición anterior en el ranking
    #   - Ordena por total de descargas descendente
    #   - Muestra formato del contenido
    @classmethod
    def ranking_contenidos_mas_descargados(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                SELECT c.id_contenido,
                       c.nombre,
                       c.autor,
                       t.formato,
                       COUNT(d.id_descarga) AS total_descargas,
                       rc_anterior.posicion_actual AS posicion_anterior
                FROM CONTENIDO c
                JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                JOIN DESCARGA d ON c.id_contenido = d.id_contenido
                LEFT JOIN (
                    SELECT rc.id_contenido, r.posicion_actual
                    FROM RANKING_CONTENIDO rc
                    JOIN RANKING r ON r.id_ranking = rc.id_ranking
                    WHERE r.tipo_ranking = 'contenido'
                      AND r.tipo = 'descargas'
                      AND r.fecha = CURRENT_DATE - INTERVAL '7 days'
                ) AS rc_anterior ON rc_anterior.id_contenido = c.id_contenido
                GROUP BY c.id_contenido, c.nombre, c.autor, t.formato, rc_anterior.posicion_actual
                ORDER BY total_descargas DESC
                LIMIT 10;
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error al obtener ranking de descargas: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    # ENT-RANK-002: Obtiene ranking de los contenidos mejor calificados
    # Retorna:
    #   list[dict]: Lista de diccionarios con información de contenidos y sus calificaciones
    # Excepciones:
    #   - Lanza excepción si hay error en la consulta
    # Características:
    #   - Limita resultados a top 10
    #   - Incluye posición anterior en el ranking
    #   - Ordena por promedio de calificación descendente
    #   - Requiere al menos 1 valoración
    #   - Muestra formato del contenido
    @classmethod
    def ranking_contenidos_mejor_calificados(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            query = """
                SELECT c.id_contenido,
                       c.nombre,
                       c.autor,
                       t.formato,
                       ROUND(AVG(v.puntuacion) * 10, 1) AS promedio,
                       rc_anterior.posicion_actual AS posicion_anterior
                FROM CONTENIDO c
                JOIN TIPO_ARCHIVO t ON c.id_tipo_archivo = t.id_tipo_archivo
                JOIN VALORACION v ON c.id_contenido = v.id_contenido
                LEFT JOIN (
                    SELECT rc.id_contenido, r.posicion_actual
                    FROM RANKING_CONTENIDO rc
                    JOIN RANKING r ON r.id_ranking = rc.id_ranking
                    WHERE r.tipo_ranking = 'contenido'
                      AND r.tipo = 'calificacion'
                      AND r.fecha = CURRENT_DATE - INTERVAL '7 days'
                ) AS rc_anterior ON rc_anterior.id_contenido = c.id_contenido
                GROUP BY c.id_contenido, c.nombre, c.autor, t.formato, rc_anterior.posicion_actual
                HAVING COUNT(v.id_valoracion) >= 1
                ORDER BY promedio DESC
                LIMIT 10;
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error al obtener ranking de calificaciones: {str(e)}")
        finally:
            cursor.close()
            conexion.close()

    # ENT-RANK-003: Obtiene ranking de clientes por cantidad de descargas
    # Retorna:
    #   list[dict]: Lista de diccionarios con información de clientes y sus descargas
    # Excepciones:
    #   - Lanza excepción si hay error en la consulta
    # Características:
    #   - Considera solo descargas de los últimos 6 meses
    #   - Ordena por total de descargas descendente
    #   - Incluye información básica del cliente
    @classmethod
    def ranking_clientes_por_descargas(cls):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            seis_meses_atras = datetime.now() - timedelta(days=180)

            query = """
                SELECT u.id_usuario,
                       u.username,
                       u.nombre,
                       u.apellido,
                       COUNT(d.id_descarga) AS total_descargas
                FROM USUARIO u
                JOIN CLIENTE c ON u.id_usuario = c.id_usuario
                JOIN DESCARGA d ON d.id_usuario = c.id_usuario
                WHERE d.fecha_y_hora >= %s
                GROUP BY u.id_usuario, u.username, u.nombre, u.apellido
                ORDER BY total_descargas DESC;
            """
            cursor.execute(query, (seis_meses_atras,))
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error al obtener ranking de clientes por descargas: {str(e)}")
        finally:
            cursor.close()
            conexion.close()