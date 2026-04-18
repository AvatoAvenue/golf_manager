"""
Funciones de cálculo de puntuación puras
Importadas por los controladores de DocType y por las pruebas unitarias.

Al estar aisladas aquí se pueden probar con pytest estándar, sin levantar
la instancia de Frappe.
"""


#  Stableford

def calcular_stableford(golpes_totales: int, par: int) -> int:
	"""
	Puntos Stableford estándar para un hoyo.

	  puntos = max(0, par + 2 - golpes_totales)

	Ejemplos:
	  Eagle (par 4, 2 golpes)  = max(0, 4+2-2) = 4
	  Birdie (par 4, 3 golpes) = max(0, 4+2-3) = 3
	  Par    (par 4, 4 golpes) = max(0, 4+2-4) = 2
	  Bogey  (par 4, 5 golpes) = max(0, 4+2-5) = 1
	  Doble  (par 4, 6 golpes) = max(0, 4+2-6) = 0
	  Triple (par 4, 7 golpes) = max(0, 4+2-7) = 0
	"""
	return max(0, par + 2 - golpes_totales)


def calcular_stableford_ronda(hoyos: list[dict]) -> int:
	"""
	Suma los puntos Stableford de una lista de hoyos.

	Args:
		hoyos: lista de dicts con claves 'golpes_totales' y 'par_del_hoyo'.
	"""
	return sum(
		calcular_stableford(h["golpes_totales"], h["par_del_hoyo"])
		for h in hoyos
		if h.get("golpes_totales") and h.get("par_del_hoyo")
	)


#  Stroke Play

def calcular_total_stroke(hoyos: list[dict]) -> int:
	"""
	Total de golpes para Stroke Play.
	Usa 'golpes_totales' si existe, sino 'golpes_brutos'.
	"""
	return sum(
		h.get("golpes_totales") or h.get("golpes_brutos") or 0
		for h in hoyos
	)


def calcular_diferencia_par(golpes_totales: int, par: int) -> int:
	"""Diferencia respecto al par (+/-). Stroke Play."""
	return golpes_totales - par


#  Penalizaciones

def aplicar_penalizaciones(golpes_brutos: int, penalizaciones: list[dict]) -> int:
	"""
	Suma los golpes adicionales de penalizaciones a los golpes brutos.

	Args:
		golpes_brutos: golpes registrados antes de penalizar.
		penalizaciones: lista de dicts con clave 'golpes_adicionales'.

	Returns:
		Total de golpes incluyendo penalizaciones.
	"""
	extra = sum(int(p.get("golpes_adicionales") or 0) for p in penalizaciones)
	return golpes_brutos + extra


#  Ranking

def construir_sort_key(
	tipo_formato: str,
	criterio_desempate: str,
	scores_ultima_ronda: dict,
):
	"""
	Devuelve una función sort_key para ordenar participantes.

	Args:
		tipo_formato: "Stroke Play" | "Match Play" | "Stableford"
		criterio_desempate: "Mejor última ronda" | "Menor hándicap" |
		                    "Mejor última ronda, luego menor hándicap"
		scores_ultima_ronda: dict { jugador -> {"golpes": N, "pts_stableford": N} }

	Returns:
		Callable que recibe un dict de participación y devuelve tuple de sort.
	"""

	def sort_key(p: dict) -> tuple:
		total = float(p.get("puntuacion_total_acumulada") or 0)
		hcp   = float(p.get("handicap_inscripcion") or 0)
		sr    = scores_ultima_ronda.get(p.get("jugador"), {})

		if tipo_formato == "Stableford":
			primary      = -total                           # más puntos = mejor
			score_ultima = -(sr.get("pts_stableford") or 0)
		else:
			primary      = total                            # menos golpes = mejor
			score_ultima = sr.get("golpes") or 999

		if criterio_desempate == "Mejor última ronda":
			return (primary, score_ultima)
		elif criterio_desempate == "Menor hándicap":
			return (primary, hcp)
		else:  # Mejor última ronda, luego menor hándicap
			return (primary, score_ultima, hcp)

	return sort_key


def asignar_posiciones(participaciones: list[dict], sort_key) -> list[dict]:
	"""
	Ordena participantes y asigna posición respetando empates.

	Args:
		participaciones: lista de dicts de participación.
		sort_key: función de ordenación (de construir_sort_key).

	Returns:
		Lista ordenada con clave 'posicion_en_ranking' añadida.
	"""
	ordenados = sorted(participaciones, key=sort_key)

	posicion_actual = 1
	for i, p in enumerate(ordenados):
		if i > 0 and sort_key(p) == sort_key(ordenados[i - 1]):
			p["posicion_en_ranking"] = ordenados[i - 1]["posicion_en_ranking"]
		else:
			p["posicion_en_ranking"] = posicion_actual
		posicion_actual = i + 2

	return ordenados
