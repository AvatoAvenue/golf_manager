// Copyright (c) 2026, avato and contributors
// For license information, please see license.txt

if (typeof MOTIVOS_PENALIZACION === "undefined") {
	var MOTIVOS_PENALIZACION = [
		"Bola fuera de limites",
		"Bola perdida",
		"Hazard de agua",
		"Hazard lateral",
		"Obstruccion inmovible",
		"Obstruccion movible",
		"Terraplay incorrecto",
		"Otro",
	];
}

frappe.ui.form.on("torneo de golf", {

	refresh(frm) {
		frm.trigger("_render_estado_badge");
		frm.trigger("_setup_botones");
		setTimeout(() => frm.trigger("_render_panel_rondas"), 300);
		setTimeout(() => frm.trigger("_render_panel_participantes"), 400);
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

		frm.add_custom_button(__("Brackets de rondas"), () => {
			_dialogo_filtro_brackets(frm);
		}, __("Reportes"));

		frm.add_custom_button(__("Puntuaciones por jugador"), () => {
			_dialogo_filtro_puntuaciones(frm);
		}, __("Reportes"));

		if (frm.doc.docstatus === 1 && frm.doc.estado === "Activo") {
			frm.add_custom_button(__("Capturar puntuaciones"), () => {
				_abrir_captura_puntuaciones(frm);
			}, __("Acciones"));

			frm.add_custom_button(__("Finalizar torneo"), () => {
				frappe.confirm(
					__("Confirma que desea finalizar el torneo? Esta accion no se puede deshacer."),
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

		// Botones siempre disponibles
		frm.add_custom_button(__("Agregar participante"), () => {
			frappe.new_doc("participacion en torneo", {
				torneo: frm.doc.name,
			});
		}, __("Acciones"));

		frm.add_custom_button(__("Ver participantes"), () => {
			frappe.set_route("List", "participacion en torneo", {
				torneo: frm.doc.name,
			});
		}, __("Acciones"));
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

	_render_panel_participantes(frm) {
		if (frm.is_new()) return;

		const PANEL = "golf-participantes-panel";
		$(frm.wrapper).find(`.${PANEL}`).remove();

		frappe.db
			.get_list("participacion en torneo", {
				filters:  { torneo: frm.doc.name },
				fields:   ["name", "jugador", "categoria", "handicap_inscripcion", "posicion_en_ranking"],
				order_by: "categoria asc, posicion_en_ranking asc",
				limit:    100,
			})
			.then((participantes) => {
				$(frm.wrapper).find(`.${PANEL}`).remove();
				if (!participantes.length) return;

				// Obtener nombres completos
				const jugadores = [...new Set(participantes.map(p => p.jugador))];
				frappe.db.get_list("User", {
					filters: [["name", "in", jugadores]],
					fields:  ["name", "full_name"],
					limit:   100,
				}).then((users) => {
					const nombreMap = {};
					users.forEach(u => nombreMap[u.name] = u.full_name);

					const filas = participantes
						.map(p => `
							<tr>
								<td><a href="/app/participacion-en-torneo/${p.name}">
									${nombreMap[p.jugador] || p.jugador}
								</a></td>
								<td>${p.categoria || "—"}</td>
								<td>${p.handicap_inscripcion ?? "—"}</td>
								<td style="text-align:center">${p.posicion_en_ranking || "—"}</td>
							</tr>`)
						.join("");

					const html = `
						<div class="${PANEL}"
							style="margin:20px 15px 0;background:var(--card-bg,#fff);
								   border:1px solid var(--border-color,#d1d8dd);
								   border-radius:var(--border-radius,6px);padding:14px 16px;">
							<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
								<div style="font-weight:600;font-size:12px;color:var(--text-muted,#8d99a6);
											text-transform:uppercase;letter-spacing:.06em;">
									${__("Participantes")} (${participantes.length})
								</div>
								<a class="btn btn-xs btn-primary"
									href="/app/participacion-en-torneo/new-participacion-en-torneo-1?torneo=${frm.doc.name}">
									+ ${__("Agregar")}
								</a>
							</div>
							<table class="table table-bordered table-condensed" style="margin:0">
								<thead>
									<tr>
										<th>${__("Jugador")}</th>
										<th>${__("Categoría")}</th>
										<th>${__("Hcp")}</th>
										<th style="text-align:center">${__("Pos.")}</th>
									</tr>
								</thead>
								<tbody>${filas}</tbody>
							</table>
						</div>`;

					const $anchor = $(frm.wrapper).find(".form-layout-flex").first();
					if ($anchor && $anchor.length) {
						$anchor.append(html);
					}
				});
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


function _abrir_captura_puntuaciones(frm) {
	frappe.call({
		method:  "golf_manager.golf_manager.api.get_datos_captura_torneo",
		args:    { torneo: frm.doc.name },
		freeze:  true,
		freeze_message: __("Cargando datos..."),
		callback(r) {
			if (!r.message) return;
			const { rondas, participantes, puntuaciones, par_por_hoyo } = r.message;

			if (!rondas.length) {
				frappe.msgprint(__("Este torneo no tiene rondas creadas."));
				return;
			}
			if (!participantes.length) {
				frappe.msgprint(__("No hay participantes inscritos en este torneo."));
				return;
			}

			// Estructurar puntuaciones existentes
			const scores = {};
			for (const p of puntuaciones) {
				if (!scores[p.ronda]) scores[p.ronda] = {};
				if (!scores[p.ronda][p.jugador]) scores[p.ronda][p.jugador] = {};
				scores[p.ronda][p.jugador][p.numero_de_hoyo] = {
					golpes:         p.golpes_brutos || "",
					par:            p.par_del_hoyo  || par_por_hoyo[p.numero_de_hoyo] || 4,
					penalizaciones: p.penalizaciones || [],
				};
			}

			const categorias = [...new Set(participantes.map(p => p.categoria).filter(Boolean))].sort();

			_construir_dialogo_captura(frm, rondas, participantes, scores, par_por_hoyo, categorias);
		},
	});
}

function _construir_dialogo_captura(frm, rondas, participantes, scores, par_por_hoyo, categorias) {
	const par_actual = Object.assign({}, par_por_hoyo);
	let cat_activa = "";

	const COLOR_ESTADO = { Pendiente: "#8d99a6", "En curso": "#f39c12", Completada: "#27ae60" };

	const cat_opts_html = `
		<option value="">Todas las categorías</option>
		${categorias.map(c => `<option value="${c}">${c}</option>`).join("")}`;

	const filtro_html = categorias.length > 1 ? `
		<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap">
			<label style="font-size:12px;font-weight:600;color:#555">Categoría:</label>
			<select id="golf-cap-cat-filter" class="form-control" style="width:200px;font-size:12px;height:28px;padding:2px 6px">
				${cat_opts_html}
			</select>
			<span id="golf-cap-cat-count" style="font-size:11px;color:#888"></span>
		</div>` : "";

	// Tabs de rondas
	const tabs_nav = rondas.map((r, i) => `
		<li class="nav-item">
			<a class="nav-link ${i === 0 ? "active" : ""} golf-cap-tab"
				data-tab="${r.name}"
				href="#"
				data-panel="golf-cap-panel-${i}"
				style="font-size:12px;padding:6px 12px">
				<span style="display:inline-block;width:8px;height:8px;border-radius:50%;
					background:${COLOR_ESTADO[r.estado] || "#ccc"};margin-right:5px"></span>
				${__("R{0}", [r.numero_de_ronda])}
				<small style="color:#aaa;font-weight:400"> ${frappe.datetime.str_to_user(r.fecha)}</small>
			</a>
		</li>`).join("");

	const tabs_content = rondas.map((r, i) => `
		<div class="tab-pane ${i === 0 ? "active" : ""}" id="golf-cap-panel-${i}" data-ronda="${r.name}">
			${_html_tabla_ronda(r, participantes, scores[r.name] || {}, par_actual)}
		</div>`).join("");

	const html = `
		<style>
			.golf-cap-wrap { font-size:12px; }
			.golf-cap-wrap .nav-tabs { border-bottom:2px solid #dee2e6; margin-bottom:12px; }
			.golf-cap-wrap .nav-tabs .nav-link { border:none; border-radius:0; }
			.golf-cap-wrap .nav-tabs .nav-link.active { border-bottom:2px solid #1a5276; color:#1a5276; font-weight:600; background:transparent; }
			.golf-cap-wrap table.golf-grid {
				border-collapse:collapse; width:100%; font-size:11px; table-layout:fixed;
			}
			.golf-cap-wrap table.golf-grid th,
			.golf-cap-wrap table.golf-grid td {
				border:1px solid #dee2e6; padding:2px 3px;
				text-align:center; vertical-align:middle; overflow:hidden;
			}
			.golf-cap-wrap th.col-jugador { width:130px; text-align:left; padding-left:6px; }
			.golf-cap-wrap td.td-jugador  { text-align:left; padding-left:6px; white-space:nowrap;
				overflow:hidden; text-overflow:ellipsis; max-width:130px; }
			.golf-cap-wrap th.col-hoyo  { width:40px; min-width:40px }
			.golf-cap-wrap th.col-sub   { width:34px; background:#2e6aa8; color:#fff; }
			.golf-cap-wrap th.col-accion{ width:70px; }
			.golf-cap-wrap tr.fila-par th { background:#d6eaf8; color:#1a5276; font-weight:700; font-size:10px; }
			.golf-cap-wrap tr.fila-par input.par-input {
				width:34px; text-align:center; border:none; background:transparent;
				font-weight:700; font-size:10px; color:#1a5276; padding:0;
			}
			.golf-cap-wrap input.golpe-input {
				width:34px; text-align:center; border:1px solid #ced4da;
				border-radius:2px; font-size:11px; padding:1px; background:#fff;
			}
			.golf-cap-wrap input.golpe-input:focus { outline:2px solid #2e86c1; border-color:#2e86c1; }
			.golf-cap-wrap input.golpe-input.tiene-pen { border-color:#e67e22; background:#fff8f0; }
			.golf-cap-wrap .btn-guardar-fila { font-size:10px; padding:2px 8px; white-space:nowrap; }
			.golf-cap-wrap .fila-guardada td { background:#f0fff4 !important; }
			.golf-cap-wrap td.td-subtotal { background:#2e6aa8; color:#fff; font-weight:700; }
			.golf-cap-wrap .estado-badge {
				display:inline-block; font-size:10px; font-weight:600;
				padding:1px 7px; border-radius:3px; margin-bottom:8px;
			}
			.golf-cap-wrap .aviso-completada {
				background:#fff3cd; border:1px solid #ffc107;
				border-radius:4px; padding:8px 12px; font-size:12px; margin-bottom:10px;
			}
			.fila-oculta-cat { display:none !important; }
		</style>
		<div class="golf-cap-wrap">
			${filtro_html}
			<ul class="nav nav-tabs">${tabs_nav}</ul>
			<div class="tab-content">${tabs_content}</div>
		</div>`;

	const d = new frappe.ui.Dialog({
		title:  __("Captura de puntuaciones"),
		size:   "extra-large",
		fields: [{ fieldtype: "HTML", fieldname: "contenido_captura" }],
		primary_action_label: __("Cerrar"),
		primary_action() { d.hide(); },
	});

	d.show();
	d.fields_dict.contenido_captura.$wrapper.html(html);

	// Aplicar filtro por categoría
	function _aplicar_filtro_cat(cat) {
		cat_activa = cat;
		d.$wrapper.find("tr[data-jugador]").each(function() {
			const jugador = $(this).data("jugador");
			const part    = participantes.find(p => p.jugador === jugador);
			const cat_jug = part ? part.categoria : "";
			if (!cat || cat_jug === cat) {
				$(this).removeClass("fila-oculta-cat");
			} else {
				$(this).addClass("fila-oculta-cat");
			}
		});
		const visibles = d.$wrapper.find("tr[data-jugador]:not(.fila-oculta-cat)").length;
		d.$wrapper.find("#golf-cap-cat-count").text(
			cat ? `${visibles} jugador(es) en esta categoría` : ""
		);
	}

	d.$wrapper.on("change", "#golf-cap-cat-filter", function() {
		_aplicar_filtro_cat($(this).val());
	});

	// Cambio de pestaña
	d.$wrapper.find(".golf-cap-tab").on("click", function(e) {
		e.preventDefault();
		d.$wrapper.find(".golf-cap-tab").removeClass("active");
		d.$wrapper.find(".tab-pane").removeClass("active");
		$(this).addClass("active");
		const target = $(this).attr("data-panel");
		d.$wrapper.find("#" + target).addClass("active");
		// Reaplicar filtro al cambiar de tab
		_aplicar_filtro_cat(cat_activa);
	});

	_vincular_eventos_grilla(d, frm, rondas, participantes, scores, par_actual);
}

function _html_tabla_ronda(ronda, participantes, scores_ronda, par_actual) {
	const bloqueada = ronda.estado === "Completada";

	let aviso = "";
	if (bloqueada) {
		aviso = `<div class="aviso-completada">
			Esta ronda está completada. Las puntuaciones son de solo lectura.
		</div>`;
	}

	// Cabeceras de hoyos (1..18)
	const th_hoyos = Array.from({length: 18}, (_, i) => {
		const h = i + 1;
		return `<th class="col-hoyo">${h}</th>`;
	}).join("");

	const td_par_front = Array.from({length: 9}, (_, i) => {
		const h = i + 1;
		const par = par_actual[h] || 4;
		if (bloqueada) return `<th>${par}</th>`;
		return `<th><input class="par-input" data-hoyo="${h}" type="number"
			min="3" max="6" value="${par}" title="Par hoyo ${h}"></th>`;
	}).join("");

	const td_par_back = Array.from({length: 9}, (_, i) => {
		const h = i + 10;
		const par = par_actual[h] || 4;
		if (bloqueada) return `<th>${par}</th>`;
		return `<th><input class="par-input" data-hoyo="${h}" type="number"
			min="3" max="6" value="${par}" title="Par hoyo ${h}"></th>`;
	}).join("");

	const par_out = Array.from({length: 9}, (_, i) => par_actual[i + 1] || 4).reduce((a, b) => a + b, 0);
	const par_in  = Array.from({length: 9}, (_, i) => par_actual[i + 10] || 4).reduce((a, b) => a + b, 0);

	// Filas de jugadores
	const filas_jugadores = participantes.map((p) => {
		const datos_j = scores_ronda[p.jugador] || {};

		const celdas_front = Array.from({length: 9}, (_, i) => {
			const h   = i + 1;
			const sc  = datos_j[h] || {};
			const val = sc.golpes || "";
			const tiene_pen = sc.penalizaciones && sc.penalizaciones.length > 0;
			const readonly  = bloqueada ? "readonly" : "";
			const cls_pen   = tiene_pen ? " tiene-pen" : "";
			return `<td>
				<input class="golpe-input${cls_pen}"
					data-jugador="${p.jugador}"
					data-hoyo="${h}"
					type="number" min="1" max="20"
					value="${val}" ${readonly}
					title="Hoyo ${h} - Par ${par_actual[h] || 4}${tiene_pen ? " (con penalización)" : ""}">
				${!bloqueada ? `<span class="pen-trigger" data-jugador="${p.jugador}" data-hoyo="${h}"
					style="cursor:pointer;font-size:8px;color:${tiene_pen ? "#e67e22" : "#ccc"};
						display:block;line-height:1" title="Penalizaciones">PEN</span>` : ""}
				</td>`;
		}).join("");

		const sub_out_val = Array.from({length: 9}, (_, i) => {
			const h = i + 1;
			return parseInt(datos_j[h]?.golpes || 0);
		}).reduce((a, b) => a + b, 0);

		const celdas_back = Array.from({length: 9}, (_, i) => {
			const h   = i + 10;
			const sc  = datos_j[h] || {};
			const val = sc.golpes || "";
			const tiene_pen = sc.penalizaciones && sc.penalizaciones.length > 0;
			const readonly  = bloqueada ? "readonly" : "";
			const cls_pen   = tiene_pen ? " tiene-pen" : "";
			return `<td>
				<input class="golpe-input${cls_pen}"
					data-jugador="${p.jugador}"
					data-hoyo="${h}"
					type="number" min="1" max="20"
					value="${val}" ${readonly}
					title="Hoyo ${h} - Par ${par_actual[h] || 4}${tiene_pen ? " (con penalización)" : ""}">
				${!bloqueada ? `<span class="pen-trigger" data-jugador="${p.jugador}" data-hoyo="${h}"
					style="cursor:pointer;font-size:8px;color:${tiene_pen ? "#e67e22" : "#ccc"};
						display:block;line-height:1" title="Penalizaciones">PEN</span>` : ""}
				</td>`;
		}).join("");

		const sub_in_val = Array.from({length: 9}, (_, i) => {
			const h = i + 10;
			return parseInt(datos_j[h]?.golpes || 0);
		}).reduce((a, b) => a + b, 0);

		const total_val = sub_out_val + sub_in_val;

		const boton_guardar = bloqueada ? "" : `
			<button class="btn btn-xs btn-primary btn-guardar-fila"
				data-jugador="${p.jugador}"
				data-ronda="${ronda.name}">
				${__("Guardar")}
			</button>`;

		return `<tr data-jugador="${p.jugador}">
			<td class="td-jugador" title="${p.nombre} | ${p.categoria} | Hcp ${p.handicap_inscripcion}">
				<strong>${p.nombre || p.jugador}</strong>
				<small style="display:block;color:#aaa;font-size:9px">${p.categoria}</small>
				</td>
			${celdas_front}
			<td class="td-subtotal" data-sub="out" data-jugador="${p.jugador}">
				${sub_out_val || ""}
				</td>
			${celdas_back}
			<td class="td-subtotal" data-sub="in" data-jugador="${p.jugador}">
				${sub_in_val || ""}
				</td>
			<td class="td-subtotal" data-sub="tot" data-jugador="${p.jugador}">
				${total_val || ""}
				</td>
			<td>${boton_guardar}</td>
			</tr>`;
	}).join("");

	return `
		${aviso}
		<div style="overflow-x:auto">
			<table class="golf-grid">
				<thead>
					<tr>
						<th class="col-jugador">${__("Jugador")}</th>
						${Array.from({length: 9}, (_, i) => `<th class="col-hoyo">${i+1}</th>`).join("")}
						<th class="col-sub">OUT</th>
						${Array.from({length: 9}, (_, i) => `<th class="col-hoyo">${i+10}</th>`).join("")}
						<th class="col-sub">IN</th>
						<th class="col-sub">TOT</th>
						<th class="col-accion"></th>
					</tr>
					<tr class="fila-par">
						<th style="text-align:left;padding-left:6px;font-size:10px">PAR</th>
						${td_par_front}
						<th class="col-sub">${par_out}</th>
						${td_par_back}
						<th class="col-sub">${par_in}</th>
						<th class="col-sub">${par_out + par_in}</th>
						<th></th>
					</tr>
				</thead>
				<tbody>
					${filas_jugadores}
				</tbody>
			</table>
		</div>
		<p style="font-size:10px;color:#aaa;margin-top:6px">
			Haz clic en "PEN" debajo de un golpe para agregar penalizaciones a ese hoyo.
			Guarda fila por fila con el botón Guardar.
		</p>`;
}

function _vincular_eventos_grilla(d, frm, rondas, participantes, scores, par_actual) {
	const $wrap = d.$wrapper;
	const pens_local = {};

	// Inicializar penalizaciones locales desde datos existentes
	for (const ronda of rondas) {
		const scores_ronda = scores[ronda.name] || {};
		for (const jug of participantes) {
			for (let h = 1; h <= 18; h++) {
				const sc = (scores_ronda[jug.jugador] || {})[h];
				if (sc && sc.penalizaciones && sc.penalizaciones.length) {
					const key = `${ronda.name}||${jug.jugador}||${h}`;
					pens_local[key] = sc.penalizaciones.map(p => Object.assign({}, p));
				}
			}
		}
	}

	// Recalcular subtotales al modificar golpes
	$wrap.on("input", "input.golpe-input", function() {
		const $tr = $(this).closest("tr");
		const jugador = $tr.data("jugador");
		let out = 0, inn = 0;
		$tr.find("input.golpe-input").each(function() {
			const hoyo = parseInt($(this).data("hoyo"));
			const val  = parseInt($(this).val()) || 0;
			if (hoyo <= 9) out += val;
			else inn += val;
		});
		$tr.find(`td[data-sub="out"][data-jugador="${jugador}"]`).text(out || "");
		$tr.find(`td[data-sub="in"][data-jugador="${jugador}"]`).text(inn || "");
		$tr.find(`td[data-sub="tot"][data-jugador="${jugador}"]`).text((out + inn) || "");
	});

	// Cambio del par por hoyo
	$wrap.on("change", "input.par-input", function() {
		const hoyo = parseInt($(this).data("hoyo"));
		const val  = parseInt($(this).val()) || 4;
		par_actual[hoyo] = val;

		$wrap.find(`input.golpe-input[data-hoyo="${hoyo}"]`).each(function() {
			const tiene_pen = $(this).hasClass("tiene-pen");
			$(this).attr("title", `Hoyo ${hoyo} - Par ${val}${tiene_pen ? " (con penalización)" : ""}`);
		});

		const panel = $(this).closest(".tab-pane");
		let par_out = 0, par_in = 0;
		for (let h = 1; h <= 18; h++) {
			const v = par_actual[h] || 4;
			if (h <= 9) par_out += v; else par_in += v;
		}
		panel.find("tr.fila-par th.col-sub").eq(0).text(par_out);
		panel.find("tr.fila-par th.col-sub").eq(1).text(par_in);
		panel.find("tr.fila-par th.col-sub").eq(2).text(par_out + par_in);
	});

	// Abrir diálogo de penalizaciones
	$wrap.on("click", "span.pen-trigger", function() {
		const jugador = $(this).data("jugador");
		const hoyo    = parseInt($(this).data("hoyo"));
		const panel   = $(this).closest(".tab-pane");
		const ronda   = panel.data("ronda");
		const key     = `${ronda}||${jugador}||${hoyo}`;

		_abrir_dialogo_penalizaciones(key, pens_local, (nuevas_pens) => {
			pens_local[key] = nuevas_pens;

			const $input   = panel.find(`input.golpe-input[data-jugador="${jugador}"][data-hoyo="${hoyo}"]`);
			const $trigger = panel.find(`span.pen-trigger[data-jugador="${jugador}"][data-hoyo="${hoyo}"]`);
			const tiene    = nuevas_pens.length > 0;

			$input.toggleClass("tiene-pen", tiene);
			$trigger.css("color", tiene ? "#e67e22" : "#ccc");

			const par = par_actual[hoyo] || 4;
			$input.attr("title", `Hoyo ${hoyo} - Par ${par}${tiene ? " (con penalización)" : ""}`);
		});
	});

	// Guardar fila completa
	$wrap.on("click", "button.btn-guardar-fila", function() {
		const $btn    = $(this);
		const jugador = $btn.data("jugador");
		const ronda   = $btn.data("ronda");
		const panel   = $btn.closest(".tab-pane");
		const $fila   = panel.find(`tr[data-jugador="${jugador}"]`);

		const hoyos = [];
		$fila.find("input.golpe-input").each(function() {
			const hoyo  = parseInt($(this).data("hoyo"));
			const golpes = $(this).val();
			const par    = par_actual[hoyo] || 4;
			const key    = `${ronda}||${jugador}||${hoyo}`;
			const pens   = pens_local[key] || [];

			hoyos.push({
				numero_de_hoyo: hoyo,
				golpes_brutos:  golpes ? parseInt(golpes) : null,
				par_del_hoyo:   par,
				penalizaciones: pens,
			});
		});

		$btn.prop("disabled", true).text(__("Guardando..."));

		frappe.call({
			method: "golf_manager.golf_manager.api.guardar_fila_puntuaciones",
			args: {
				ronda:      ronda,
				jugador:    jugador,
				hoyos_json: JSON.stringify(hoyos),
			},
			callback(r) {
				$btn.prop("disabled", false).text(__("Guardar"));
				if (r.message) {
					const guardados = r.message.guardados.length;
					frappe.show_alert({
						message:   __("{0} hoyos guardados", [guardados]),
						indicator: "green",
					});
					$fila.addClass("fila-guardada");
					setTimeout(() => $fila.removeClass("fila-guardada"), 2000);
				}
			},
			error() {
				$btn.prop("disabled", false).text(__("Guardar"));
			},
		});
	});
}

function _abrir_dialogo_penalizaciones(key, pens_local, callback) {
	const pens_actuales = (pens_local[key] || []).map(p => Object.assign({}, p));

	function _filas_html(pens) {
		if (!pens.length) {
			return `<tr id="pen-empty-row"><td colspan="3" style="text-align:center;color:#aaa;font-style:italic">
				Sin penalizaciones. Usa el botón para agregar.
				</td></tr>`;
		}
		return pens.map((p, i) => `
			<tr data-idx="${i}">
				<td>
					<select class="form-control form-control-sm pen-motivo" data-idx="${i}">
						${MOTIVOS_PENALIZACION.map(m =>
							`<option value="${m}" ${m === p.motivo ? "selected" : ""}>${m}</option>`
						).join("")}
					</select>
				</td>
				<td>
					<input class="form-control form-control-sm pen-golpes" data-idx="${i}"
						type="number" min="1" max="10" value="${p.golpes_adicionales || 1}"
						style="width:60px">
				</td>
				<td>
					<button class="btn btn-xs btn-danger btn-quitar-pen" data-idx="${i}">x</button>
				</td>
			</tr>`).join("");
	}

	const d_pen = new frappe.ui.Dialog({
		title:  __("Penalizaciones en este hoyo"),
		fields: [{ fieldtype: "HTML", fieldname: "pen_html" }],
		primary_action_label: __("Aceptar"),
		primary_action() {
			const nuevas = [];
			d_pen.$wrapper.find("tr[data-idx]").each(function() {
				const idx    = $(this).data("idx");
				const motivo = $(this).find(".pen-motivo").val();
				const golpes = parseInt($(this).find(".pen-golpes").val()) || 1;
				nuevas.push({ motivo, golpes_adicionales: golpes });
			});
			callback(nuevas);
			d_pen.hide();
		},
		secondary_action_label: __("Cancelar"),
		secondary_action() { d_pen.hide(); },
	});

	d_pen.show();

	const tabla_html = `
		<table class="table table-condensed" style="font-size:12px">
			<thead>
				<tr>
					<th>Motivo</th>
					<th style="width:80px">Golpes extra</th>
					<th style="width:40px"></th>
				</tr>
			</thead>
			<tbody id="pen-tbody">
				${_filas_html(pens_actuales)}
			</tbody>
		</table>
		<button class="btn btn-xs btn-default" id="btn-agregar-pen">+ Agregar penalización</button>`;

	d_pen.fields_dict.pen_html.$wrapper.html(tabla_html);

	d_pen.$wrapper.on("click", "#btn-agregar-pen", function() {
		pens_actuales.push({ motivo: "Bola perdida", golpes_adicionales: 1 });
		d_pen.$wrapper.find("#pen-tbody").html(_filas_html(pens_actuales));
	});

	d_pen.$wrapper.on("click", ".btn-quitar-pen", function() {
		const idx = parseInt($(this).data("idx"));
		pens_actuales.splice(idx, 1);
		d_pen.$wrapper.find("#pen-tbody").html(_filas_html(pens_actuales));
	});

	d_pen.$wrapper.on("change", ".pen-motivo, .pen-golpes", function() {
		const idx = parseInt($(this).data("idx"));
		if ($(this).hasClass("pen-motivo")) {
			pens_actuales[idx].motivo = $(this).val();
		} else {
			pens_actuales[idx].golpes_adicionales = parseInt($(this).val()) || 1;
		}
	});
}

function _descargar_pdf(frm, formato, extra_params) {
	const params = new URLSearchParams({
		docname: frm.doc.name,
		formato,
		cmd: "golf_manager.golf_manager.pdf_export.descargar_pdf_torneo",
		...(extra_params || {}),
	});
	window.open(
		`/api/method/golf_manager.golf_manager.pdf_export.descargar_pdf_torneo?${params}`,
		"_blank"
	);
}

function _dialogo_filtro_brackets(frm) {
	frappe.db.get_list("participacion en torneo", {
		filters: { torneo: frm.doc.name },
		fields:  ["categoria"],
		limit:   100,
	}).then((parts) => {
		const cats = [...new Set(parts.map((p) => p.categoria).filter(Boolean))].sort();
		const cat_opts = [{ value: "", label: __("Todas las categorias") }].concat(
			cats.map((c) => ({ value: c, label: c }))
		);

		const d = new frappe.ui.Dialog({
			title: __("Descargar PDF - Brackets de rondas"),
			fields: [
				{
					fieldname: "categoria",
					fieldtype: "Select",
					label:     __("Filtrar por categoria"),
					options:   cat_opts.map((o) => o.label).join("\n"),
					default:   cat_opts[0].label,
				},
			],
			primary_action_label: __("Descargar PDF"),
			primary_action(values) {
				d.hide();
				const cat_sel = cat_opts.find((o) => o.label === values.categoria);
				const extra = {};
				if (cat_sel && cat_sel.value) extra.categoria = cat_sel.value;
				_descargar_pdf(frm, "brackets_torneo", extra);
			},
		});
		d.show();
	});
}

function _dialogo_filtro_puntuaciones(frm) {
	Promise.all([
		frappe.db.get_list("ronda", {
			filters:  { torneo: frm.doc.name },
			fields:   ["name", "numero_de_ronda", "fecha", "estado"],
			order_by: "numero_de_ronda asc",
		}),
		frappe.db.get_list("participacion en torneo", {
			filters: { torneo: frm.doc.name },
			fields:  ["categoria"],
			limit:   100,
		}),
	]).then(([rondas, parts]) => {
		const ronda_opts = [{ value: "", label: __("Todas las rondas") }].concat(
			rondas.map((r) => ({
				value: String(r.numero_de_ronda),
				label: `${__("Ronda")} ${r.numero_de_ronda} - ${frappe.datetime.str_to_user(r.fecha)} (${r.estado})`,
			}))
		);

		const cats = [...new Set(parts.map((p) => p.categoria).filter(Boolean))].sort();
		const cat_opts = [{ value: "", label: __("Todas las categorias") }].concat(
			cats.map((c) => ({ value: c, label: c }))
		);

		const d = new frappe.ui.Dialog({
			title: __("Descargar PDF - Puntuaciones por jugador"),
			fields: [
				{
					fieldname: "ronda_idx",
					fieldtype: "Select",
					label:     __("Filtrar por ronda"),
					options:   ronda_opts.map((o) => o.label).join("\n"),
					default:   ronda_opts[0].label,
				},
				{
					fieldname: "categoria",
					fieldtype: "Select",
					label:     __("Filtrar por categoria"),
					options:   cat_opts.map((o) => o.label).join("\n"),
					default:   cat_opts[0].label,
				},
			],
			primary_action_label: __("Descargar PDF"),
			primary_action(values) {
				d.hide();
				const ronda_sel = ronda_opts.find((o) => o.label === values.ronda_idx);
				const cat_sel   = cat_opts.find((o) => o.label === values.categoria);
				const extra = {};
				if (ronda_sel && ronda_sel.value) extra.ronda_idx = ronda_sel.value;
				if (cat_sel   && cat_sel.value)   extra.categoria  = cat_sel.value;
				_descargar_pdf(frm, "puntuaciones_torneo", extra);
			},
		});
		d.show();
	});
}

function _mostrar_ranking_dialog(data) {
	if (!data || !data.ranking) {
		frappe.msgprint(__("No hay datos de ranking disponibles."));
		return;
	}

	const info   = data.torneo_info || {};
	const titulo = info.nombre || __("Ranking");

	const BADGE = {
		1: `<span style="background:#ffc107;color:#212529;padding:1px 8px;border-radius:3px;font-weight:700">1</span>`,
		2: `<span style="background:#6c757d;color:#fff;padding:1px 8px;border-radius:3px;font-weight:700">2</span>`,
		3: `<span style="background:#cd7f32;color:#fff;padding:1px 8px;border-radius:3px;font-weight:700">3</span>`,
	};

	const filas = data.ranking.length
		? data.ranking.map((p) => `
			<tr>
				<td style="text-align:center">
					${BADGE[p.posicion_en_ranking] || (p.posicion_en_ranking ?? "")}
				</td>
				<td><strong>${p.nombre_jugador || p.jugador}</strong></td>
				<td>${p.categoria || ""}</td>
				<td style="text-align:center">${p.handicap_inscripcion ?? ""}</td>
				<td style="text-align:center;font-weight:600">${p.puntuacion_total_acumulada ?? ""}</td>
			</tr>`).join("")
		: `<tr><td colspan="5" class="text-center text-muted">${__("Sin resultados registrados.")}</td></tr>`;

	frappe.msgprint({
		title:   `${titulo} - ${info.estado || ""}`,
		message: `
			<div style="font-size:12px;color:#6c757d;margin-bottom:8px">
				${__("Campo")}: <strong>${info.campo || ""}</strong>
				&nbsp;
				${__("Formato")}: <strong>${info.formato || ""}</strong>
			</div>
			<table class="table table-bordered table-condensed" style="margin:0;font-size:13px">
				<thead style="background:#1a5276;color:#fff">
					<tr>
						<th style="text-align:center;width:50px">#</th>
						<th>${__("Jugador")}</th>
						<th>${__("Categoria")}</th>
						<th style="text-align:center">${__("Hcp")}</th>
						<th style="text-align:center">${__("Puntuacion")}</th>
					</tr>
				</thead>
				<tbody>${filas}</tbody>
			</table>`,
		wide: true,
	});
}
