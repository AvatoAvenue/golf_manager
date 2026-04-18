"""
Pruebas de las validaciones de los controladores de DocType.
El mock de frappe se construye ANTES de cualquier import de los controladores.

Ejecutar:
    pytest golf_manager/tests/test_validaciones.py -v
"""

import sys
import os
import types
from unittest.mock import MagicMock

# Mock

class _FrappeException(Exception):
	pass

class _Document:
	flags = type("F", (), {"ignore_permissions": False, "ignore_mandatory": False})()
	def db_set(self, *a, **kw): pass
	def db_update(self): pass
	def run_method(self, *a): pass

def _throw(msg, *a):
	raise _FrappeException(msg)

frappe_m = types.ModuleType("frappe")
frappe_m._ = lambda s, *a: s.format(*a) if a else s
frappe_m.db = MagicMock()
frappe_m.throw = _throw
frappe_m.whitelist = lambda *a, **kw: (lambda f: f)
frappe_m.get_roles = MagicMock(return_value=[])
frappe_m.ValidationError = _FrappeException
frappe_m.get_doc = MagicMock()
frappe_m.get_all = MagicMock(return_value=[])
frappe_m.logger = MagicMock(return_value=MagicMock())

model_m = types.ModuleType("frappe.model")
doc_m = types.ModuleType("frappe.model.document")
doc_m.Document = _Document
model_m.document = doc_m
frappe_m.model = model_m

sys.modules["frappe"] = frappe_m
sys.modules["frappe.model"] = model_m
sys.modules["frappe.model.document"] = doc_m

# Path y los imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest

from golf_manager.golf_manager.doctype.campo_de_golf.campo_de_golf import CampoDeGolf
from golf_manager.golf_manager.doctype.formato_de_torneo.formato_de_torneo import FormatoDeTorneo
from golf_manager.golf_manager.doctype.puntuacion_por_hoyo.puntuacion_por_hoyo import PuntuacionPorHoyo
from golf_manager.golf_manager.doctype.participacion_en_torneo.participacion_en_torneo import ParticipacionEnTorneo
from golf_manager.golf_manager.doctype.torneo_de_golf.torneo_de_golf import TorneoDeGolf


def _doc(**fields):
	obj = MagicMock()
	obj.name = fields.pop("name", "TEST-001")
	obj.is_new = MagicMock(return_value=fields.pop("is_new", True))
	for k, v in fields.items():
		setattr(obj, k, v)
	return obj


# CampoDeGolf

class TestCampoDeGolfValidaciones:
	def _campo(self, hoyos=18, par=72):
		return _doc(nombre="Club Test", numero_de_hoyos=hoyos, par_total=par)

	def test_18_hoyos_par72_valido(self):
		doc = self._campo()
		CampoDeGolf._validar_numero_de_hoyos(doc)
		CampoDeGolf._validar_par_total(doc)

	def test_9_hoyos_valido(self):
		doc = self._campo(9, 36)
		CampoDeGolf._validar_numero_de_hoyos(doc)
		CampoDeGolf._validar_par_total(doc)

	def test_par_limite_inferior_exacto(self):
		CampoDeGolf._validar_par_total(self._campo(18, 54))

	def test_par_limite_superior_exacto(self):
		CampoDeGolf._validar_par_total(self._campo(18, 90))

	def test_numero_hoyos_invalido(self):
		with pytest.raises(_FrappeException):
			CampoDeGolf._validar_numero_de_hoyos(self._campo(hoyos=12))

	def test_par_total_muy_bajo(self):
		with pytest.raises(_FrappeException):
			CampoDeGolf._validar_par_total(self._campo(18, 30))

	def test_par_total_muy_alto(self):
		with pytest.raises(_FrappeException):
			CampoDeGolf._validar_par_total(self._campo(18, 100))


# FormatoDeTorneo

class TestFormatoDeTorneoValidaciones:
	def _fmt(self, tipo, criterio):
		return _doc(nombre="Test", tipo_de_formato=tipo, criterio_de_desempate=criterio)

	def test_stroke_play_valido(self):
		FormatoDeTorneo._validar_coherencia_formato_criterio(
			self._fmt("Stroke Play", "Mejor última ronda"))

	def test_stableford_menor_handicap_valido(self):
		FormatoDeTorneo._validar_coherencia_formato_criterio(
			self._fmt("Stableford", "Menor hándicap"))

	def test_criterio_inexistente_invalido(self):
		with pytest.raises(_FrappeException):
			FormatoDeTorneo._validar_coherencia_formato_criterio(
				self._fmt("Stroke Play", "Criterio inexistente"))


# PuntuacionPorHoyo

class TestPuntuacionPorHoyoValidaciones:
	def _score(self, hoyo=1, golpes=4, par=4, pens=None):
		return _doc(ronda="RONDA-001", jugador="j@test.com",
		            numero_de_hoyo=hoyo, golpes_brutos=golpes,
		            par_del_hoyo=par, penalizaciones=pens or [],
		            flag_penalizacion=0)

	def test_hoyo_1_valido(self):
		PuntuacionPorHoyo._validar_numero_de_hoyo(self._score(hoyo=1))

	def test_hoyo_18_valido(self):
		PuntuacionPorHoyo._validar_numero_de_hoyo(self._score(hoyo=18))

	def test_hoyo_0_invalido(self):
		with pytest.raises(_FrappeException):
			PuntuacionPorHoyo._validar_numero_de_hoyo(self._score(hoyo=0))

	def test_hoyo_19_invalido(self):
		with pytest.raises(_FrappeException):
			PuntuacionPorHoyo._validar_numero_de_hoyo(self._score(hoyo=19))

	def test_golpes_cero_invalido(self):
		with pytest.raises(_FrappeException):
			PuntuacionPorHoyo._validar_golpes(self._score(golpes=0))

	def test_par_menor_3_invalido(self):
		with pytest.raises(_FrappeException):
			PuntuacionPorHoyo._validar_golpes(self._score(golpes=2, par=2))

	def test_golpes_totales_sin_penalizaciones(self):
		doc = self._score(golpes=4)
		PuntuacionPorHoyo._calcular_golpes_totales(doc)
		assert doc.golpes_totales == 4
		assert doc.flag_penalizacion == 0

	def test_golpes_totales_con_penalizaciones(self):
		pen = MagicMock(golpes_adicionales=2)
		doc = self._score(golpes=4, pens=[pen])
		PuntuacionPorHoyo._calcular_golpes_totales(doc)
		assert doc.golpes_totales == 6
		assert doc.flag_penalizacion == 1


# ParticipacionEnTorneo

class TestParticipacionValidaciones:
	def _part(self, hcp=10, estado_torneo="Activo"):
		frappe_m.db.get_value = MagicMock(return_value=estado_torneo)
		return _doc(torneo="TORN-001", jugador="j@test.com",
		            categoria="Amateur A", handicap_inscripcion=hcp)

	def test_handicap_valido(self):
		ParticipacionEnTorneo._validar_handicap(self._part(hcp=18))

	def test_handicap_negativo_valido(self):
		ParticipacionEnTorneo._validar_handicap(self._part(hcp=-5))

	def test_handicap_demasiado_alto(self):
		with pytest.raises(_FrappeException):
			ParticipacionEnTorneo._validar_handicap(self._part(hcp=55))

	def test_handicap_demasiado_bajo(self):
		with pytest.raises(_FrappeException):
			ParticipacionEnTorneo._validar_handicap(self._part(hcp=-15))

	def test_torneo_finalizado_bloquea_inscripcion(self):
		with pytest.raises(_FrappeException):
			ParticipacionEnTorneo._validar_torneo_activo(self._part(estado_torneo="Finalizado"))

	def test_torneo_activo_permite_inscripcion(self):
		ParticipacionEnTorneo._validar_torneo_activo(self._part(estado_torneo="Activo"))

	def test_torneo_borrador_permite_inscripcion(self):
		ParticipacionEnTorneo._validar_torneo_activo(self._part(estado_torneo="Borrador"))


# TorneoDeGolf

class TestTorneoDeGolfValidaciones:
	def _torneo(self, inicio="2026-05-01", fin="2026-05-03", rondas=2,
	            estado="Borrador", docstatus=0):
		return _doc(nombre_del_torneo="Test", fecha_de_inicio=inicio,
		            fecha_de_fin=fin, numero_de_rondas=rondas,
		            estado=estado, docstatus=docstatus)

	def test_fechas_validas(self):
		TorneoDeGolf._validar_fechas(self._torneo())

	def test_fecha_fin_anterior_a_inicio(self):
		with pytest.raises(_FrappeException):
			TorneoDeGolf._validar_fechas(self._torneo(inicio="2026-05-05", fin="2026-05-01"))

	def test_cero_rondas_invalido(self):
		with pytest.raises(_FrappeException):
			TorneoDeGolf._validar_fechas(self._torneo(rondas=0))

	def test_estado_activo_sin_submit_se_corrige(self):
		doc = self._torneo(estado="Activo", docstatus=0)
		TorneoDeGolf._sincronizar_estado_con_docstatus(doc)
		assert doc.estado == "Borrador"

	def test_estado_activo_con_submit_se_mantiene(self):
		doc = self._torneo(estado="Activo", docstatus=1)
		TorneoDeGolf._sincronizar_estado_con_docstatus(doc)
		assert doc.estado == "Activo"
