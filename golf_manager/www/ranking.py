"""
Página pública de ranking /ranking
"""

import frappe

no_cache = 1


def get_context(context):
	context.no_cache = 1

	torneo_name = frappe.form_dict.get("torneo")

	if not torneo_name:
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

	context.ranking = frappe.db.sql(
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

	for p in context.ranking:
		if not p.get("nombre_jugador"):
			p["nombre_jugador"] = p["jugador"]

	categorias = sorted({p["categoria"] for p in context.ranking})
	context.ranking_por_categoria = {
		cat: [p for p in context.ranking if p["categoria"] == cat]
		for cat in categorias
	}

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
