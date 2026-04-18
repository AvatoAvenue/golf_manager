"""
Tareas programadas del scheduler de Frappe.
Definidas en hooks.py bajo scheduler_events.
"""

import frappe

from golf_manager.golf_manager.doctype.puntuacion_por_hoyo.puntuacion_por_hoyo import (
	_recalcular_rankings,
)




def recalcular_rankings_torneos_activos():
	"""
	Recalcula los rankings de todos los torneos con estado 'Activo'.
	Corre cada 5 minutos como respaldo al recálculo en tiempo real.
	"""
	torneos_activos = frappe.get_all(
		"torneo de golf",
		filters={"estado": "Activo", "docstatus": 1},
		pluck="name",
	)
	for torneo in torneos_activos:
		try:
			_recalcular_rankings(torneo)
		except Exception:
			frappe.log_error(
				title=f"Error recalculando ranking: {torneo}",
				message=frappe.get_traceback(),
			)


def limpiar_cache_torneos_finalizados():
	"""
	Elimina las entradas de caché Redis de torneos finalizados
	hace más de 7 días para no acumular memoria innecesaria.
	"""
	torneos_finalizados = frappe.get_all(
		"torneo de golf",
		filters={"estado": "Finalizado"},
		pluck="name",
	)
	for torneo in torneos_finalizados:
		frappe.cache().delete_key(f"golf_ranking_{torneo}")
