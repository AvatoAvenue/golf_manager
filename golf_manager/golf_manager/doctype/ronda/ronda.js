// Copyright (c) 2026, avato and contributors
// For license information, please see license.txt

frappe.ui.form.on("ronda", {
	refresh(frm) {
		frm.trigger("_render_estado_badge");
		frm.trigger("_setup_botones_estado");
		frm.trigger("_render_panel_grupos");
	},

	//  Estado visual

	_render_estado_badge(frm) {
		const colores = { Pendiente: "gray", "En curso": "orange", Completada: "green" };
		frm.page.set_indicator(frm.doc.estado, colores[frm.doc.estado] || "gray");
	},

	//  Botones de transición de estado

	_setup_botones_estado(frm) {
		if (frm.is_new()) return;

		if (frm.doc.estado === "Pendiente") {
			frm.add_custom_button(__("Iniciar ronda"), () => {
				frm.trigger("_cambiar_estado", "En curso");
			}, __("Acciones"));
		}

		if (frm.doc.estado === "En curso") {
			frm.add_custom_button(__("Registrar puntuación"), () => {
				frappe.new_doc("puntuacion por hoyo", { ronda: frm.doc.name });
			}, __("Acciones"));

			frm.add_custom_button(__("Completar ronda"), () => {
				frappe.confirm(
					__("¿Confirma que todos los jugadores han terminado la ronda?"),
					() => frm.trigger("_cambiar_estado", "Completada")
				);
			}, __("Acciones"));
		}

		if (frm.doc.estado === "Completada") {
			frm.add_custom_button(__("Ver puntuaciones"), () => {
				frappe.set_route("List", "puntuacion por hoyo", { ronda: frm.doc.name });
			}, __("Reportes"));
		}
	},

	_cambiar_estado(frm, nuevo_estado) {
		frappe.db.set_value("ronda", frm.doc.name, "estado", nuevo_estado).then(() => {
			frappe.show_alert({ message: __("Estado actualizado: {0}", [nuevo_estado]), indicator: "green" });
			frm.reload_doc();
		});
	},

	//  Panel de grupos

	_render_panel_grupos(frm) {
		if (frm.is_new()) return;

		// Limpiar panel previo antes de cada render para evitar duplicados
		$(frm.wrapper).find(".golf-grupos-panel").remove();

		frappe.db
			.get_list("grupo por ronda", {
				filters: { ronda: frm.doc.name },
				fields: ["name", "nombre_del_grupo", "hora_de_salida"],
				order_by: "hora_de_salida asc",
			})
			.then((grupos) => {
				// Limpiar de nuevo por si llegaron respuestas async solapadas
				$(frm.wrapper).find(".golf-grupos-panel").remove();

				if (!grupos.length) return;

				const filas = grupos
					.map(
						(g) => `
						<tr>
							<td><a href="/app/grupo-por-ronda/${g.name}">${g.nombre_del_grupo}</a></td>
							<td>${g.hora_de_salida || "—"}</td>
						</tr>`
					)
					.join("");

				const html = `
					<div class="form-section golf-grupos-panel">
						<div class="section-head">${__("Grupos de salida")}</div>
						<table class="table table-bordered table-condensed" style="margin-top:8px">
							<thead>
								<tr>
									<th>${__("Grupo")}</th>
									<th>${__("Hora de salida")}</th>
								</tr>
							</thead>
							<tbody>${filas}</tbody>
						</table>
						<a class="btn btn-xs btn-default"
							href="/app/grupo-por-ronda/new-grupo-por-ronda-1?ronda=${frm.doc.name}">
							+ ${__("Nuevo grupo")}
						</a>
					</div>`;

				$(frm.fields_dict["fecha"].wrapper)
					.closest(".form-section")
					.after(html);
			});
	},
});
