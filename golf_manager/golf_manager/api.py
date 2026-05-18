"""
API publica del modulo de torneos.
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
	Retorna la tarjeta de puntuacion de un jugador.
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
			extra = sum(p.golpes_adicionales or 0 for p in pens)
			hoyo["golpes_totales"] = (hoyo.golpes_brutos or 0) + extra

		subtotal_golpes     = sum(h["golpes_totales"] for h in hoyos)
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
		"jugador":                 jugador,
		"nombre_jugador":          nombre_jugador,
		"participacion":           participacion,
		"scorecard":               scorecard,
		"total_golpes":            golpes_total,
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
				"jugador":          jugador,
				"nombre_jugador":   row.nombre_jugador,
				"hoyos":            [],
				"total_golpes":     0,
				"total_stableford": 0,
			}
		por_jugador[jugador]["hoyos"].append(row)
		por_jugador[jugador]["total_golpes"]     += row.golpes_brutos or 0
		por_jugador[jugador]["total_stableford"] += row.puntos_stableford or 0

	return list(por_jugador.values())


#  Captura masiva de puntuaciones

@frappe.whitelist()
def get_datos_captura_torneo(torneo):
	"""
	Retorna en una sola llamada todo lo necesario para la grilla de captura:
	  - rondas del torneo
	  - participantes con nombre, categoria y handicap
	  - puntuaciones ya registradas para pre-poblar la grilla
	  - penalizaciones de cada puntuacion
	  - pares por hoyo inferidos de registros existentes (default 4)
	"""
	if not frappe.has_permission("torneo de golf", "read", torneo):
		frappe.throw(frappe._("No tiene permiso."), frappe.PermissionError)

	rondas = frappe.get_all(
		"ronda",
		filters={"torneo": torneo},
		fields=["name", "numero_de_ronda", "fecha", "estado"],
		order_by="numero_de_ronda asc",
	)

	participantes = frappe.db.sql(
		"""
		SELECT pt.jugador, u.full_name AS nombre, pt.categoria, pt.handicap_inscripcion
		FROM `tabparticipacion en torneo` pt
		LEFT JOIN `tabUser` u ON u.name = pt.jugador
		WHERE pt.torneo = %s
		ORDER BY pt.categoria, u.full_name
		""",
		torneo,
		as_dict=True,
	)

	ronda_names  = [r.name for r in rondas]
	puntuaciones = []
	if ronda_names:
		puntuaciones = frappe.db.sql(
			"""
			SELECT p.name, p.ronda, p.jugador, p.numero_de_hoyo,
			       p.golpes_brutos, p.par_del_hoyo, p.puntos_stableford,
			       p.flag_penalizacion
			FROM `tabpuntuacion por hoyo` p
			WHERE p.ronda IN %(rondas)s
			ORDER BY p.jugador, p.numero_de_hoyo
			""",
			{"rondas": ronda_names},
			as_dict=True,
		)

	pun_names = [p.name for p in puntuaciones]
	pens_map  = {}
	if pun_names:
		pens_raw = frappe.db.sql(
			"""
			SELECT parent, motivo, golpes_adicionales
			FROM `tabpenalizacion`
			WHERE parent IN %(names)s
			""",
			{"names": pun_names},
			as_dict=True,
		)
		for pen in pens_raw:
			pens_map.setdefault(pen.parent, []).append({
				"motivo":             pen.motivo,
				"golpes_adicionales": pen.golpes_adicionales,
			})

	for p in puntuaciones:
		p["penalizaciones"] = pens_map.get(p.name, [])

	# Pares por hoyo: usar valores de registros existentes o default 4
	par_por_hoyo = {h: 4 for h in range(1, 19)}
	for p in puntuaciones:
		if p.par_del_hoyo and p.numero_de_hoyo:
			par_por_hoyo[p.numero_de_hoyo] = p.par_del_hoyo

	return {
		"rondas":        rondas,
		"participantes": participantes,
		"puntuaciones":  puntuaciones,
		"par_por_hoyo":  par_por_hoyo,
	}


@frappe.whitelist()
def guardar_fila_puntuaciones(ronda, jugador, hoyos_json):
	"""
	Crea o actualiza los registros puntuacion por hoyo para un jugador
	en una ronda. Los hoyos sin golpes_brutos se omiten.

	hoyos_json: lista JSON con objetos:
	  {
	    "numero_de_hoyo": 1,
	    "golpes_brutos": 4,
	    "par_del_hoyo": 4,
	    "penalizaciones": [{"motivo": "Bola perdida", "golpes_adicionales": 1}]
	  }
	"""
	if not frappe.has_permission("puntuacion por hoyo", "write"):
		frappe.throw(frappe._("No tiene permiso para registrar puntuaciones."), frappe.PermissionError)

	estado_ronda = frappe.db.get_value("ronda", ronda, "estado")
	if estado_ronda == "Completada":
		frappe.throw(frappe._("No se pueden modificar puntuaciones de una ronda completada."))

	hoyos     = json.loads(hoyos_json) if isinstance(hoyos_json, str) else hoyos_json
	guardados = []
	omitidos  = []

	for hoyo in hoyos:
		numero = int(hoyo.get("numero_de_hoyo", 0))
		golpes = hoyo.get("golpes_brutos")
		par    = hoyo.get("par_del_hoyo") or 4
		pens   = hoyo.get("penalizaciones") or []

		if not numero or not golpes:
			omitidos.append(numero)
			continue

		golpes = int(golpes)
		par    = int(par)

		existente = frappe.db.get_value(
			"puntuacion por hoyo",
			{"ronda": ronda, "jugador": jugador, "numero_de_hoyo": numero},
			"name",
		)

		if existente:
			doc = frappe.get_doc("puntuacion por hoyo", existente)
		else:
			doc                = frappe.new_doc("puntuacion por hoyo")
			doc.ronda          = ronda
			doc.jugador        = jugador
			doc.numero_de_hoyo = numero

		doc.golpes_brutos     = golpes
		doc.par_del_hoyo      = par
		doc.flag_penalizacion = 1 if pens else 0
		doc.set("penalizaciones", [])

		for p in pens:
			doc.append("penalizaciones", {
				"motivo":             p.get("motivo", "Otro"),
				"golpes_adicionales": int(p.get("golpes_adicionales") or 1),
			})

		doc.flags.ignore_permissions = True
		doc.save()
		guardados.append(numero)

	frappe.db.commit()
	return {
		"guardados": guardados,
		"omitidos":  omitidos,
		"jugador":   jugador,
		"ronda":     ronda,
	}


#  Estadisticas

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

	mejor_posicion      = min((p.posicion_en_ranking or 999 for p in participaciones), default=None)
	torneos_jugados     = len(participaciones)
	torneos_finalizados = [p for p in participaciones if p.estado_torneo == "Finalizado"]
	promedio_golpes     = (
		sum(p.puntuacion_total_acumulada or 0 for p in torneos_finalizados) / len(torneos_finalizados)
		if torneos_finalizados else None
	)

	return {
		"jugador":             jugador,
		"nombre_jugador":      frappe.db.get_value("User", jugador, "full_name"),
		"torneos_jugados":     torneos_jugados,
		"mejor_posicion":      mejor_posicion,
		"promedio_puntuacion": round(promedio_golpes, 2) if promedio_golpes is not None else None,
		"historial":           participaciones,
	}


#  Busqueda de jugadores

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_jugadores_de_ronda(doctype, txt, searchfield, start, page_len, filters):
	"""
	Query de busqueda para el campo jugador en puntuacion por hoyo.
	Retorna solo los usuarios inscritos en el torneo de la ronda indicada.
	"""
	ronda = filters.get("ronda") if filters else None
	if not ronda:
		return []

	torneo = frappe.db.get_value("ronda", ronda, "torneo")
	if not torneo:
		return []

	return frappe.db.sql(
		"""
		SELECT u.name, u.full_name
		FROM `tabUser` u
		JOIN `tabparticipacion en torneo` pt ON pt.jugador = u.name
		WHERE pt.torneo = %(torneo)s
		  AND (
		      u.name LIKE %(txt)s
		      OR u.full_name LIKE %(txt)s
		  )
		ORDER BY u.full_name
		LIMIT %(start)s, %(page_len)s
		""",
		{
			"torneo":   torneo,
			"txt":      f"%{txt}%",
			"start":    start,
			"page_len": page_len,
		},
	)


#  Cache

@frappe.whitelist()
def invalidar_cache_ranking(torneo):
	if not frappe.has_permission("torneo de golf", "write", torneo):
		frappe.throw(frappe._("No tiene permiso."), frappe.PermissionError)
	frappe.cache().delete_key(f"golf_ranking_{torneo}")
	return frappe._("Cache invalidado para el torneo {0}.").format(torneo)
