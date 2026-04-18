# Copyright (c) 2026, avato and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


# Separación mínima entre horas de salida del mismo torneo (minutos)
_MINUTOS_ENTRE_GRUPOS = 8


class grupoporronda(Document):
	#  Lifecycle hooks

	def validate(self):
		self._validar_ronda_no_completada()
		self._validar_jugadores_inscritos()
		self._validar_sin_jugadores_duplicados()
		self._validar_jugador_en_un_solo_grupo()
		self._validar_solapamiento_hora_salida()
		self._validar_minimo_jugadores()

	#  Validaciones

	def _validar_ronda_no_completada(self):
		estado = frappe.db.get_value("ronda", self.ronda, "estado")
		if estado == "Completada":
			frappe.throw(
				frappe._("No se pueden modificar grupos de una ronda ya completada.")
			)

	def _validar_jugadores_inscritos(self):
		"""
		Todos los jugadores del grupo deben estar inscritos en el torneo
		al que pertenece la ronda.
		"""
		torneo = frappe.db.get_value("ronda", self.ronda, "torneo")
		inscritos = frappe.get_all(
			"participacion en torneo",
			filters={"torneo": torneo},
			pluck="jugador",
		)
		for row in self.jugadores:
			if row.jugador not in inscritos:
				frappe.throw(
					frappe._(
						"El jugador {0} no está inscrito en el torneo. "
						"Inscríbalo primero en 'Participación en Torneo'."
					).format(row.jugador)
				)

	def _validar_sin_jugadores_duplicados(self):
		"""Evita que el mismo jugador aparezca dos veces en el mismo grupo."""
		vistos = set()
		for row in self.jugadores:
			if row.jugador in vistos:
				frappe.throw(
					frappe._("El jugador {0} aparece más de una vez en este grupo.").format(
						row.jugador
					)
				)
			vistos.add(row.jugador)

	def _validar_jugador_en_un_solo_grupo(self):
		"""
		Un jugador no puede estar en dos grupos distintos de la misma ronda.
		"""
		for row in self.jugadores:
			grupo_existente = frappe.db.sql(
				"""
				SELECT g.name, g.nombre_del_grupo
				FROM `tabgrupo por ronda` g
				JOIN `tabjugador en grupo` j ON j.parent = g.name
				WHERE g.ronda = %s
				  AND j.jugador = %s
				  AND g.name != %s
				LIMIT 1
				""",
				(self.ronda, row.jugador, self.name or ""),
				as_dict=True,
			)
			if grupo_existente:
				frappe.throw(
					frappe._(
						"El jugador {0} ya pertenece al grupo '{1}' en esta ronda."
					).format(row.jugador, grupo_existente[0].nombre_del_grupo)
				)

	def _validar_solapamiento_hora_salida(self):
		"""
		Dos grupos de la misma ronda no pueden tener la misma hora de salida,
		y debe haber al menos {_MINUTOS_ENTRE_GRUPOS} minutos entre salidas.
		"""
		grupos = frappe.get_all(
			"grupo por ronda",
			filters={
				"ronda": self.ronda,
				"name": ("!=", self.name or ""),
			},
			fields=["nombre_del_grupo", "hora_de_salida"],
		)

		from datetime import datetime, timedelta

		def _parse(t):
			if isinstance(t, str):
				return datetime.strptime(t, "%H:%M:%S")
			return datetime.combine(datetime.today(), t)

		mi_hora = _parse(str(self.hora_de_salida))
		margen = timedelta(minutes=_MINUTOS_ENTRE_GRUPOS)

		for g in grupos:
			otra_hora = _parse(str(g.hora_de_salida))
			diferencia = abs(mi_hora - otra_hora)
			if diferencia < margen:
				frappe.throw(
					frappe._(
						"La hora de salida se solapa con el grupo '{0}' ({1}). "
						"Debe haber al menos {2} minutos de separación entre salidas."
					).format(g.nombre_del_grupo, g.hora_de_salida, _MINUTOS_ENTRE_GRUPOS)
				)

	def _validar_minimo_jugadores(self):
		if not self.jugadores or len(self.jugadores) < 1:
			frappe.throw(frappe._("El grupo debe tener al menos un jugador."))
		if len(self.jugadores) > 4:
			frappe.throw(
				frappe._("Un grupo no puede tener más de 4 jugadores. Actual: {0}.").format(
					len(self.jugadores)
				)
			)
