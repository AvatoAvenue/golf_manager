import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils.jinja import get_jenv

_PDF_OPTIONS = {
    "load-error-handling": "ignore",
    "load-media-error-handling": "ignore",
    "disable-javascript": "",
    "disable-external-links": "",
    "encoding": "UTF-8",
    "margin-top": "10mm",
    "margin-bottom": "10mm",
    "margin-left": "8mm",
    "margin-right": "8mm",
    "page-size": "A4",
}

_FORMATOS_LANDSCAPE = {"puntuaciones_torneo", "brackets_torneo"}


@frappe.whitelist()
def descargar_pdf_torneo(docname, formato):
    if not frappe.has_permission("torneo de golf", "read", docname):
        frappe.throw(frappe._("Sin permiso."), frappe.PermissionError)

    doc = frappe.get_doc("torneo de golf", docname)

    # Parámetros de filtro opcionales que vienen en la query string
    extra = {
        "categoria":  frappe.form_dict.get("categoria",  "") or "",
        "ronda_idx":  frappe.form_dict.get("ronda_idx",  "") or "",
    }

    html = _renderizar(formato, doc, extra)

    options = dict(_PDF_OPTIONS)
    if formato in _FORMATOS_LANDSCAPE:
        options["orientation"] = "Portrait"

    pdf = get_pdf(html, options=options)

    frappe.local.response.filename = f"{docname}_{formato}.pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "pdf"


def _renderizar(formato, doc, extra=None):
    import os
    app_path = frappe.get_app_path("golf_manager")
    template_path = os.path.join(app_path, "print_format", f"{formato}.html")

    if not os.path.exists(template_path):
        frappe.throw(frappe._("Print format no encontrado: {0}").format(formato))

    template_src = open(template_path).read()
    env = get_jenv()

    render_ctx = {"doc": doc, "frappe": frappe}
    if extra:
        render_ctx.update(extra)

    body = env.from_string(template_src).render(**render_ctx)

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
* {{ box-sizing: border-box; }}
body {{ font-family: Arial, Helvetica, sans-serif; font-size: 10pt; color: #111; background: #fff; }}
</style>
</head><body>{body}</body></html>"""
