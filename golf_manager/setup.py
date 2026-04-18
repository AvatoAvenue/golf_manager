"""
Ejecutado tras bench install-app y bench migrate.
Garantiza que los roles del modulo tengan acceso al desk de Frappe,
resolviendo el error "no tiene acceso a doctype a traves del permiso
de rol para el documento Pagina" en Frappe v15.
"""

import frappe


# Roles del modulo que necesitan acceder al desk
_ROLES_GOLF = [
    "administrador",
    "Staff",
    "jugador",
]

# DocTypes de sistema que Frappe requiere para navegar el desk
_DOCTYPES_SISTEMA = [
    "Page",
    "Module Def",
    "Report",
    "Workspace",
]


def grant_role_permissions():
    """
    Agrega permisos de lectura sobre Page, Module Def,
    Report y Workspace para cada rol del modulo si no existen ya.
    """
    for role in _ROLES_GOLF:
        if not frappe.db.exists("Role", role):
            continue
        for doctype in _DOCTYPES_SISTEMA:
            _ensure_permission(role, doctype)

    frappe.db.commit()


def _ensure_permission(role, doctype):
    """Crea el registro de permiso de lectura si no existe."""
    existe = frappe.db.exists(
        "Custom DocPerm",
        {"parent": doctype, "role": role, "permlevel": 0},
    )
    if existe:
        return

    # Intentar primero con DocPerm estandar
    existe_std = frappe.db.exists(
        "DocPerm",
        {"parent": doctype, "role": role, "permlevel": 0},
    )
    if existe_std:
        return

    try:
        perm = frappe.new_doc("Custom DocPerm")
        perm.parent      = doctype
        perm.parenttype  = "DocType"
        perm.parentfield = "permissions"
        perm.role        = role
        perm.permlevel   = 0
        perm.read        = 1
        perm.write       = 0
        perm.create      = 0
        perm.delete      = 0
        perm.flags.ignore_permissions = True
        perm.insert()
        frappe.logger().info(
            f"Golf Manager setup: permiso de lectura en '{doctype}' para rol '{role}' creado."
        )
    except Exception as e:
        # No interrumpir la migracion si algo falla
        frappe.logger().warning(
            f"Golf Manager setup: no se pudo crear permiso {doctype}/{role}: {e}"
        )
