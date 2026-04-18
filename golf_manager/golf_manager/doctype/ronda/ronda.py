# Copyright (c) 2026, avato and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

from golf_manager.golf_manager.doctype.puntuacion_por_hoyo.puntuacion_por_hoyo import (
    _recalcular_rankings,
)


class ronda(Document):
    #  Lifecycle hooks

    def validate(self):
        self._validar_numero_de_ronda()
        self._validar_fecha()
        self._validar_transicion_estado()

    def on_update(self):
        if self.estado == "Completada":
            self._recalcular_todos_los_totales()
            _recalcular_rankings(self.torneo)
            frappe.cache().delete_key(f"golf_ranking_{self.torneo}")

    #  Validaciones

    def _validar_numero_de_ronda(self):
        numero_rondas = frappe.db.get_value(
            "torneo de golf", self.torneo, "numero_de_rondas"
        )
        if numero_rondas and self.numero_de_ronda > numero_rondas:
            frappe.throw(
                frappe._(
                    "El número de ronda ({0}) supera el total de rondas configuradas en el torneo ({1})."
                ).format(self.numero_de_ronda, numero_rondas)
            )

        existente = frappe.db.get_value(
            "ronda",
            {
                "torneo": self.torneo,
                "numero_de_ronda": self.numero_de_ronda,
                "name": ("!=", self.name),
            },
            "name",
        )
        if existente:
            frappe.throw(
                frappe._("Ya existe una ronda {0} para el torneo {1}.").format(
                    self.numero_de_ronda, self.torneo
                )
            )

    def _validar_fecha(self):
        torneo = frappe.get_doc("torneo de golf", self.torneo)
        fecha_ronda = getdate(self.fecha)
        fecha_inicio = getdate(torneo.fecha_de_inicio)
        fecha_fin = getdate(torneo.fecha_de_fin)

        if fecha_ronda < fecha_inicio or fecha_ronda > fecha_fin:
            frappe.throw(
                frappe._(
                    "La fecha de la ronda ({0}) debe estar dentro del período del torneo ({1} - {2})."
                ).format(
                    fecha_ronda.strftime("%d/%m/%Y"),
                    fecha_inicio.strftime("%d/%m/%Y"),
                    fecha_fin.strftime("%d/%m/%Y"),
                )
            )

    def _validar_transicion_estado(self):
        """
        Transiciones permitidas:
          Pendiente → En curso
          En curso  → Completada
          Pendiente → Completada  (carga diferida de resultados)
        """
        if self.is_new():
            return

        estado_anterior = frappe.db.get_value("ronda", self.name, "estado")
        if estado_anterior == "Completada" and self.estado != "Completada":
            frappe.throw(
                frappe._("Una ronda completada no puede cambiar de estado.")
            )

    #  Recálculo en cascada

    def _recalcular_todos_los_totales(self):
        """
        Al completar una ronda, recalcula stableford para cada puntuación
        de esa ronda. Útil si el formato cambió o hay penalizaciones nuevas.
        """
        puntuaciones = frappe.get_all(
            "puntuacion por hoyo",
            filters={"ronda": self.name},
            fields=["name"],
        )
        for p in puntuaciones:
            doc = frappe.get_doc("puntuacion por hoyo", p.name)
            doc.run_method("validate")
            doc.db_update()
