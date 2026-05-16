frappe.ui.form.on("torneo de golf", {

	refresh(frm) {
		frm.trigger("_render_estado_badge");
		frm.trigger("_setup_botones");
		setTimeout(() => frm.trigger("_render_panel_rondas"), 300);
	},

	_render_estado_badge(frm) {
		const colores = { Borrador: "gray", Activo: "green", Finalizado: "blue" };
		frm.page.set_indicator(frm.doc.estado, colores[frm.doc.estado] || "gray");
	},

	_setup_botones(frm) {
		frm.add_custom_button(__("Ver ranking"), () => {
			frappe.call({
				method: "golf_manager.golf_manager.api.get_ranking",
				args:   { torneo: frm.doc.name, usar_cache: 0 },
				freeze: true,
				freeze_message: __("Cargando ranking..."),
				callback(r) {
					if (r.message) {
						_mostrar_ranking_dialog(r.message);
					} else {
						frappe.msgprint(__("No se pudo obtener el ranking."));
					}
				},
			});
		}, __("Reportes"));

		frm.add_custom_button(__("PDF — Brackets de rondas"), () => {
			_descargar_pdf(frm, "brackets_torneo");
		}, __("Reportes"));

		frm.add_custom_button(__("PDF — Puntuaciones por jugador"), () => {
			_descargar_pdf(frm, "puntuaciones_torneo");
		}, __("Reportes"));

		if (frm.doc.docstatus === 1 && frm.doc.estado === "Activo") {
			frm.add_custom_button(__("Finalizar torneo"), () => {
				frappe.confirm(
					__("¿Confirma que desea finalizar el torneo? Esta acción no se puede deshacer."),
					() => {
						frm.call("finalizar").then(() => {
							frappe.show_alert({
								message:   __("Torneo finalizado correctamente."),
								indicator: "green",
							});
							frm.reload_doc();
						});
					}
				);
			}, __("Acciones"));

			frm.add_custom_button(__("Nueva ronda"), () => {
				frm.trigger("_crear_ronda");
			}, __("Acciones"));
		}
	},

	_render_panel_rondas(frm) {
		if (frm.is_new()) return;

		const PANEL = "golf-rondas-panel";
		$(frm.wrapper).find(`.${PANEL}`).remove();

		frappe.db
			.get_list("ronda", {
				filters:  { torneo: frm.doc.name },
				fields:   ["name", "numero_de_ronda", "fecha", "estado"],
				order_by: "numero_de_ronda asc",
			})
			.then((rondas) => {
				$(frm.wrapper).find(`.${PANEL}`).remove();

				const PILL = { Pendiente: "gray", "En curso": "orange", Completada: "green" };

				const filas = rondas.length
					? rondas.map((r) => `
						<tr>
							<td><a href="/app/ronda/${r.name}">${__("Ronda")} ${r.numero_de_ronda}</a></td>
							<td>${frappe.datetime.str_to_user(r.fecha)}</td>
							<td><span class="indicator-pill ${PILL[r.estado] || "gray"}">${r.estado}</span></td>
							<td>
								<a class="btn btn-xs btn-default"
									href="/app/puntuacion-por-hoyo?ronda=${r.name}">
									${__("Puntuaciones")}
								</a>
							</td>
						</tr>`).join("")
					: `<tr><td colspan="4" class="text-center text-muted">${__("Sin rondas creadas.")}</td></tr>`;

				const html = `
					<div class="${PANEL}"
						style="margin:20px 15px 0;background:var(--card-bg,#fff);
							   border:1px solid var(--border-color,#d1d8dd);
							   border-radius:var(--border-radius,6px);padding:14px 16px;">
						<div style="font-weight:600;font-size:12px;color:var(--text-muted,#8d99a6);
									text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px;">
							${__("Rondas del torneo")}
						</div>
						<table class="table table-bordered table-condensed" style="margin:0">
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

				const $anchor =
					$(frm.wrapper).find(".form-layout-flex").first() ||
					$(frm.wrapper).find(".form-page").first()        ||
					$(frm.wrapper).find(".page-content-wrapper").first();

				if ($anchor && $anchor.length) {
					$anchor.append(html);
				} else {
					$(frm.wrapper).append(html);
				}
			});
	},

	_crear_ronda(frm) {
		frappe.db
			.get_list("ronda", {
				filters:  { torneo: frm.doc.name },
				fields:   ["numero_de_ronda"],
				order_by: "numero_de_ronda desc",
				limit:    1,
			})
			.then((res) => {
				const siguiente = res.length ? res[0].numero_de_ronda + 1 : 1;

				if (siguiente > frm.doc.numero_de_rondas) {
					frappe.msgprint(
						__("El torneo ya tiene todas sus rondas creadas ({0}).", [frm.doc.numero_de_rondas])
					);
					return;
				}

				const d = new frappe.ui.Dialog({
					title: __("Nueva ronda {0}", [siguiente]),
					fields: [{
						fieldname: "fecha",
						fieldtype: "Date",
						label:     __("Fecha de la ronda"),
						reqd:      1,
					}],
					primary_action_label: __("Crear"),
					primary_action(values) {
						frappe.new_doc("ronda", {
							torneo:          frm.doc.name,
							numero_de_ronda: siguiente,
							fecha:           values.fecha,
							estado:          "Pendiente",
						});
						d.hide();
					},
				});
				d.show();
			});
	},

	fecha_de_fin(frm) {
		if (frm.doc.fecha_de_inicio && frm.doc.fecha_de_fin) {
			if (frm.doc.fecha_de_fin < frm.doc.fecha_de_inicio) {
				frappe.msgprint(__("La fecha de fin no puede ser anterior a la fecha de inicio."));
				frm.set_value("fecha_de_fin", "");
			}
		}
	},
});


function _descargar_pdf(frm, formato) {
    const params = new URLSearchParams({
        docname: frm.doc.name,
        formato,
        cmd: "golf_manager.golf_manager.pdf_export.descargar_pdf_torneo",
    });
    window.open(`/api/method/golf_manager.golf_manager.pdf_export.descargar_pdf_torneo?${params}`, "_blank");
}


function _mostrar_ranking_dialog(data) {
	if (!data || !data.ranking) {
		frappe.msgprint(__("No hay datos de ranking disponibles."));
		return;
	}

	const info   = data.torneo_info || {};
	const titulo = info.nombre || __("Ranking");

	const BADGE = {
		1: `<span style="background:#ffc107;color:#212529;padding:1px 8px;border-radius:3px;font-weight:700">1°</span>`,
		2: `<span style="background:#6c757d;color:#fff;padding:1px 8px;border-radius:3px;font-weight:700">2°</span>`,
		3: `<span style="background:#cd7f32;color:#fff;padding:1px 8px;border-radius:3px;font-weight:700">3°</span>`,
	};

	const filas = data.ranking.length
		? data.ranking.map((p) => `
			<tr>
				<td style="text-align:center">
					${BADGE[p.posicion_en_ranking] || (p.posicion_en_ranking ?? "—")}
				</td>
				<td><strong>${p.nombre_jugador || p.jugador}</strong></td>
				<td>${p.categoria || "—"}</td>
				<td style="text-align:center">${p.handicap_inscripcion ?? "—"}</td>
				<td style="text-align:center;font-weight:600">${p.puntuacion_total_acumulada ?? "—"}</td>
			</tr>`).join("")
		: `<tr><td colspan="5" class="text-center text-muted">${__("Sin resultados registrados.")}</td></tr>`;

	frappe.msgprint({
		title:   `${titulo} — ${info.estado || ""}`,
		message: `
			<div style="font-size:12px;color:#6c757d;margin-bottom:8px">
				${__("Campo")}: <strong>${info.campo || "—"}</strong>
				&nbsp;·&nbsp;
				${__("Formato")}: <strong>${info.formato || "—"}</strong>
			</div>
			<table class="table table-bordered table-condensed" style="margin:0;font-size:13px">
				<thead style="background:#1a5276;color:#fff">
					<tr>
						<th style="text-align:center;width:50px">#</th>
						<th>${__("Jugador")}</th>
						<th>${__("Categoría")}</th>
						<th style="text-align:center">${__("Hcp")}</th>
						<th style="text-align:center">${__("Puntuación")}</th>
					</tr>
				</thead>
				<tbody>${filas}</tbody>
			</table>`,
		wide: true,
	});
}
