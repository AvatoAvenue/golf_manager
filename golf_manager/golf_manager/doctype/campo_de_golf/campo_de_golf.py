# Copyright (c) 2026, avato and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class campodegolf(Document):
	#  Lifecycle hooks

	def validate(self):
		self._validar_unicidad_nombre()
		self._validar_numero_de_hoyos()
		self._validar_par_total()
		self._normalizar_nombre()

	def on_trash(self):
		self._verificar_sin_torneos_activos()

	#  Validaciones

	def _validar_unicidad_nombre(self):
		existente = frappe.db.get_value(
			"campo de golf",
			{
				"nombre": self.nombre,
				"name": ("!=", self.name),
			},
			"name",
		)
		if existente:
			frappe.throw(
				frappe._("Ya existe un campo de golf con el nombre '{0}'.").format(self.nombre)
			)

	def _validar_numero_de_hoyos(self):
		if self.numero_de_hoyos not in (9, 18, 27, 36):
			frappe.throw(
				frappe._(
					"El número de hoyos debe ser 9, 18, 27 o 36. Valor recibido: {0}."
				).format(self.numero_de_hoyos)
			)

	def _validar_par_total(self):
		"""
		Par razonable por hoyo: entre 3 y 5.
		Rango total aceptado: hoyos × 3 ≤ par_total ≤ hoyos × 5.
		"""
		minimo = self.numero_de_hoyos * 3
		maximo = self.numero_de_hoyos * 5
		if not (minimo <= self.par_total <= maximo):
			frappe.throw(
				frappe._(
					"El par total ({0}) está fuera del rango esperado para {1} hoyos ({2}–{3})."
				).format(self.par_total, self.numero_de_hoyos, minimo, maximo)
			)

	def _normalizar_nombre(self):
		self.nombre = self.nombre.strip()

	#  Protección de borrado

	def _verificar_sin_torneos_activos(self):
		torneos = frappe.get_all(
			"torneo de golf",
			filters={
				"campo_de_golf": self.name,
				"estado": ("in", ("Borrador", "Activo")),
			},
			fields=["nombre_del_torneo", "estado"],
			limit=5,
		)
		if torneos:
			nombres = ", ".join(t.nombre_del_torneo for t in torneos)
			frappe.throw(
				frappe._(
					"No se puede eliminar el campo '{0}' porque está asociado a los siguientes torneos: {1}."
				).format(self.nombre, nombres)
			)
