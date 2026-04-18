# Copyright (c) 2026, avato and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class torneodegolf(Document):
	#  Lifecycle hooks

	def autoname(self):
		"""
		Genera el name como: "<nombre_del_torneo> - YYYY-MM"
		Se hace aquí en lugar de en el campo autoname del JSON porque
		Frappe no interpreta formatos de fecha dentro de autoname field.
		"""
		if self.nombre_del_torneo and self.fecha_de_inicio:
			fecha = getdate(self.fecha_de_inicio)
			sufijo = fecha.strftime("%Y-%m")
			self.name = f"{self.nombre_del_torneo} - {sufijo}"
		else:
			# Fallback por si alguno de los campos aún no está seteado
			self.name = self.nombre_del_torneo

	def validate(self):
		self._validar_fechas()
		self._sincronizar_estado_con_docstatus()

	def on_submit(self):
		self.db_set("estado", "Activo")

	def on_cancel(self):
		self.db_set("estado", "Borrador")

	def on_update(self):
		frappe.cache().delete_key(f"golf_ranking_{self.name}")

	#  Validaciones

	def _validar_fechas(self):
		if self.fecha_de_fin < self.fecha_de_inicio:
			frappe.throw(
				frappe._("La fecha de fin no puede ser anterior a la fecha de inicio.")
			)
		if self.numero_de_rondas < 1:
			frappe.throw(frappe._("El torneo debe tener al menos una ronda."))

	def _sincronizar_estado_con_docstatus(self):
		"""
		Evita inconsistencias entre el campo estado y el docstatus de Frappe.
		Un torneo Borrador no puede estar en estado Activo si no está 'submitted'.
		"""
		if self.docstatus == 0 and self.estado == "Activo":
			self.estado = "Borrador"

	#  Métodos públicos

	@frappe.whitelist()
	def finalizar(self):
		"""
		Marca el torneo como Finalizado y congela las puntuaciones.
		Solo puede llamarse sobre un torneo Activo (docstatus=1).
		"""
		if self.docstatus != 1:
			frappe.throw(frappe._("Solo se puede finalizar un torneo activo (enviado)."))
		if self.estado == "Finalizado":
			frappe.throw(frappe._("El torneo ya está finalizado."))

		rondas_incompletas = frappe.get_all(
			"ronda",
			filters={"torneo": self.name, "estado": ("!=", "Completada")},
			fields=["name", "numero_de_ronda"],
		)
		if rondas_incompletas:
			numeros = ", ".join(str(r.numero_de_ronda) for r in rondas_incompletas)
			frappe.throw(
				frappe._(
					"Las siguientes rondas no están completadas: {0}. "
					"Complete todas las rondas antes de finalizar el torneo."
				).format(numeros)
			)

		self.db_set("estado", "Finalizado")
		frappe.cache().delete_key(f"golf_ranking_{self.name}")
		return frappe._("Torneo finalizado correctamente.")
