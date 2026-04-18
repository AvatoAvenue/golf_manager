# Copyright (c) 2026, avato and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class jugadorengrupo(Document):
	"""
	Tabla hija de GrupoPorRonda.
	Vincula automáticamente el registro de ParticipacionEnTorneo del jugador
	cuando se guarda el grupo, para facilitar navegación y reportes.
	"""

	def validate(self):
		self._autocompletar_participacion()

	#  Completado automático

	def _autocompletar_participacion(self):
		"""
		Si el campo 'participacion' está vacío, lo busca y lo rellena
		automáticamente a partir del jugador y el torneo de la ronda padre.
		"""
		if self.participacion:
			return

		ronda = frappe.db.get_value(
			"grupo por ronda", self.parent, "ronda"
		)
		if not ronda:
			return

		torneo = frappe.db.get_value("ronda", ronda, "torneo")
		if not torneo:
			return

		participacion = frappe.db.get_value(
			"participacion en torneo",
			{"torneo": torneo, "jugador": self.jugador},
			"name",
		)
		if participacion:
			self.participacion = participacion
