"""
Seguridad a nivel de fila para los DocTypes
donde el jugador solo debe ver sus propios registros.

Roles del modulo:
  administrador - control total sobre todos los doctypes
  Staff         - puede editar puntuaciones de jugadores
  jugador       - solo puede ver sus propias puntuaciones y los torneos

Registrado en hooks.py bajo permission_query_conditions y has_permission.
"""

import frappe


# Participacion en Torneo

def participacion_en_torneo_conditions(user=None):
    """
    Jugadores solo ven su propia participacion.
    administrador y Staff ven todo.
    """
    if not user:
        user = frappe.session.user

    if _es_admin_o_staff(user):
        return ""

    return f"(`tabparticipacion en torneo`.jugador = {frappe.db.escape(user)})"


def participacion_en_torneo_has_permission(doc, user=None, ptype="read"):
    """
    Comprobacion de permiso individual.
    Jugadores solo acceden a su propio registro en modo lectura.
    administrador y Staff pueden leer cualquiera.
    Staff puede ademas escribir.
    """
    if not user:
        user = frappe.session.user

    if _es_admin(user):
        return True

    if _es_staff(user):
        if ptype in ("read", "write", "create"):
            return True
        return False

    # jugador: solo su propio registro, solo lectura
    if ptype == "read":
        return doc.jugador == user

    return False


# Puntuacion por Hoyo

def puntuacion_por_hoyo_conditions(user=None):
    """
    Jugadores solo ven sus propias puntuaciones.
    administrador y Staff ven todo.
    """
    if not user:
        user = frappe.session.user

    if _es_admin_o_staff(user):
        return ""

    return f"(`tabpuntuacion por hoyo`.jugador = {frappe.db.escape(user)})"


def puntuacion_por_hoyo_has_permission(doc, user=None, ptype="read"):
    if not user:
        user = frappe.session.user

    if _es_admin(user):
        return True

    if _es_staff(user):
        # Staff puede crear y editar puntuaciones de cualquier jugador
        if ptype in ("read", "write", "create"):
            return True
        return False

    # jugador: solo lectura de sus propias puntuaciones
    if ptype == "read":
        return doc.jugador == user

    return False


# Torneo de Golf

def torneo_de_golf_conditions(user=None):
    """
    Todos los roles con acceso de lectura ven todos los torneos.
    """
    return ""


def torneo_de_golf_has_permission(doc, user=None, ptype="read"):
    """
    administrador tiene acceso completo.
    Staff y jugador solo pueden leer.
    """
    if not user:
        user = frappe.session.user

    roles = set(frappe.get_roles(user))

    if "System Manager" in roles or user == "Administrator":
        return True

    if _es_admin(user):
        return True

    if ptype == "read":
        return bool(roles & _ROLES_LECTURA)

    if ptype in ("write", "create", "delete", "submit", "cancel", "amend"):
        return "administrador" in roles

    return False


# Utilidad interna

_ROLES_ADMIN = frozenset({
    "System Manager",
    "administrador",
    "Administrator",
})

_ROLES_STAFF = frozenset({
    "Staff",
})

_ROLES_LECTURA = frozenset({
    "System Manager",
    "administrador",
    "Staff",
    "jugador",
    "Visitante",
    "Guest",
})


def _es_admin(user):
    """True si el usuario es administrador o System Manager."""
    if user in ("Administrator",):
        return True
    if user == "Guest":
        return False
    roles = frappe.get_roles(user)
    return bool(_ROLES_ADMIN & set(roles))


def _es_staff(user):
    """True si el usuario tiene el rol Staff."""
    if user in ("Administrator",):
        return True
    if user == "Guest":
        return False
    roles = frappe.get_roles(user)
    return bool(_ROLES_STAFF & set(roles))


def _es_admin_o_staff(user):
    """True si el usuario es administrador, System Manager o Staff."""
    if user == "Administrator":
        return True
    if user == "Guest":
        return False
    roles = set(frappe.get_roles(user))
    return bool((_ROLES_ADMIN | _ROLES_STAFF) & roles)
