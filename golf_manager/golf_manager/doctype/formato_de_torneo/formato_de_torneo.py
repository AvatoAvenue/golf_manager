# Copyright (c) 2026, avato and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


# Combinaciones válidas de formato y criterio de desempate
_CRITERIOS_VALIDOS = {
	"Stroke Play": (
		"Mejor última ronda",
		"Menor hándicap",
		"Mejor última ronda, luego menor hándicap",
	),
	"Match Play": (
		"Mejor última ronda",
		"Menor hándicap",
		"Mejor última ronda, luego menor hándicap",
	),
	"Stableford": (
		"Mejor última ronda",
		"Menor hándicap",
		"Mejor última ronda, luego menor hándicap",
	),
}


class formatodetorneo(Document):
	#  Lifecycle hooks

	def validate(self):
		self._validar_unicidad_nombre()
		self._validar_coherencia_formato_criterio()
		self._normalizar_nombre()

	def on_trash(self):
		self._verificar_sin_torneos()

	#  Validaciones

	def _validar_unicidad_nombre(self):
		existente = frappe.db.get_value(
			"formato de torneo",
			{
				"nombre": self.nombre,
				"name": ("!=", self.name),
			},
			"name",
		)
		if existente:
			frappe.throw(
				frappe._("Ya existe un formato de torneo con el nombre '{0}'.").format(self.nombre)
			)

	def _validar_coherencia_formato_criterio(self):
		criterios = _CRITERIOS_VALIDOS.get(self.tipo_de_formato, ())
		if self.criterio_de_desempate not in criterios:
			frappe.throw(
				frappe._(
					"El criterio de desempate '{0}' no es compatible con el formato '{1}'."
				).format(self.criterio_de_desempate, self.tipo_de_formato)
			)

	def _normalizar_nombre(self):
		self.nombre = self.nombre.strip()

	#  Protección de borrado

	def _verificar_sin_torneos(self):
		torneos = frappe.get_all(
			"torneo de golf",
			filters={"formato": self.name},
			fields=["nombre_del_torneo"],
			limit=5,
		)
		if torneos:
			nombres = ", ".join(t.nombre_del_torneo for t in torneos)
			frappe.throw(
				frappe._(
					"No se puede eliminar el formato '{0}' porque está en uso por los siguientes torneos: {1}."
				).format(self.nombre, nombres)
			)
