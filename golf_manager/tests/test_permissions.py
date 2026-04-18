"""
Pruebas de la seguridad a nivel de fila (permissions.py).
Mock de frappe construido antes de cualquier import.

Ejecutar:
    pytest golf_manager/tests/test_permissions.py -v
"""

import sys
import os
import types
from unittest.mock import MagicMock

# Mock

class _Document:
	pass

frappe_m = types.ModuleType("frappe")
frappe_m._ = lambda s, *a: s.format(*a) if a else s
frappe_m.db = MagicMock()
frappe_m.db.escape = lambda v: f"'{v}'"
frappe_m.session = MagicMock()
frappe_m.session.user = "jugador@test.com"
frappe_m.get_roles = MagicMock(return_value=[])
frappe_m.whitelist = lambda *a, **kw: (lambda f: f)

model_m = types.ModuleType("frappe.model")
doc_m = types.ModuleType("frappe.model.document")
doc_m.Document = _Document
model_m.document = doc_m
frappe_m.model = model_m

sys.modules["frappe"] = frappe_m
sys.modules["frappe.model"] = model_m
sys.modules["frappe.model.document"] = doc_m

# Imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest

from golf_manager.golf_manager.permissions import (
	_es_admin,
	_es_staff,
	_es_admin_o_staff,
	participacion_en_torneo_conditions,
	participacion_en_torneo_has_permission,
	puntuacion_por_hoyo_conditions,
	puntuacion_por_hoyo_has_permission,
)


def _con_roles(roles):
	mock = MagicMock(return_value=roles)
	frappe_m.get_roles = mock
	sys.modules["frappe"].get_roles = mock


# es admin

class TestEsAdmin:
	def test_system_manager_es_admin(self):
		_con_roles(["System Manager"])
		assert _es_admin("u@test.com") is True

	def test_administrador_es_admin(self):
		_con_roles(["administrador"])
		assert _es_admin("u@test.com") is True

	def test_staff_no_es_admin(self):
		_con_roles(["Staff"])
		assert _es_admin("u@test.com") is False

	def test_jugador_no_es_admin(self):
		_con_roles(["jugador"])
		assert _es_admin("u@test.com") is False

	def test_administrator_hardcoded(self):
		assert _es_admin("Administrator") is True

	def test_guest_no_tiene_acceso(self):
		assert _es_admin("Guest") is False


# es staff

class TestEsStaff:
	def test_staff_es_staff(self):
		_con_roles(["Staff"])
		assert _es_staff("u@test.com") is True

	def test_jugador_no_es_staff(self):
		_con_roles(["jugador"])
		assert _es_staff("u@test.com") is False

	def test_administrador_no_es_staff_por_rol(self):
		_con_roles(["administrador"])
		assert _es_staff("u@test.com") is False

	def test_administrator_hardcoded(self):
		assert _es_staff("Administrator") is True


# es admin o staff

class TestEsAdminOStaff:
	def test_administrador_es_admin_o_staff(self):
		_con_roles(["administrador"])
		assert _es_admin_o_staff("u@test.com") is True

	def test_staff_es_admin_o_staff(self):
		_con_roles(["Staff"])
		assert _es_admin_o_staff("u@test.com") is True

	def test_jugador_no_es_admin_o_staff(self):
		_con_roles(["jugador"])
		assert _es_admin_o_staff("u@test.com") is False

	def test_guest_no_tiene_acceso(self):
		assert _es_admin_o_staff("Guest") is False


# Condiciones SQL

class TestParticipacionConditions:
	def test_administrador_ve_todo_sin_condicion(self):
		_con_roles(["administrador"])
		assert participacion_en_torneo_conditions("admin@test.com") == ""

	def test_staff_ve_todo_sin_condicion(self):
		_con_roles(["Staff"])
		assert participacion_en_torneo_conditions("staff@test.com") == ""

	def test_jugador_obtiene_condicion_filtrada(self):
		_con_roles(["jugador"])
		resultado = participacion_en_torneo_conditions("jugador@test.com")
		assert "jugador@test.com" in resultado
		assert "tabparticipacion en torneo" in resultado


# has_permission participacion

class TestParticipacionHasPermission:
	def _doc(self, jugador):
		d = MagicMock()
		d.jugador = jugador
		return d

	def test_administrador_puede_ver_cualquier_participacion(self):
		_con_roles(["administrador"])
		assert participacion_en_torneo_has_permission(self._doc("otro@test.com"), "admin@test.com") is True

	def test_staff_puede_ver_cualquier_participacion(self):
		_con_roles(["Staff"])
		assert participacion_en_torneo_has_permission(self._doc("otro@test.com"), "staff@test.com") is True

	def test_staff_puede_escribir_cualquier_participacion(self):
		_con_roles(["Staff"])
		assert participacion_en_torneo_has_permission(self._doc("otro@test.com"), "staff@test.com", "write") is True

	def test_jugador_puede_ver_la_suya(self):
		_con_roles(["jugador"])
		assert participacion_en_torneo_has_permission(self._doc("jugador@test.com"), "jugador@test.com") is True

	def test_jugador_no_puede_ver_la_de_otro(self):
		_con_roles(["jugador"])
		assert participacion_en_torneo_has_permission(self._doc("otro@test.com"), "jugador@test.com") is False

	def test_jugador_no_puede_escribir_ninguna(self):
		_con_roles(["jugador"])
		assert participacion_en_torneo_has_permission(self._doc("jugador@test.com"), "jugador@test.com", "write") is False


# has_permission puntuacion

class TestPuntuacionHasPermission:
	def _doc(self, jugador, ronda="RONDA-001"):
		d = MagicMock()
		d.jugador = jugador
		d.ronda = ronda
		return d

	def test_administrador_puede_leer_cualquier_puntuacion(self):
		_con_roles(["administrador"])
		assert puntuacion_por_hoyo_has_permission(self._doc("otro@test.com"), "admin@test.com", "read") is True

	def test_administrador_puede_escribir_cualquier_puntuacion(self):
		_con_roles(["administrador"])
		assert puntuacion_por_hoyo_has_permission(self._doc("otro@test.com"), "admin@test.com", "write") is True

	def test_staff_puede_leer_cualquier_puntuacion(self):
		_con_roles(["Staff"])
		assert puntuacion_por_hoyo_has_permission(self._doc("otro@test.com"), "staff@test.com", "read") is True

	def test_staff_puede_escribir_cualquier_puntuacion(self):
		_con_roles(["Staff"])
		assert puntuacion_por_hoyo_has_permission(self._doc("otro@test.com"), "staff@test.com", "write") is True

	def test_staff_puede_crear_puntuacion(self):
		_con_roles(["Staff"])
		assert puntuacion_por_hoyo_has_permission(self._doc("otro@test.com"), "staff@test.com", "create") is True

	def test_jugador_puede_leer_la_suya(self):
		_con_roles(["jugador"])
		assert puntuacion_por_hoyo_has_permission(self._doc("jugador@test.com"), "jugador@test.com", "read") is True

	def test_jugador_no_puede_leer_la_de_otro(self):
		_con_roles(["jugador"])
		assert puntuacion_por_hoyo_has_permission(self._doc("otro@test.com"), "jugador@test.com", "read") is False

	def test_jugador_no_puede_escribir_ninguna(self):
		_con_roles(["jugador"])
		frappe_m.db.get_value = MagicMock(return_value="En curso")
		sys.modules["frappe"].db.get_value = frappe_m.db.get_value
		assert puntuacion_por_hoyo_has_permission(self._doc("jugador@test.com"), "jugador@test.com", "write") is False
