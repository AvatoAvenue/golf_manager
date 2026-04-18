"""
Datos de prueba para validar el flujo completo de un torneo de golf.

Ejecutar:
    bench --site <site> execute golf_manager.patches.v1_0.datos_de_prueba.execute

Para revertir:
    bench --site <site> execute golf_manager.patches.v1_0.datos_de_prueba.revert
"""

import frappe
from frappe.utils import today, add_days

_PREFIJO = "test.golf"

_USUARIOS = [
    (f"{_PREFIJO}.admin@example.com",       "Carlos Administrador",  "administrador"),
    (f"{_PREFIJO}.staff@example.com",       "Laura Staff",           "Staff"),
    (f"{_PREFIJO}.jugador01@example.com",   "Miguel Angel Torres",   "jugador"),
    (f"{_PREFIJO}.jugador02@example.com",   "Sofia Ramirez",         "jugador"),
    (f"{_PREFIJO}.jugador03@example.com",   "Fernando Castillo",     "jugador"),
    (f"{_PREFIJO}.jugador04@example.com",   "Valentina Herrera",     "jugador"),
    (f"{_PREFIJO}.jugador05@example.com",   "Roberto Mendoza",       "jugador"),
    (f"{_PREFIJO}.jugador06@example.com",   "Patricia Lozano",       "jugador"),
    (f"{_PREFIJO}.jugador07@example.com",   "Andres Villanueva",     "jugador"),
    (f"{_PREFIJO}.jugador08@example.com",   "Claudia Serrano",       "jugador"),
    (f"{_PREFIJO}.jugador09@example.com",   "Hector Fuentes",        "jugador"),
    (f"{_PREFIJO}.jugador10@example.com",   "Isabel Moreno",         "jugador"),
    (f"{_PREFIJO}.jugador11@example.com",   "Gabriela Pena",         "jugador"),
    (f"{_PREFIJO}.jugador12@example.com",   "Diana Ibanez",          "jugador"),
]

_CAMPO        = "Club de Golf Las Palomas"
_FMT_STROKE   = "Stroke Play Estandar"
_TORNEO_NOMBRE = "Torneo de Prueba 2026"

_PARTICIPACIONES = [
    (f"{_PREFIJO}.jugador01@example.com", "Amateur A",  4.2),
    (f"{_PREFIJO}.jugador02@example.com", "Amateur A",  6.8),
    (f"{_PREFIJO}.jugador03@example.com", "Amateur A",  9.1),
    (f"{_PREFIJO}.jugador04@example.com", "Amateur B", 14.5),
    (f"{_PREFIJO}.jugador05@example.com", "Amateur B", 17.0),
    (f"{_PREFIJO}.jugador06@example.com", "Amateur B", 19.3),
    (f"{_PREFIJO}.jugador07@example.com", "Amateur C", 24.6),
    (f"{_PREFIJO}.jugador08@example.com", "Amateur C", 27.2),
    (f"{_PREFIJO}.jugador09@example.com", "Amateur C", 30.0),
    (f"{_PREFIJO}.jugador10@example.com", "Dama",      11.4),
    (f"{_PREFIJO}.jugador11@example.com", "Dama",      15.7),
    (f"{_PREFIJO}.jugador12@example.com", "Dama",      22.0),
]

_PARES = [4,3,5,4,4,3,5,4,4, 4,3,5,4,4,3,5,4,4]

_SCORES = {
    f"{_PREFIJO}.jugador01@example.com": [4,3,4,4,4,3,5,4,4, 4,2,5,4,4,3,5,4,4],
    f"{_PREFIJO}.jugador02@example.com": [4,3,5,4,5,3,5,4,4, 4,3,5,4,4,3,5,4,5],
    f"{_PREFIJO}.jugador03@example.com": [5,3,5,4,4,3,5,5,4, 4,3,5,4,4,4,5,4,4],
    f"{_PREFIJO}.jugador04@example.com": [5,4,5,4,5,3,5,4,5, 4,3,5,5,4,3,5,5,4],
    f"{_PREFIJO}.jugador05@example.com": [5,4,6,4,5,4,5,4,5, 5,3,5,4,5,3,5,5,4],
    f"{_PREFIJO}.jugador06@example.com": [5,4,5,5,5,3,6,4,5, 4,4,5,5,4,4,5,5,5],
    f"{_PREFIJO}.jugador07@example.com": [6,4,6,5,5,4,6,5,5, 5,4,6,5,5,4,6,5,5],
    f"{_PREFIJO}.jugador08@example.com": [6,4,6,5,6,4,6,5,5, 5,4,6,5,5,4,6,5,6],
    f"{_PREFIJO}.jugador09@example.com": [6,5,6,5,6,4,7,5,5, 6,4,6,5,6,4,6,5,5],
    f"{_PREFIJO}.jugador10@example.com": [5,3,5,4,5,3,5,4,4, 4,3,5,4,5,3,5,4,4],
    f"{_PREFIJO}.jugador11@example.com": [5,4,5,5,5,3,5,5,4, 5,3,5,5,4,3,5,5,4],
    f"{_PREFIJO}.jugador12@example.com": [6,4,5,5,5,4,6,5,5, 5,4,5,5,5,4,5,5,5],
}

def execute():
    frappe.logger().info("Golf Manager: cargando datos de prueba...")
    _crear_usuarios()
    _crear_campo()
    torneo_name = _crear_torneo()
    ronda1, _r2 = _crear_rondas(torneo_name)
    _crear_participaciones(torneo_name)
    _crear_grupos(ronda1, torneo_name)
    _registrar_puntuaciones(ronda1, torneo_name)
    _completar_ronda(ronda1)
    frappe.db.commit()
    print(f"\nListo.")
    print(f"  torneo name  : {torneo_name}")
    print(f"  ronda 1 name : {ronda1}")
    print(f"  password     : Test@12345\n")


def _crear_usuarios():
    for email, nombre, rol in _USUARIOS:
        if frappe.db.exists("User", email):
            continue
        partes = nombre.split()
        u = frappe.new_doc("User")
        u.email      = email
        u.first_name = partes[0]
        u.last_name  = " ".join(partes[1:])
        u.full_name  = nombre
        u.enabled    = 1
        u.user_type  = "System User"
        u.new_password       = "Test@12345"
        u.send_welcome_email = 0
        u.append("roles", {"role": rol})
        if rol == "jugador":
            u.append("roles", {"role": "Blogger"})
        u.flags.ignore_permissions     = True
        u.flags.ignore_password_policy = True
        u.insert()


def _crear_campo():
    if frappe.db.exists("campo de golf", _CAMPO):
        return
    d = frappe.new_doc("campo de golf")
    d.nombre          = _CAMPO
    d.numero_de_hoyos = 18
    d.par_total       = 72
    d.ubicacion       = "Av. del Golf 100, CDMX"
    d.flags.ignore_permissions = True
    d.insert()


def _crear_torneo():
    existente = frappe.db.get_value(
        "torneo de golf", {"nombre_del_torneo": _TORNEO_NOMBRE}, "name"
    )
    if existente:
        return existente

    if not frappe.db.exists("formato de torneo", _FMT_STROKE):
        f = frappe.new_doc("formato de torneo")
        f.nombre               = _FMT_STROKE
        f.tipo_de_formato      = "Stroke Play"
        f.aplica_handicap_ajustado = 0
        f.criterio_de_desempate    = "Mejor ultima ronda, luego menor handicap"
        f.flags.ignore_permissions = True
        f.insert()

    t = frappe.new_doc("torneo de golf")
    t.nombre_del_torneo = _TORNEO_NOMBRE
    t.campo_de_golf     = _CAMPO
    t.formato           = _FMT_STROKE
    t.estado            = "Borrador"
    t.fecha_de_inicio   = today()
    t.fecha_de_fin      = add_days(today(), 2)
    t.numero_de_rondas  = 2
    t.flags.ignore_permissions = True
    t.insert()
    t.flags.ignore_permissions = True
    t.submit()
    return t.name


def _crear_rondas(torneo_name):
    r1 = _crear_ronda(torneo_name, 1, today())
    r2 = _crear_ronda(torneo_name, 2, add_days(today(), 1))
    frappe.db.set_value("ronda", r2, "estado", "En curso", update_modified=False)
    return r1, r2


def _crear_ronda(torneo_name, numero, fecha):
    existente = frappe.db.get_value(
        "ronda", {"torneo": torneo_name, "numero_de_ronda": numero}, "name"
    )
    if existente:
        return existente

    r = frappe.new_doc("ronda")
    r.torneo          = torneo_name
    r.numero_de_ronda = numero
    r.fecha           = fecha
    r.estado          = "Pendiente"
    r.flags.ignore_permissions = True
    r.flags.ignore_validate    = True
    r.insert()
    return r.name


def _crear_participaciones(torneo_name):
    for email, cat, hcp in _PARTICIPACIONES:
        if frappe.db.exists(
            "participacion en torneo", {"torneo": torneo_name, "jugador": email}
        ):
            continue
        p = frappe.new_doc("participacion en torneo")
        p.torneo                     = torneo_name
        p.jugador                    = email
        p.categoria                  = cat
        p.handicap_inscripcion       = hcp
        p.puntuacion_total_acumulada = 0
        p.posicion_en_ranking        = 0
        p.flags.ignore_permissions   = True
        p.insert()


def _crear_grupos(ronda1, torneo_name):
    cfg = [
        ("Grupo A - 08:00", "08:00:00", [
            f"{_PREFIJO}.jugador01@example.com",
            f"{_PREFIJO}.jugador04@example.com",
            f"{_PREFIJO}.jugador10@example.com",
        ]),
        ("Grupo B - 08:10", "08:10:00", [
            f"{_PREFIJO}.jugador02@example.com",
            f"{_PREFIJO}.jugador05@example.com",
            f"{_PREFIJO}.jugador11@example.com",
        ]),
        ("Grupo C - 08:20", "08:20:00", [
            f"{_PREFIJO}.jugador03@example.com",
            f"{_PREFIJO}.jugador06@example.com",
            f"{_PREFIJO}.jugador12@example.com",
        ]),
        ("Grupo D - 08:30", "08:30:00", [
            f"{_PREFIJO}.jugador07@example.com",
            f"{_PREFIJO}.jugador08@example.com",
            f"{_PREFIJO}.jugador09@example.com",
        ]),
    ]
    for nombre_g, hora, jugadores in cfg:
        if frappe.db.exists(
            "grupo por ronda", {"ronda": ronda1, "nombre_del_grupo": nombre_g}
        ):
            continue
        g = frappe.new_doc("grupo por ronda")
        g.ronda            = ronda1
        g.nombre_del_grupo = nombre_g
        g.hora_de_salida   = hora
        for email in jugadores:
            part = frappe.db.get_value(
                "participacion en torneo",
                {"torneo": torneo_name, "jugador": email}, "name"
            )
            g.append("jugadores", {"jugador": email, "participacion": part})
        g.flags.ignore_permissions = True
        g.insert()


def _registrar_puntuaciones(ronda1, torneo_name):
    frappe.db.set_value("ronda", ronda1, "estado", "En curso", update_modified=False)
    frappe.db.commit()

    for email, golpes_lista in _SCORES.items():
        for i, golpes in enumerate(golpes_lista):
            hoyo = i + 1
            par  = _PARES[i]
            if frappe.db.exists(
                "puntuacion por hoyo",
                {"ronda": ronda1, "jugador": email, "numero_de_hoyo": hoyo},
            ):
                continue
            s = frappe.new_doc("puntuacion por hoyo")
            s.ronda             = ronda1
            s.jugador           = email
            s.numero_de_hoyo    = hoyo
            s.golpes_brutos     = golpes
            s.par_del_hoyo      = par
            s.puntos_stableford = max(0, par + 2 - golpes)
            s.flag_penalizacion = 0
            s.flags.ignore_permissions = True
            s.flags.ignore_validate    = True
            s.insert()

    for email, golpes_lista in _SCORES.items():
        part = frappe.db.get_value(
            "participacion en torneo",
            {"torneo": torneo_name, "jugador": email}, "name"
        )
        if part:
            frappe.db.set_value(
                "participacion en torneo", part,
                "puntuacion_total_acumulada", float(sum(golpes_lista)),
                update_modified=False,
            )

    _recalcular_ranking(torneo_name)


def _completar_ronda(ronda1):
    frappe.db.set_value("ronda", ronda1, "estado", "Completada", update_modified=False)


def _recalcular_ranking(torneo_name):
    rows = frappe.get_all(
        "participacion en torneo",
        filters={"torneo": torneo_name},
        fields=["name", "puntuacion_total_acumulada"],
        order_by="puntuacion_total_acumulada asc",
    )
    pos = 1
    for i, r in enumerate(rows):
        if i > 0 and r.puntuacion_total_acumulada == rows[i-1].puntuacion_total_acumulada:
            p = rows[i-1]._p
        else:
            p = pos
        r._p = p
        pos = i + 2
    for r in rows:
        frappe.db.set_value(
            "participacion en torneo", r.name,
            "posicion_en_ranking", r._p, update_modified=False
        )

def revert():
    torneo_name = frappe.db.get_value(
        "torneo de golf", {"nombre_del_torneo": _TORNEO_NOMBRE}, "name"
    )
    if torneo_name:
        for r in frappe.get_all("ronda", filters={"torneo": torneo_name}, pluck="name"):
            frappe.db.delete("puntuacion por hoyo", {"ronda": r})
            frappe.db.delete("grupo por ronda",     {"ronda": r})
        frappe.db.delete("ronda",                    {"torneo": torneo_name})
        frappe.db.delete("participacion en torneo",  {"torneo": torneo_name})
        doc = frappe.get_doc("torneo de golf", torneo_name)
        if doc.docstatus == 1:
            doc.flags.ignore_permissions = True
            doc.cancel()
        frappe.delete_doc("torneo de golf", torneo_name, force=True)

    if frappe.db.exists("campo de golf", _CAMPO):
        frappe.delete_doc("campo de golf", _CAMPO, force=True)

    for email, _, _ in _USUARIOS:
        if frappe.db.exists("User", email):
            frappe.delete_doc("User", email, force=True)

    frappe.db.commit()
    print("Datos de prueba eliminados.")
