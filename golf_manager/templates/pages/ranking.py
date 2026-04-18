"""
Controlador de la página pública de ranking.
URL: /ranking?torneo=<name>

La página es accesible sin autenticación.
"""

import frappe

# Declarar la página como pública para que Frappe no exija login
no_cache = 1


def get_context(context):
    # Marcar la página como pública
    context.no_cache = 1

    torneo_name = frappe.form_dict.get("torneo")

    if not torneo_name:
        # Mostrar el torneo activo más reciente si no se especifica uno
        torneo_name = frappe.db.get_value(
            "torneo de golf",
            {"estado": "Activo", "docstatus": 1},
            "name",
            order_by="fecha_de_inicio desc",
        )

    if not torneo_name:
        context.sin_torneo = True
        context.title = "Ranking de torneos"
        return

    # Consulta directa en BD para evitar comprobaciones de permisos en
    # contexto de Guest, ya que los torneos son datos públicos de lectura
    torneo = frappe.db.get_value(
        "torneo de golf",
        torneo_name,
        [
            "name", "nombre_del_torneo", "campo_de_golf",
            "fecha_de_inicio", "fecha_de_fin", "estado", "formato",
        ],
        as_dict=True,
    )

    if not torneo:
        context.sin_torneo = True
        context.title = "Ranking de torneos"
        return

    context.torneo = torneo
    context.title = f"Ranking — {torneo.nombre_del_torneo}"

    # Ranking general
    ranking = frappe.db.sql(
        """
        SELECT
            pt.jugador,
            pt.categoria,
            pt.handicap_inscripcion,
            pt.puntuacion_total_acumulada,
            pt.posicion_en_ranking,
            u.full_name AS nombre_jugador
        FROM `tabparticipacion en torneo` pt
        LEFT JOIN `tabUser` u ON u.name = pt.jugador
        WHERE pt.torneo = %s
        ORDER BY pt.posicion_en_ranking ASC
        """,
        torneo_name,
        as_dict=True,
    )

    # Rellenar nombre si viene vacío
    for p in ranking:
        if not p.get("nombre_jugador"):
            p["nombre_jugador"] = p["jugador"]

    context.ranking = ranking

    # Ranking por categoría
    categorias = sorted({p["categoria"] for p in ranking})
    context.ranking_por_categoria = {
        cat: [p for p in ranking if p["categoria"] == cat]
        for cat in categorias
    }

    # Lista de torneos activos o finalizados para el selector
    context.torneos_activos = frappe.db.sql(
        """
        SELECT name, nombre_del_torneo, estado
        FROM `tabtorneo de golf`
        WHERE estado IN ('Activo', 'Finalizado')
          AND docstatus = 1
        ORDER BY fecha_de_inicio DESC
        LIMIT 20
        """,
        as_dict=True,
    )
