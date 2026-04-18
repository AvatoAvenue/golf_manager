// Copyright (c) 2026, avato and contributors
// For license information, please see license.txt

frappe.ui.form.on("torneo de golf", {
	//  Refresh: botones y estado visual

	refresh(frm) {
		frm.trigger("_render_estado_badge");
		frm.trigger("_setup_botones");
		frm.trigger("_render_panel_rondas");
	},

	//  Estado visual

	_render_estado_badge(frm) {
		const colores = {
			Borrador: "gray",
			Activo: "green",
			Finalizado: "blue",
		};
		const color = colores[frm.doc.estado] || "gray";
		frm.page.set_indicator(frm.doc.estado, color);
	},

	//  Botones de acción

	_setup_botones(frm) {
		// Botón: Ver ranking público
		frm.add_custom_button(__("Ver ranking"), () => {
			frappe.call({
				method: "golf_manager.golf_manager.api.get_ranking",
				args: { torneo: frm.doc.name },
				callback(r) {
					if (r.message) {
						frm.trigger("_mostrar_ranking_dialog", r.message);
					}
				},
			});
		}, __("Reportes"));

		// Botón: Finalizar torneo si se esta activo y enviado
		if (frm.doc.docstatus === 1 && frm.doc.estado === "Activo") {
			frm.add_custom_button(__("Finalizar torneo"), () => {
				frappe.confirm(
					__("¿Confirma que desea finalizar el torneo? Esta acción no se puede deshacer."),
					() => {
						frm.call("finalizar").then(() => {
							frappe.show_alert({
								message: __("Torneo finalizado correctamente."),
								indicator: "green",
							});
							frm.reload_doc();
						});
					}
				);
			}, __("Acciones"));
		}

		// Botón: Nueva ronda si está activo
		if (frm.doc.docstatus === 1 && frm.doc.estado === "Activo") {
			frm.add_custom_button(__("Nueva ronda"), () => {
				frm.trigger("_crear_ronda");
			}, __("Acciones"));
		}
	},

	//  Panel de rondas

	_render_panel_rondas(frm) {
		if (frm.is_new()) return;

		// Eliminar cualquier panel previo antes de renderizar uno nuevo.
		// Esto evita la duplicación cuando refresh se dispara varias veces.
		$(frm.wrapper).find(".golf-rondas-panel").remove();

		frappe.db
			.get_list("ronda", {
				filters: { torneo: frm.doc.name },
				fields: ["name", "numero_de_ronda", "fecha", "estado"],
				order_by: "numero_de_ronda asc",
			})
			.then((rondas) => {
				// Limpiar de nuevo por si llegaron dos respuestas async solapadas
				$(frm.wrapper).find(".golf-rondas-panel").remove();

				if (!rondas.length) return;

				const colores_estado = {
					Pendiente: "gray",
					"En curso": "orange",
					Completada: "green",
				};

				const filas = rondas
					.map((r) => {
						const color = colores_estado[r.estado] || "gray";
						const badge = `<span class="indicator-pill ${color}">${r.estado}</span>`;
						return `
							<tr>
								<td><a href="/app/ronda/${r.name}">Ronda ${r.numero_de_ronda}</a></td>
								<td>${frappe.datetime.str_to_user(r.fecha)}</td>
								<td>${badge}</td>
								<td>
									<a class="btn btn-xs btn-default"
										href="/app/puntuacion-por-hoyo?ronda=${r.name}">
										${__("Puntuaciones")}
									</a>
								</td>
							</tr>`;
					})
					.join("");

				const html = `
					<div class="form-section golf-rondas-panel">
						<div class="section-head">${__("Rondas del torneo")}</div>
						<table class="table table-bordered table-condensed" style="margin-top:8px">
							<thead>
								<tr>
									<th>${__("Ronda")}</th>
									<th>${__("Fecha")}</th>
									<th>${__("Estado")}</th>
									<th></th>
								</tr>
							</thead>
							<tbody>${filas}</tbody>
						</table>
					</div>`;

				// Insertar una única vez después del campo descripción
				$(frm.fields_dict["descripcion"].wrapper)
					.closest(".form-column")
					.after(html);
			});
	},

	//  Crear ronda rápida

	_crear_ronda(frm) {
		frappe.db
			.get_list("ronda", {
				filters: { torneo: frm.doc.name },
				fields: ["numero_de_ronda"],
				order_by: "numero_de_ronda desc",
				limit: 1,
			})
			.then((res) => {
				const siguiente = res.length ? res[0].numero_de_ronda + 1 : 1;

				if (siguiente > frm.doc.numero_de_rondas) {
					frappe.msgprint(__("El torneo ya tiene todas sus rondas creadas ({0}).", [frm.doc.numero_de_rondas]));
					return;
				}

				const d = new frappe.ui.Dialog({
					title: __("Nueva ronda {0}", [siguiente]),
					fields: [
						{
							fieldname: "fecha",
							fieldtype: "Date",
							label: __("Fecha de la ronda"),
							reqd: 1,
						},
					],
					primary_action_label: __("Crear"),
					primary_action(values) {
						frappe.new_doc("ronda", {
							torneo: frm.doc.name,
							numero_de_ronda: siguiente,
							fecha: values.fecha,
							estado: "Pendiente",
						});
						d.hide();
					},
				});
				d.show();
			});
	},

	//  Dialog de ranking

	_mostrar_ranking_dialog(frm, data) {
		const filas = (data.ranking || [])
			.map(
				(p) => `
				<tr>
					<td>${p.posicion_en_ranking || "-"}</td>
					<td>${p.nombre_jugador || p.jugador}</td>
					<td>${p.categoria}</td>
					<td>${p.puntuacion_total_acumulada ?? "-"}</td>
				</tr>`
			)
			.join("");

		frappe.msgprint({
			title: __("Ranking — {0}", [data.torneo_info?.nombre || frm.doc.nombre_del_torneo]),
			message: `
				<table class="table table-bordered table-condensed">
					<thead>
						<tr>
							<th>#</th>
							<th>${__("Jugador")}</th>
							<th>${__("Categoría")}</th>
							<th>${__("Puntuación")}</th>
						</tr>
					</thead>
					<tbody>${filas}</tbody>
				</table>`,
			wide: true,
		});
	},

	//  Validación en cliente

	fecha_de_fin(frm) {
		if (frm.doc.fecha_de_inicio && frm.doc.fecha_de_fin) {
			if (frm.doc.fecha_de_fin < frm.doc.fecha_de_inicio) {
				frappe.msgprint(__("La fecha de fin no puede ser anterior a la fecha de inicio."));
				frm.set_value("fecha_de_fin", "");
			}
		}
	},
});
