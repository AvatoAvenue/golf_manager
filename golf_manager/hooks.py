app_name = "golf_manager"
app_title = "Golf Manager"
app_publisher = "avato"
app_description = "Prototype to manage golf tournaments"
app_email = "sanchezruano2004@gmail.com"
app_license = "agpl-3.0"

fixtures = [
	{
		"doctype": "Client Script",
		"filters": [["module", "in", ("Golf Manager",)]],
	},
	{
		"doctype": "Server Script",
		"filters": [["module", "in", ("Golf Manager",)]],
	},
	{
		"doctype": "Role",
		"filters": [["name", "in", (
			"administrador",
			"Staff",
			"jugador",
		)]],
	},
	{
		"doctype": "Workspace",
		"filters": [["module", "in", ("Golf Manager",)]],
	},
	{
		"doctype": "Print Format",
		"filters": [["module", "in", ("Golf Manager",)]],
	},
	{
		"doctype": "Page",
		"filters": [["module", "in", ("Golf Manager",)]],
	},
]

scheduler_events = {
	"cron": {
		"*/5 * * * *": [
			"golf_manager.tasks.recalcular_rankings_torneos_activos",
		],
	},
	"daily": [
		"golf_manager.tasks.limpiar_cache_torneos_finalizados",
	],
}

doctype_js = {
	"torneo de golf":      "golf_manager/doctype/torneo_de_golf/torneo_de_golf.js",
	"puntuacion por hoyo": "golf_manager/doctype/puntuacion_por_hoyo/puntuacion_por_hoyo.js",
	"ronda":               "golf_manager/doctype/ronda/ronda.js",
}

permission_query_conditions = {
	"participacion en torneo": (
		"golf_manager.golf_manager.permissions.participacion_en_torneo_conditions"
	),
	"puntuacion por hoyo": (
		"golf_manager.golf_manager.permissions.puntuacion_por_hoyo_conditions"
	),
}

has_permission = {
	"participacion en torneo": (
		"golf_manager.golf_manager.permissions.participacion_en_torneo_has_permission"
	),
	"puntuacion por hoyo": (
		"golf_manager.golf_manager.permissions.puntuacion_por_hoyo_has_permission"
	),
}

after_install = "golf_manager.setup.grant_role_permissions"
after_migrate = "golf_manager.setup.grant_role_permissions"
