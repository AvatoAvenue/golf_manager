"""
Patch de migracion que inserta los datos de catalogo minimos
para que el modulo sea operativo desde la primera instalacion.

Catalogos insertados:
- 3 Formatos de torneo estandar (Stroke Play, Match Play, Stableford)
- 1 Campo de golf de ejemplo

Ejecutar manualmente:
    bench execute golf_manager.patches.v1_0.insertar_datos_iniciales.execute
"""

import frappe


def execute():
	_insertar_formatos()
	_insertar_campo_ejemplo()
	frappe.db.commit()


# Formatos de torneo

# Los valores de criterio_de_desempate deben coincidir exactamente con
# las options definidas en formato_de_torneo.json y con _CRITERIOS_VALIDOS
# en formato_de_torneo.py.
_FORMATOS = [
	{
		"nombre": "Stroke Play Estandar",
		"tipo_de_formato": "Stroke Play",
		"aplica_handicap_ajustado": 0,
		"criterio_de_desempate": "Mejor ultima ronda, luego menor handicap",
		"descripcion_de_reglas": (
			"Modalidad de juego en la que se cuentan el total de golpes de todas "
			"las rondas. Gana el jugador con menos golpes al final del torneo."
		),
	},
	{
		"nombre": "Match Play Estandar",
		"tipo_de_formato": "Match Play",
		"aplica_handicap_ajustado": 0,
		"criterio_de_desempate": "Mejor ultima ronda",
		"descripcion_de_reglas": (
			"Modalidad en la que se compara el resultado hoyo a hoyo entre "
			"dos jugadores. Gana quien gana mas hoyos."
		),
	},
	{
		"nombre": "Stableford Estandar",
		"tipo_de_formato": "Stableford",
		"aplica_handicap_ajustado": 1,
		"criterio_de_desempate": "Mejor ultima ronda, luego menor handicap",
		"descripcion_de_reglas": (
			"Sistema de puntuacion por hoyos: Eagle=4, Birdie=3, Par=2, "
			"Bogey=1, Doble bogey o mas=0. Gana quien acumula mas puntos."
		),
	},
]


def _insertar_formatos():
	for datos in _FORMATOS:
		if frappe.db.exists("formato de torneo", datos["nombre"]):
			continue
		doc = frappe.new_doc("formato de torneo")
		doc.update(datos)
		doc.flags.ignore_permissions = True
		doc.flags.ignore_mandatory   = False
		doc.insert()
		frappe.logger().info(f"Golf Manager: formato insertado -> {datos['nombre']}")


# Campo de golf de ejemplo

_CAMPO_EJEMPLO = {
	"nombre": "Campo de Ejemplo",
	"numero_de_hoyos": 18,
	"par_total": 72,
	"ubicacion": "Por configurar",
	"descripcion": (
		"Campo de golf de ejemplo creado automaticamente durante la instalacion. "
		"Edite este registro con los datos reales del campo."
	),
}


def _insertar_campo_ejemplo():
	if frappe.db.exists("campo de golf", _CAMPO_EJEMPLO["nombre"]):
		return
	doc = frappe.new_doc("campo de golf")
	doc.update(_CAMPO_EJEMPLO)
	doc.flags.ignore_permissions = True
	doc.insert()
	frappe.logger().info("Golf Manager: campo de ejemplo insertado")
