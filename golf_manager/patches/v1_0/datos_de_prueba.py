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

_CAMPO         = "Club de Golf Las Palomas"
_FMT_STROKE    = "Stroke Play Estandar"       # coincide con inserción inicial
_FMT_STABLE    = "Stableford Estandar"
_FMT_MATCH     = "Match Play Estandar"

# -------------------------------------------------------------------
# Torneo Stroke Play (original)
# -------------------------------------------------------------------
_TORNEO_STROKE_NOMBRE = "Torneo de Prueba 2026"

_PARTICIPACIONES_STROKE = [
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

_PARES = [4, 3, 5, 4, 4, 3, 5, 4, 4, 4, 3, 5, 4, 4, 3, 5, 4, 4]

_SCORES_STROKE = {
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

# -------------------------------------------------------------------
# Torneo Stableford
# -------------------------------------------------------------------
_TORNEO_STABLEFORD_NOMBRE = "Torneo Stableford 2026"

_PARTICIPACIONES_STABLEFORD = [
    (f"{_PREFIJO}.jugador01@example.com", "Amateur A",  4.2),
    (f"{_PREFIJO}.jugador02@example.com", "Amateur A",  6.8),
    (f"{_PREFIJO}.jugador03@example.com", "Amateur A",  9.1),
    (f"{_PREFIJO}.jugador04@example.com", "Amateur B", 14.5),
    (f"{_PREFIJO}.jugador05@example.com", "Amateur B", 17.0),
    (f"{_PREFIJO}.jugador06@example.com", "Amateur B", 19.3),
    (f"{_PREFIJO}.jugador07@example.com", "Amateur C", 24.6),
    (f"{_PREFIJO}.jugador08@example.com", "Amateur C", 27.2),
]

_SCORES_STABLEFORD = {
    f"{_PREFIJO}.jugador01@example.com": [4,3,4,4,4,3,5,4,4, 4,2,5,4,4,3,5,4,4],
    f"{_PREFIJO}.jugador02@example.com": [4,3,5,4,5,3,5,4,4, 4,3,5,4,4,3,5,4,5],
    f"{_PREFIJO}.jugador03@example.com": [5,3,5,4,4,3,5,5,4, 4,3,5,4,4,4,5,4,4],
    f"{_PREFIJO}.jugador04@example.com": [5,4,5,4,5,3,5,4,5, 4,3,5,5,4,3,5,5,4],
    f"{_PREFIJO}.jugador05@example.com": [5,4,6,4,5,4,5,4,5, 5,3,5,4,5,3,5,5,4],
    f"{_PREFIJO}.jugador06@example.com": [5,4,5,5,5,3,6,4,5, 4,4,5,5,4,4,5,5,5],
    f"{_PREFIJO}.jugador07@example.com": [6,4,6,5,5,4,6,5,5, 5,4,6,5,5,4,6,5,5],
    f"{_PREFIJO}.jugador08@example.com": [6,4,6,5,6,4,6,5,5, 5,4,6,5,5,4,6,5,6],
}

# -------------------------------------------------------------------
# Torneo Matchplay
# -------------------------------------------------------------------
_TORNEO_MATCHPLAY_NOMBRE = "Torneo Matchplay 2026"

_PARTICIPACIONES_MATCHPLAY = _PARTICIPACIONES_STROKE  # mismos 12


# ================================================================
# Helpers reutilizables
# ================================================================

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


def _completar_ronda(ronda):
    frappe.db.set_value("ronda", ronda, "estado", "Completada", update_modified=False)


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
            r._p = rows[i-1]._p
        else:
            r._p = pos
            pos += 1
    for r in rows:
        frappe.db.set_value(
            "participacion en torneo", r.name,
            "posicion_en_ranking", r._p,
            update_modified=False
        )


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


def _crear_participaciones(torneo_name, participaciones):
    for email, cat, hcp in participaciones:
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


# ================================================================
# Torneo Stroke Play
# ================================================================

def _crear_torneo_stroke():
    existente = frappe.db.get_value(
        "torneo de golf", {"nombre_del_torneo": _TORNEO_STROKE_NOMBRE}, "name"
    )
    if existente:
        return existente

    if not frappe.db.exists("formato de torneo", _FMT_STROKE):
        # Esto no debería ocurrir si ya se ejecutó insertar_datos_iniciales
        f = frappe.new_doc("formato de torneo")
        f.nombre                   = _FMT_STROKE
        f.tipo_de_formato          = "Stroke Play"
        f.aplica_handicap_ajustado = 0
        f.criterio_de_desempate    = "Mejor ultima ronda, luego menor handicap"
        f.flags.ignore_permissions = True
        f.insert()

    t = frappe.new_doc("torneo de golf")
    t.nombre_del_torneo = _TORNEO_STROKE_NOMBRE
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


def _crear_grupos_stroke(ronda1, torneo_name):
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


def _registrar_puntuaciones_stroke(ronda, torneo_name, scores):
    frappe.db.set_value("ronda", ronda, "estado", "En curso", update_modified=False)
    frappe.db.commit()

    for email, golpes_lista in scores.items():
        for i, golpes in enumerate(golpes_lista):
            hoyo = i + 1
            par  = _PARES[i]
            if frappe.db.exists(
                "puntuacion por hoyo",
                {"ronda": ronda, "jugador": email, "numero_de_hoyo": hoyo},
            ):
                continue
            s = frappe.new_doc("puntuacion por hoyo")
            s.ronda             = ronda
            s.jugador           = email
            s.numero_de_hoyo    = hoyo
            s.golpes_brutos     = golpes
            s.par_del_hoyo      = par
            s.puntos_stableford = max(0, par + 2 - golpes)  # simplificación
            s.flag_penalizacion = 0
            s.flags.ignore_permissions = True
            s.flags.ignore_validate    = True
            s.insert()

    # Actualizar totales (golpes netos totales)
    for email in scores:
        part = frappe.db.get_value(
            "participacion en torneo",
            {"torneo": torneo_name, "jugador": email}, "name"
        )
        if part:
            frappe.db.set_value(
                "participacion en torneo", part,
                "puntuacion_total_acumulada", float(sum(scores[email])),
                update_modified=False,
            )
    _recalcular_ranking(torneo_name)


# ================================================================
# Torneo Stableford
# ================================================================

def _crear_torneo_stableford():
    existente = frappe.db.get_value(
        "torneo de golf", {"nombre_del_torneo": _TORNEO_STABLEFORD_NOMBRE}, "name"
    )
    if existente:
        return existente

    if not frappe.db.exists("formato de torneo", _FMT_STABLE):
        # por si acaso no se corrió inserción inicial
        f = frappe.new_doc("formato de torneo")
        f.nombre                   = _FMT_STABLE
        f.tipo_de_formato          = "Stableford"
        f.aplica_handicap_ajustado = 1
        f.criterio_de_desempate    = "Mejor ultima ronda, luego menor handicap"
        f.flags.ignore_permissions = True
        f.insert()

    t = frappe.new_doc("torneo de golf")
    t.nombre_del_torneo = _TORNEO_STABLEFORD_NOMBRE
    t.campo_de_golf     = _CAMPO
    t.formato           = _FMT_STABLE
    t.estado            = "Activo"
    t.fecha_de_inicio   = add_days(today(), -1)
    t.fecha_de_fin      = add_days(today(), 1)
    t.numero_de_rondas  = 2
    t.flags.ignore_permissions = True
    t.insert()
    t.flags.ignore_permissions = True
    t.submit()
    return t.name


def _registrar_puntuaciones_stableford(ronda, torneo_name, scores):
    """
    Asigna puntos stableford basados en neto ajustado por hándicap.
    Reparto simple: floor(hcp/18) por hoyo.
    """
    frappe.db.set_value("ronda", ronda, "estado", "En curso", update_modified=False)
    frappe.db.commit()

    # Obtener hándicap de inscripción de cada jugador
    hcp_map = {}
    for email, cat, hcp in _PARTICIPACIONES_STABLEFORD:
        hcp_map[email] = hcp

    for email, golpes_lista in scores.items():
        hcp = hcp_map.get(email, 0)
        # golpes de ventaja por hoyo (simple)
        ventaja_por_hoyo = int(hcp // 18)
        # los hoyos restantes (si hcp%18 != 0) los asignamos a los hoyos más difíciles,
        # pero para testing usamos solo la parte entera.
        for i, golpes in enumerate(golpes_lista):
            hoyo = i + 1
            par  = _PARES[i]
            if frappe.db.exists(
                "puntuacion por hoyo",
                {"ronda": ronda, "jugador": email, "numero_de_hoyo": hoyo},
            ):
                continue
            net_score = golpes - ventaja_por_hoyo
            if net_score <= par - 3:
                puntos = 4
            elif net_score == par - 2:
                puntos = 3
            elif net_score == par - 1:
                puntos = 2
            elif net_score == par:
                puntos = 1
            else:
                puntos = 0

            s = frappe.new_doc("puntuacion por hoyo")
            s.ronda             = ronda
            s.jugador           = email
            s.numero_de_hoyo    = hoyo
            s.golpes_brutos     = golpes
            s.par_del_hoyo      = par
            s.puntos_stableford = puntos
            s.flag_penalizacion = 0
            s.flags.ignore_permissions = True
            s.flags.ignore_validate    = True
            s.insert()

    # Actualizar total acumulado con puntos stableford
    for email in scores:
        part = frappe.db.get_value(
            "participacion en torneo",
            {"torneo": torneo_name, "jugador": email}, "name"
        )
        if part:
            total = frappe.db.sql(
                """SELECT SUM(puntos_stableford)
                   FROM `tabpuntuacion por hoyo`
                   WHERE jugador = %s AND ronda = %s""",
                (email, ronda)
            )[0][0] or 0
            frappe.db.set_value(
                "participacion en torneo", part,
                "puntuacion_total_acumulada", total,
                update_modified=False,
            )
    _recalcular_ranking(torneo_name)


# ================================================================
# Torneo Matchplay
# ================================================================

def _crear_torneo_matchplay():
    existente = frappe.db.get_value(
        "torneo de golf", {"nombre_del_torneo": _TORNEO_MATCHPLAY_NOMBRE}, "name"
    )
    if existente:
        return existente

    if not frappe.db.exists("formato de torneo", _FMT_MATCH):
        f = frappe.new_doc("formato de torneo")
        f.nombre                   = _FMT_MATCH
        f.tipo_de_formato          = "Match Play"
        f.aplica_handicap_ajustado = 1
        f.criterio_de_desempate    = "Muerte subita"
        f.flags.ignore_permissions = True
        f.insert()

    t = frappe.new_doc("torneo de golf")
    t.nombre_del_torneo = _TORNEO_MATCHPLAY_NOMBRE
    t.campo_de_golf     = _CAMPO
    t.formato           = _FMT_MATCH
    t.estado            = "Activo"
    t.fecha_de_inicio   = add_days(today(), -2)
    t.fecha_de_fin      = today()
    t.numero_de_rondas  = 3
    t.flags.ignore_permissions = True
    t.insert()
    t.flags.ignore_permissions = True
    t.submit()
    return t.name


def _crear_grupos_matchplay(ronda, torneo_name):
    jugadores = [email for email, _, _ in _PARTICIPACIONES_MATCHPLAY]
    parejas = [jugadores[i:i+2] for i in range(0, len(jugadores), 2)]

    # Generar horas válidas: 07:30, 07:40, 07:50, 08:00, 08:10, 08:20
    horas = []
    base_hora, base_min = 7, 30
    for i in range(len(parejas)):
        hora_str = f"{base_hora:02d}:{base_min:02d}:00"
        horas.append(hora_str)
        base_min += 10
        if base_min >= 60:
            base_min -= 60
            base_hora += 1

    for idx, par in enumerate(parejas):
        if len(par) < 2:
            continue
        nombre_g = f"Match {idx+1} - {horas[idx][:5]}"  # "07:30"
        hora = horas[idx]

        if frappe.db.exists(
            "grupo por ronda", {"ronda": ronda, "nombre_del_grupo": nombre_g}
        ):
            continue
        g = frappe.new_doc("grupo por ronda")
        g.ronda            = ronda
        g.nombre_del_grupo = nombre_g
        g.hora_de_salida   = hora
        for email in par:
            part = frappe.db.get_value(
                "participacion en torneo",
                {"torneo": torneo_name, "jugador": email}, "name"
            )
            g.append("jugadores", {"jugador": email, "participacion": part})
        g.flags.ignore_permissions = True
        g.insert()


# ================================================================
# Ejecución principal
# ================================================================

def execute():
    frappe.logger().info("Golf Manager: cargando datos de prueba extendidos...")
    _crear_usuarios()
    _crear_campo()

    # --- Stroke Play ---
    torneo_stroke = _crear_torneo_stroke()
    r1_stroke, r2_stroke = _crear_ronda(torneo_stroke, 1, today()), _crear_ronda(torneo_stroke, 2, add_days(today(), 1))
    _crear_participaciones(torneo_stroke, _PARTICIPACIONES_STROKE)
    _crear_grupos_stroke(r1_stroke, torneo_stroke)
    _registrar_puntuaciones_stroke(r1_stroke, torneo_stroke, _SCORES_STROKE)
    _completar_ronda(r1_stroke)

    # --- Stableford ---
    torneo_stable = _crear_torneo_stableford()
    r1_stable, r2_stable = _crear_ronda(torneo_stable, 1, add_days(today(), -1)), _crear_ronda(torneo_stable, 2, add_days(today(), 0))
    _crear_participaciones(torneo_stable, _PARTICIPACIONES_STABLEFORD)
    _registrar_puntuaciones_stableford(r1_stable, torneo_stable, _SCORES_STABLEFORD)
    _completar_ronda(r1_stable)

    # --- Matchplay ---
    torneo_match = _crear_torneo_matchplay()
    r1_match = _crear_ronda(torneo_match, 1, add_days(today(), -2))
    r2_match = _crear_ronda(torneo_match, 2, add_days(today(), -1))
    r3_match = _crear_ronda(torneo_match, 3, add_days(today(), 0))
    _crear_participaciones(torneo_match, _PARTICIPACIONES_MATCHPLAY)
    _crear_grupos_matchplay(r1_match, torneo_match)
    # Matchplay se deja sin puntuaciones para probar captura manual

    frappe.db.commit()
    print("\nListo. Tres torneos de prueba creados.")
    print(f"  Stroke Play : {torneo_stroke}")
    print(f"  Stableford  : {torneo_stable}")
    print(f"  Match Play  : {torneo_match}")
    print("  Contraseña   : Test@12345\n")


def revert():
    # Eliminar torneos en orden inverso
    def _eliminar_torneo(nombre_torneo):
        torneo = frappe.db.get_value("torneo de golf", {"nombre_del_torneo": nombre_torneo}, "name")
        if not torneo:
            return
        for r in frappe.get_all("ronda", filters={"torneo": torneo}, pluck="name"):
            frappe.db.delete("puntuacion por hoyo", {"ronda": r})
            frappe.db.delete("grupo por ronda", {"ronda": r})
        frappe.db.delete("ronda", {"torneo": torneo})
        frappe.db.delete("participacion en torneo", {"torneo": torneo})
        doc = frappe.get_doc("torneo de golf", torneo)
        if doc.docstatus == 1:
            doc.flags.ignore_permissions = True
            doc.cancel()
        frappe.delete_doc("torneo de golf", torneo, force=True)

    _eliminar_torneo(_TORNEO_MATCHPLAY_NOMBRE)
    _eliminar_torneo(_TORNEO_STABLEFORD_NOMBRE)
    _eliminar_torneo(_TORNEO_STROKE_NOMBRE)

    if frappe.db.exists("campo de golf", _CAMPO):
        frappe.delete_doc("campo de golf", _CAMPO, force=True)

    for email, _, _ in _USUARIOS:
        if frappe.db.exists("User", email):
            frappe.delete_doc("User", email, force=True)

    frappe.db.commit()
    print("Todos los datos de prueba han sido eliminados.")
