# Copyright (c) 2026, avato and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class puntuacionporhoyo(Document):
	#  Lifecycle hooks

	def validate(self):
		self._validar_numero_de_hoyo()
		self._validar_golpes()
		self._calcular_puntos_stableford()

	def on_update(self):
		self._actualizar_total_participacion()

	def on_trash(self):
		self._actualizar_total_participacion()

	#  Validaciones

	def _validar_numero_de_hoyo(self):
		if not (1 <= self.numero_de_hoyo <= 18):
			frappe.throw(
				frappe._("El número de hoyo debe estar entre 1 y 18. Valor recibido: {0}").format(
					self.numero_de_hoyo
				)
			)

	def _validar_golpes(self):
		if self.golpes_brutos is None or self.golpes_brutos < 1:
			frappe.throw(frappe._("Los golpes brutos deben ser al menos 1."))

		if self.par_del_hoyo is None or self.par_del_hoyo < 3:
			frappe.throw(frappe._("El par del hoyo debe ser al menos 3."))

		existente = frappe.db.get_value(
			"puntuacion por hoyo",
			{
				"ronda":          self.ronda,
				"jugador":        self.jugador,
				"numero_de_hoyo": self.numero_de_hoyo,
				"name":           ("!=", self.name),
			},
			"name",
		)
		if existente:
			frappe.throw(
				frappe._(
					"Ya existe una puntuación para el jugador {0} en el hoyo {1} de esta ronda."
				).format(self.jugador, self.numero_de_hoyo)
			)

	#  Cálculos

	def _calcular_puntos_stableford(self):
		"""
		Stableford estándar: puntos = max(0, par + 2 - golpes_brutos)
		Para Stroke Play y Match Play el campo se deja en 0.
		"""
		if self._obtener_tipo_formato() == "Stableford":
			self.puntos_stableford = max(0, (self.par_del_hoyo or 4) + 2 - (self.golpes_brutos or 0))
		else:
			self.puntos_stableford = 0

	def _obtener_tipo_formato(self):
		try:
			torneo = frappe.db.get_value("ronda", self.ronda, "torneo")
			if not torneo:
				return "Stroke Play"
			formato = frappe.db.get_value("torneo de golf", torneo, "formato")
			if not formato:
				return "Stroke Play"
			return frappe.db.get_value("formato de torneo", formato, "tipo_de_formato") or "Stroke Play"
		except Exception:
			return "Stroke Play"

	#  Propagación a Participación en Torneo

	def _actualizar_total_participacion(self):
		torneo = self._obtener_torneo()
		if not torneo:
			return

		participacion = frappe.db.get_value(
			"participacion en torneo",
			{"torneo": torneo, "jugador": self.jugador},
			"name",
		)
		if not participacion:
			return

		total = _calcular_total_jugador(torneo, self.jugador)
		frappe.db.set_value(
			"participacion en torneo",
			participacion,
			"puntuacion_total_acumulada",
			total,
			update_modified=False,
		)
		frappe.cache().delete_key(f"golf_ranking_{torneo}")
		_recalcular_rankings(torneo)

	def _obtener_torneo(self):
		try:
			return frappe.db.get_value("ronda", self.ronda, "torneo")
		except Exception:
			return None


#  Funciones reutilizables exportadas

def _calcular_total_jugador(torneo, jugador):
	"""
	Suma la puntuación de todas las rondas del torneo para un jugador.
	Stableford: suma puntos_stableford.
	Stroke Play / Match Play: suma golpes_brutos.
	"""
	formato_tipo = _obtener_tipo_formato_torneo(torneo)

	rondas = frappe.get_all("ronda", filters={"torneo": torneo}, pluck="name")
	if not rondas:
		return 0.0

	if formato_tipo == "Stableford":
		result = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(puntos_stableford), 0)
			FROM `tabpuntuacion por hoyo`
			WHERE ronda IN %(rondas)s AND jugador = %(jugador)s
			""",
			{"rondas": rondas, "jugador": jugador},
		)
	else:
		result = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(COALESCE(golpes_brutos, 0)), 0)
			FROM `tabpuntuacion por hoyo`
			WHERE ronda IN %(rondas)s AND jugador = %(jugador)s
			""",
			{"rondas": rondas, "jugador": jugador},
		)

	return float(result[0][0]) if result else 0.0


def _obtener_tipo_formato_torneo(torneo):
	try:
		formato = frappe.db.get_value("torneo de golf", torneo, "formato")
		return frappe.db.get_value("formato de torneo", formato, "tipo_de_formato") or "Stroke Play"
	except Exception:
		return "Stroke Play"


def _recalcular_rankings(torneo):
	"""
	Recalcula las posiciones de todos los participantes de un torneo.
	"""
	formato_name = frappe.db.get_value("torneo de golf", torneo, "formato")
	formato      = frappe.get_doc("formato de torneo", formato_name) if formato_name else None
	tipo         = formato.tipo_de_formato      if formato else "Stroke Play"
	criterio     = formato.criterio_de_desempate if formato else "Mejor última ronda"

	participaciones = frappe.get_all(
		"participacion en torneo",
		filters={"torneo": torneo},
		fields=["name", "jugador", "puntuacion_total_acumulada", "handicap_inscripcion"],
	)
	if not participaciones:
		return

	ultima_ronda = frappe.db.get_value(
		"ronda", {"torneo": torneo}, "name", order_by="numero_de_ronda desc"
	)

	scores_ultima = {}
	if ultima_ronda:
		rows = frappe.db.sql(
			"""
			SELECT jugador,
			       COALESCE(SUM(puntos_stableford), 0) AS pts_stableford,
			       COALESCE(SUM(COALESCE(golpes_brutos, 0)), 0) AS golpes
			FROM `tabpuntuacion por hoyo`
			WHERE ronda = %s
			GROUP BY jugador
			""",
			ultima_ronda,
			as_dict=True,
		)
		for r in rows:
			scores_ultima[r.jugador] = r

	def sort_key(p):
		total  = p.puntuacion_total_acumulada or 0.0
		hcp    = p.handicap_inscripcion or 0.0
		sr     = scores_ultima.get(p.jugador, {})

		if tipo == "Stableford":
			primary      = -total
			score_ultima = -(sr.get("pts_stableford") or 0)
		else:
			primary      = total
			score_ultima = sr.get("golpes") or 999

		if criterio == "Mejor última ronda":
			return (primary, score_ultima)
		elif criterio == "Menor hándicap":
			return (primary, hcp)
		else:
			return (primary, score_ultima, hcp)

	participaciones.sort(key=sort_key)

	posicion_actual = 1
	for i, p in enumerate(participaciones):
		if i > 0 and sort_key(p) == sort_key(participaciones[i - 1]):
			posicion = participaciones[i - 1]._posicion
		else:
			posicion = posicion_actual
		p._posicion     = posicion
		posicion_actual = i + 2

	for p in participaciones:
		frappe.db.set_value(
			"participacion en torneo",
			p.name,
			"posicion_en_ranking",
			p._posicion,
			update_modified=False,
		)
