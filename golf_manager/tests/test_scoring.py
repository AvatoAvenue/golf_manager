"""
Pruebas unitarias puras para golf_manager.golf_manager.scoring.
No requieren instancia de Frappe ni base de datos.

Ejecutar:
    pytest golf_manager/tests/test_scoring.py -v
"""

import sys
import os

# Permite ejecutar sin instalar el app completo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from golf_manager.golf_manager.scoring import (
	aplicar_penalizaciones,
	asignar_posiciones,
	calcular_diferencia_par,
	calcular_stableford,
	calcular_stableford_ronda,
	calcular_total_stroke,
	construir_sort_key,
)


#  Stableford por hoyo                                                     #

class TestStablefordHoyo:
	def test_eagle_par4(self):
		assert calcular_stableford(2, 4) == 4

	def test_birdie_par4(self):
		assert calcular_stableford(3, 4) == 3

	def test_par_par4(self):
		assert calcular_stableford(4, 4) == 2

	def test_bogey_par4(self):
		assert calcular_stableford(5, 4) == 1

	def test_doble_bogey_par4(self):
		assert calcular_stableford(6, 4) == 0

	def test_triple_bogey_no_negativo(self):
		assert calcular_stableford(7, 4) == 0

	def test_birdie_par3(self):
		assert calcular_stableford(2, 3) == 3

	def test_eagle_par5(self):
		assert calcular_stableford(3, 5) == 4

	def test_albatros_par5(self):
		# 2 golpes en par 5 → max(0, 5+2-2) = 5
		assert calcular_stableford(2, 5) == 5

	def test_muchos_golpes_siempre_cero(self):
		assert calcular_stableford(15, 4) == 0


#  Stableford de ronda completa                                            #

class TestStablefordRonda:
	def _hacer_ronda(self, golpes_list, par=4):
		return [{"golpes_totales": g, "par_del_hoyo": par} for g in golpes_list]

	def test_ronda_perfecta_18_pares(self):
		hoyos = self._hacer_ronda([4] * 18)
		assert calcular_stableford_ronda(hoyos) == 36  # 2 puntos × 18

	def test_ronda_todos_birdie(self):
		hoyos = self._hacer_ronda([3] * 18)
		assert calcular_stableford_ronda(hoyos) == 54  # 3 puntos × 18

	def test_ronda_mixta(self):
		# 9 birdies (3 pts) + 9 bogeys (1 pt)
		hoyos = self._hacer_ronda([3] * 9 + [5] * 9)
		assert calcular_stableford_ronda(hoyos) == 9 * 3 + 9 * 1  # 36

	def test_ronda_incompleta_ignora_sin_golpes(self):
		hoyos = [
			{"golpes_totales": 4, "par_del_hoyo": 4},
			{"golpes_totales": None, "par_del_hoyo": 4},  # hoyo sin registrar
			{"golpes_totales": 3, "par_del_hoyo": 4},
		]
		assert calcular_stableford_ronda(hoyos) == 2 + 3  # solo los dos registrados

	def test_ronda_vacia(self):
		assert calcular_stableford_ronda([]) == 0


#  Stroke Play                                                             #

class TestStrokePlay:
	def test_total_18_hoyos(self):
		hoyos = [{"golpes_totales": 4, "par_del_hoyo": 4}] * 18
		assert calcular_total_stroke(hoyos) == 72

	def test_usa_golpes_brutos_si_no_hay_totales(self):
		hoyos = [{"golpes_totales": None, "golpes_brutos": 5, "par_del_hoyo": 4}]
		assert calcular_total_stroke(hoyos) == 5

	def test_golpes_totales_prevalece_sobre_brutos(self):
		hoyos = [{"golpes_totales": 6, "golpes_brutos": 4, "par_del_hoyo": 4}]
		assert calcular_total_stroke(hoyos) == 6

	def test_diferencia_par_positiva(self):
		assert calcular_diferencia_par(74, 72) == 2   # +2

	def test_diferencia_par_negativa(self):
		assert calcular_diferencia_par(68, 72) == -4  # -4

	def test_diferencia_par_exacto(self):
		assert calcular_diferencia_par(72, 72) == 0


#  Penalizaciones                                                          #

class TestPenalizaciones:
	def test_sin_penalizaciones(self):
		assert aplicar_penalizaciones(4, []) == 4

	def test_una_penalizacion(self):
		assert aplicar_penalizaciones(4, [{"golpes_adicionales": 2}]) == 6

	def test_multiples_penalizaciones(self):
		pens = [{"golpes_adicionales": 1}, {"golpes_adicionales": 2}]
		assert aplicar_penalizaciones(3, pens) == 6

	def test_penalizacion_cero(self):
		assert aplicar_penalizaciones(4, [{"golpes_adicionales": 0}]) == 4

	def test_penalizacion_none_se_ignora(self):
		assert aplicar_penalizaciones(4, [{"golpes_adicionales": None}]) == 4


#  Rankings — sort_key                                                     #

def _participante(jugador, total, hcp=10, ultima_golpes=None, ultima_stab=None):
	return {
		"jugador": jugador,
		"puntuacion_total_acumulada": total,
		"handicap_inscripcion": hcp,
	}


def _scores(jugador, golpes=None, stab=None):
	return {jugador: {"golpes": golpes or 0, "pts_stableford": stab or 0}}


class TestSortKeyStrokePlay:
	def _key(self, criterio, scores=None):
		return construir_sort_key("Stroke Play", criterio, scores or {})

	def test_menos_golpes_primero(self):
		key = self._key("Mejor última ronda")
		a = _participante("A", 70)
		b = _participante("B", 72)
		assert key(a) < key(b)

	def test_empate_resuelto_por_ultima_ronda(self):
		scores = {**_scores("A", golpes=34), **_scores("B", golpes=36)}
		key = self._key("Mejor última ronda", scores)
		a = _participante("A", 70)
		b = _participante("B", 70)
		# A tiene mejor última ronda (34 < 36)
		assert key(a) < key(b)

	def test_empate_resuelto_por_handicap(self):
		key = self._key("Menor hándicap")
		a = _participante("A", 70, hcp=8)
		b = _participante("B", 70, hcp=12)
		assert key(a) < key(b)

	def test_empate_resuelto_por_ultima_ronda_luego_hcp(self):
		scores = {**_scores("A", golpes=34), **_scores("B", golpes=34)}
		key = self._key("Mejor última ronda, luego menor hándicap", scores)
		a = _participante("A", 70, hcp=8)
		b = _participante("B", 70, hcp=12)
		# misma última ronda → desempate por hcp
		assert key(a) < key(b)


class TestSortKeyStableford:
	def _key(self, criterio, scores=None):
		return construir_sort_key("Stableford", criterio, scores or {})

	def test_mas_puntos_primero(self):
		key = self._key("Mejor última ronda")
		a = _participante("A", 38)
		b = _participante("B", 35)
		# A tiene más puntos → sort key de A debe ser menor (negativo más negativo)
		assert key(a) < key(b)

	def test_empate_stableford_ultima_ronda(self):
		scores = {**_scores("A", stab=20), **_scores("B", stab=18)}
		key = self._key("Mejor última ronda", scores)
		a = _participante("A", 38)
		b = _participante("B", 38)
		assert key(a) < key(b)


#  Rankings

class TestAsignarPosiciones:
	def _run(self, participantes, tipo="Stroke Play",
	         criterio="Mejor última ronda", scores=None):
		key = construir_sort_key(tipo, criterio, scores or {})
		return asignar_posiciones(participantes, key)

	def test_orden_simple_sin_empates(self):
		ps = [
			_participante("A", 75),
			_participante("B", 70),
			_participante("C", 72),
		]
		resultado = self._run(ps)
		jugadores_orden = [p["jugador"] for p in resultado]
		assert jugadores_orden == ["B", "C", "A"]
		assert [p["posicion_en_ranking"] for p in resultado] == [1, 2, 3]

	def test_empate_en_primer_lugar(self):
		ps = [
			_participante("A", 70),
			_participante("B", 70),
			_participante("C", 72),
		]
		resultado = self._run(ps)
		pos = {p["jugador"]: p["posicion_en_ranking"] for p in resultado}
		assert pos["A"] == pos["B"] == 1
		assert pos["C"] == 3  # no hay posición 2 cuando hay empate en 1

	def test_empate_en_segundo_lugar(self):
		ps = [
			_participante("A", 68),
			_participante("B", 70),
			_participante("C", 70),
		]
		resultado = self._run(ps)
		pos = {p["jugador"]: p["posicion_en_ranking"] for p in resultado}
		assert pos["A"] == 1
		assert pos["B"] == pos["C"] == 2

	def test_todos_empatados(self):
		ps = [_participante(str(i), 70) for i in range(5)]
		resultado = self._run(ps)
		assert all(p["posicion_en_ranking"] == 1 for p in resultado)

	def test_stableford_mas_puntos_primero(self):
		ps = [
			_participante("A", 32),
			_participante("B", 38),
			_participante("C", 35),
		]
		resultado = self._run(ps, tipo="Stableford")
		jugadores_orden = [p["jugador"] for p in resultado]
		assert jugadores_orden == ["B", "C", "A"]

	def test_lista_vacia(self):
		assert self._run([]) == []

	def test_un_solo_jugador(self):
		ps = [_participante("Solo", 72)]
		resultado = self._run(ps)
		assert resultado[0]["posicion_en_ranking"] == 1
