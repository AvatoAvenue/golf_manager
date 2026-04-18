"""
API pública del módulo de torneos.
"""

import json
import frappe

RANKING_CACHE_TTL = 60  # segundos


#  Ranking

@frappe.whitelist(allow_guest=True)
def get_ranking(torneo, categoria=None, usar_cache=True):
	cache_key = f"golf_ranking_{torneo}" + (f"_{categoria}" if categoria else "")

	if usar_cache:
		cached = frappe.cache().get_value(cache_key)
		if cached:
			return json.loads(cached)

	if not frappe.has_permission("torneo de golf", "read", torneo):
		frappe.throw(frappe._("No tiene permiso para ver este torneo."), frappe.PermissionError)

	torneo_doc = frappe.get_doc("torneo de golf", torneo)

	filters = {"torneo": torneo}
	if categoria:
		filters["categoria"] = categoria

	participaciones = frappe.get_all(
		"participacion en torneo",
		filters=filters,
		fields=[
			"name",
			"jugador",
			"categoria",
			"handicap_inscripcion",
			"puntuacion_total_acumulada",
			"posicion_en_ranking",
		],
		order_by="posicion_en_ranking asc",
	)

	for p in participaciones:
		nombre = frappe.db.get_value("User", p.jugador, "full_name")
		p["nombre_jugador"] = nombre or p.jugador

	resultado = {
		"torneo_info": {
			"name":    torneo_doc.name,
			"nombre":  torneo_doc.nombre_del_torneo,
			"estado":  torneo_doc.estado,
			"campo":   torneo_doc.campo_de_golf,
			"formato": torneo_doc.formato,
		},
		"ranking": participaciones,
	}

	frappe.cache().set_value(
		cache_key, json.dumps(resultado, default=str), expires_in_sec=RANKING_CACHE_TTL
	)
	return resultado


@frappe.whitelist(allow_guest=True)
def get_ranking_por_categoria(torneo):
	categorias = frappe.db.sql(
		"""
		SELECT DISTINCT categoria
		FROM `tabparticipacion en torneo`
		WHERE torneo = %s
		ORDER BY categoria
		""",
		torneo,
		as_list=True,
	)

	resultado = {}
	for (cat,) in categorias:
		data = get_ranking(torneo, categoria=cat)
		resultado[cat] = data.get("ranking", [])

	return resultado


#  Puntuaciones

@frappe.whitelist()
def get_scorecard(torneo, jugador, ronda=None):
	"""
	Retorna la tarjeta de puntuación de un jugador.
	Nota: el campo golpes_totales fue eliminado del DocType; se usa
	      golpes_brutos como valor definitivo (penalizaciones se
	      calculan aparte desde la tabla hija).
	"""
	if not frappe.has_permission("torneo de golf", "read", torneo):
		frappe.throw(frappe._("No tiene permiso para ver este torneo."), frappe.PermissionError)

	filters_ronda = {"torneo": torneo}
	if ronda:
		filters_ronda["name"] = ronda

	rondas = frappe.get_all(
		"ronda",
		filters=filters_ronda,
		fields=["name", "numero_de_ronda", "fecha", "estado"],
		order_by="numero_de_ronda asc",
	)

	scorecard    = []
	golpes_total = 0
	puntos_total = 0

	for r in rondas:
		hoyos = frappe.get_all(
			"puntuacion por hoyo",
			filters={"ronda": r.name, "jugador": jugador},
			fields=[
				"numero_de_hoyo",
				"golpes_brutos",
				"par_del_hoyo",
				"puntos_stableford",
				"flag_penalizacion",
			],
			order_by="numero_de_hoyo asc",
		)

		# Penalizaciones por hoyo
		for hoyo in hoyos:
			pens = frappe.db.sql(
				"""
				SELECT motivo, golpes_adicionales
				FROM `tabpenalizacion`
				WHERE parent IN (
					SELECT name FROM `tabpuntuacion por hoyo`
					WHERE ronda = %s AND jugador = %s AND numero_de_hoyo = %s
				)
				""",
				(r.name, jugador, hoyo.numero_de_hoyo),
				as_dict=True,
			)
			hoyo["penalizaciones"] = pens
			# Calcular golpes totales al vuelo (brutos + penalizaciones)
			extra = sum(p.golpes_adicionales or 0 for p in pens)
			hoyo["golpes_totales"] = (hoyo.golpes_brutos or 0) + extra

		subtotal_golpes    = sum(h["golpes_totales"] for h in hoyos)
		subtotal_stableford = sum(h.get("puntos_stableford") or 0 for h in hoyos)
		golpes_total += subtotal_golpes
		puntos_total += subtotal_stableford

		scorecard.append({
			"ronda":               r.numero_de_ronda,
			"fecha":               str(r.fecha),
			"estado":              r.estado,
			"hoyos":               hoyos,
			"subtotal_golpes":     subtotal_golpes,
			"subtotal_stableford": subtotal_stableford,
		})

	nombre_jugador = frappe.db.get_value("User", jugador, "full_name") or jugador
	participacion  = frappe.db.get_value(
		"participacion en torneo",
		{"torneo": torneo, "jugador": jugador},
		["categoria", "handicap_inscripcion", "posicion_en_ranking"],
		as_dict=True,
	)

	return {
		"jugador":                jugador,
		"nombre_jugador":         nombre_jugador,
		"participacion":          participacion,
		"scorecard":              scorecard,
		"total_golpes":           golpes_total,
		"total_puntos_stableford": puntos_total,
	}


@frappe.whitelist()
def get_puntuaciones_ronda(ronda):
	"""Retorna todas las puntuaciones de una ronda, agrupadas por jugador."""
	if not frappe.has_permission("ronda", "read", ronda):
		frappe.throw(frappe._("No tiene permiso para ver esta ronda."), frappe.PermissionError)

	rows = frappe.db.sql(
		"""
		SELECT
			p.jugador,
			u.full_name          AS nombre_jugador,
			p.numero_de_hoyo,
			p.golpes_brutos,
			p.par_del_hoyo,
			p.puntos_stableford,
			p.flag_penalizacion,
			p.name
		FROM `tabpuntuacion por hoyo` p
		LEFT JOIN `tabUser` u ON u.name = p.jugador
		WHERE p.ronda = %s
		ORDER BY u.full_name, p.numero_de_hoyo
		""",
		ronda,
		as_dict=True,
	)

	por_jugador = {}
	for row in rows:
		jugador = row.jugador
		if jugador not in por_jugador:
			por_jugador[jugador] = {
				"jugador":       jugador,
				"nombre_jugador": row.nombre_jugador,
				"hoyos":         [],
				"total_golpes":  0,
				"total_stableford": 0,
			}
		por_jugador[jugador]["hoyos"].append(row)
		por_jugador[jugador]["total_golpes"]     += row.golpes_brutos or 0
		por_jugador[jugador]["total_stableford"] += row.puntos_stableford or 0

	return list(por_jugador.values())


#  Estadísticas

@frappe.whitelist()
def get_estadisticas_jugador(jugador):
	if not frappe.has_permission("participacion en torneo", "read"):
		frappe.throw(frappe._("No tiene permiso."), frappe.PermissionError)

	participaciones = frappe.db.sql(
		"""
		SELECT
			pt.name,
			pt.torneo,
			t.nombre_del_torneo,
			t.fecha_de_inicio,
			t.estado                  AS estado_torneo,
			pt.categoria,
			pt.handicap_inscripcion,
			pt.puntuacion_total_acumulada,
			pt.posicion_en_ranking,
			(SELECT COUNT(*) FROM `tabparticipacion en torneo`
			 WHERE torneo = pt.torneo) AS total_participantes
		FROM `tabparticipacion en torneo` pt
		JOIN `tabtorneo de golf` t ON t.name = pt.torneo
		WHERE pt.jugador = %s
		ORDER BY t.fecha_de_inicio DESC
		""",
		jugador,
		as_dict=True,
	)

	mejor_posicion     = min((p.posicion_en_ranking or 999 for p in participaciones), default=None)
	torneos_jugados    = len(participaciones)
	torneos_finalizados = [p for p in participaciones if p.estado_torneo == "Finalizado"]
	promedio_golpes    = (
		sum(p.puntuacion_total_acumulada or 0 for p in torneos_finalizados) / len(torneos_finalizados)
		if torneos_finalizados else None
	)

	return {
		"jugador":            jugador,
		"nombre_jugador":     frappe.db.get_value("User", jugador, "full_name"),
		"torneos_jugados":    torneos_jugados,
		"mejor_posicion":     mejor_posicion,
		"promedio_puntuacion": round(promedio_golpes, 2) if promedio_golpes is not None else None,
		"historial":          participaciones,
	}


#  Caché

@frappe.whitelist()
def invalidar_cache_ranking(torneo):
	if not frappe.has_permission("torneo de golf", "write", torneo):
		frappe.throw(frappe._("No tiene permiso."), frappe.PermissionError)
	frappe.cache().delete_key(f"golf_ranking_{torneo}")
	return frappe._("Caché invalidado para el torneo {0}.").format(torneo)
