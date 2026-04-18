# Copyright (c) 2026, avato and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from golf_manager.golf_manager.doctype.puntuacion_por_hoyo.puntuacion_por_hoyo import (
	_calcular_total_jugador,
	_recalcular_rankings,
)


class participacionentorneo(Document):
	#  Lifecycle hooks

	def validate(self):
		self._validar_unicidad()
		self._validar_handicap()
		self._validar_torneo_activo()

	def after_insert(self):
		_recalcular_rankings(self.torneo)

	def on_update(self):
		_recalcular_rankings(self.torneo)

	def on_trash(self):
		_recalcular_rankings(self.torneo)

	#  Validaciones

	def _validar_unicidad(self):
		existente = frappe.db.get_value(
			"participacion en torneo",
			{
				"torneo": self.torneo,
				"jugador": self.jugador,
				"name": ("!=", self.name),
			},
			"name",
		)
		if existente:
			frappe.throw(
				frappe._("El jugador {0} ya está inscrito en el torneo {1}.").format(
					self.jugador, self.torneo
				)
			)

	def _validar_handicap(self):
		if self.handicap_inscripcion is None:
			frappe.throw(frappe._("El hándicap de inscripción es obligatorio."))
		if not (-10 <= self.handicap_inscripcion <= 54):
			frappe.throw(
				frappe._("El hándicap debe estar entre -10 y 54. Valor recibido: {0}").format(
					self.handicap_inscripcion
				)
			)

	def _validar_torneo_activo(self):
		estado = frappe.db.get_value("torneo de golf", self.torneo, "estado")
		if estado == "Finalizado":
			frappe.throw(
				frappe._("No se puede inscribir jugadores en un torneo finalizado.")
			)

	#  Métodos públicos

	def recalcular_total(self):
		"""
		Recalcula la puntuación total desde las puntuaciones por hoyo
		y persiste el resultado. Útil para llamadas manuales o desde API.
		"""
		total = _calcular_total_jugador(self.torneo, self.jugador)
		self.db_set("puntuacion_total_acumulada", total, update_modified=False)
		return total
