// Copyright (c) 2026, avato and contributors
// For license information, please see license.txt

frappe.ui.form.on("puntuacion por hoyo", {

	setup(frm) {
		frm._torneo_name    = null;
		frm._realtime_bound = false;   // evita registrar el listener más de una vez

		frm.set_query("ronda", () => ({
			filters: { estado: "En curso" },
		}));

		frm.set_query("jugador", () => {
			if (!frm.doc.ronda) return {};
			return {
				query: "golf_manager.golf_manager.api.get_jugadores_de_ronda",
				filters: { ronda: frm.doc.ronda },
			};
		});
	},

	refresh(frm) {
		// Resolver el torneo de la ronda y luego renderizar
		frm.trigger("_resolver_torneo").then(() => {
			frm.trigger("_setup_scorecard_rapido");
		});

		// Recalcular resumen
		frm.trigger("_mostrar_resumen_golpes");

		// Registrar el listener de realtime UNA SOLA VEZ por documento
		if (frm.doc.ronda && !frm._realtime_bound) {
			frm._realtime_bound = true;
			frappe.realtime.on(`golf_score_${frm.doc.ronda}`, (data) => {
				if (
					data.jugador !== frm.doc.jugador ||
					data.hoyo    !== frm.doc.numero_de_hoyo
				) {
					frm.page.set_indicator(__("Actualizando..."), "orange");
					setTimeout(() => frm.trigger("_setup_scorecard_rapido"), 2000);
				}
			});
		}
	},

	//  Resolver torneo

	_resolver_torneo(frm) {
		if (!frm.doc.ronda) {
			frm._torneo_name = null;
			return Promise.resolve();
		}
		if (frm._torneo_name) {
			return Promise.resolve();
		}
		return frappe.db.get_value("ronda", frm.doc.ronda, "torneo").then((r) => {
			frm._torneo_name = r.message && r.message.torneo ? r.message.torneo : null;
		});
	},

	//  Scorecard rápido

	_setup_scorecard_rapido(frm) {
		if (frm.is_new() || !frm.doc.ronda || !frm.doc.jugador) return;
		if (!frm._torneo_name) return;

		frappe.call({
			method: "golf_manager.golf_manager.api.get_scorecard",
			args: {
				torneo:  frm._torneo_name,
				jugador: frm.doc.jugador,
				ronda:   frm.doc.ronda,
			},
			callback(r) {
				if (!r.message) return;
				const ronda_data = r.message.scorecard && r.message.scorecard[0];
				if (!ronda_data) return;
				frm.trigger("_renderizar_grilla_hoyos", ronda_data);
			},
		});
	},

	_renderizar_grilla_hoyos(frm, ronda_data) {
		const hoyos       = ronda_data.hoyos || [];
		const hoyo_actual = frm.doc.numero_de_hoyo;

		const celdas = Array.from({ length: 18 }, (_, i) => {
			const n      = i + 1;
			const h      = hoyos.find((x) => x.numero_de_hoyo === n);
			const golpes = h ? (h.golpes_totales ?? h.golpes_brutos ?? "-") : "—";
			const par    = h ? h.par_del_hoyo : "—";
			const activo = n === hoyo_actual
				? "style='background:var(--yellow-highlight)'" : "";
			const pen    = h && h.flag_penalizacion ? " ⚑" : "";

			return `
				<td ${activo} title="Par ${par}"
					style="text-align:center;cursor:pointer;padding:4px 6px"
					data-hoyo="${n}">
					<div style="font-size:10px;color:#888">${n}</div>
					<div style="font-weight:500">${golpes}${pen}</div>
				</td>`;
		});

		const html = `
			<div class="golf-scorecard-mini" style="margin:8px 0 16px">
				<div style="font-size:11px;color:#888;margin-bottom:4px">
					${__("Tarjeta de puntuación — haga clic en un hoyo para ir a él")}
				</div>
				<table class="table table-bordered"
					style="table-layout:fixed;font-size:12px;margin:0">
					<tbody>
						<tr>${celdas.slice(0, 9).join("")}</tr>
						<tr>${celdas.slice(9).join("")}</tr>
					</tbody>
				</table>
				<div style="margin-top:6px;font-size:12px;color:#555">
					${__("Total golpes")}: <strong>${ronda_data.subtotal_golpes || 0}</strong>
					&nbsp;|&nbsp;
					${__("Stableford")}: <strong>${ronda_data.subtotal_stableford || 0}</strong>
				</div>
			</div>`;

		// Limpiar scorecard previo antes de insertar el nuevo
		const $wrapper = $(frm.fields_dict["ronda"].wrapper).closest(".form-section");
		$wrapper.find(".golf-scorecard-mini").remove();
		$wrapper.prepend(html);

		$wrapper.find("[data-hoyo]").on("click", function () {
			frm.set_value("numero_de_hoyo", parseInt($(this).data("hoyo")));
		});
	},

	//  Resumen visual

	_mostrar_resumen_golpes(frm) {
		// Limpiar intro previo siempre, para evitar acumulación
		frm.set_intro("");

		if (!frm.doc.golpes_brutos || !frm.doc.par_del_hoyo) return;

		const penalizaciones = (frm.doc.penalizaciones || []).reduce(
			(acc, r) => acc + (r.golpes_adicionales || 0), 0
		);
		const total      = frm.doc.golpes_brutos + penalizaciones;
		const diferencia = total - frm.doc.par_del_hoyo;

		let etiqueta;
		if      (diferencia <= -2) etiqueta = "Eagle o mejor";
		else if (diferencia === -1) etiqueta = "Birdie";
		else if (diferencia ===  0) etiqueta = "Par";
		else if (diferencia ===  1) etiqueta = "Bogey";
		else if (diferencia ===  2) etiqueta = "Doble bogey";
		else                        etiqueta = `+${diferencia}`;

		const stableford = Math.max(0, frm.doc.par_del_hoyo + 2 - total);
		const color      = diferencia > 0 ? "orange" : diferencia < 0 ? "blue" : "green";

		frm.set_intro(
			`${__("Total")}: <strong>${total} golpes</strong> &nbsp;·&nbsp; `
			+ `${etiqueta} &nbsp;·&nbsp; `
			+ `${__("Stableford")}: <strong>${stableford} pts</strong>`,
			color
		);
	},

	//  Recalcular al cambiar campos

	golpes_brutos(frm) { frm.trigger("_mostrar_resumen_golpes"); },
	par_del_hoyo(frm)  { frm.trigger("_mostrar_resumen_golpes"); },

	penalizaciones_add(frm)    { frm.trigger("_mostrar_resumen_golpes"); },
	penalizaciones_remove(frm) { frm.trigger("_mostrar_resumen_golpes"); },

	// Al cambiar ronda, resetear caché
	ronda(frm) {
		frm._torneo_name    = null;
		frm._realtime_bound = false;
		frm.trigger("_resolver_torneo");
	},

	after_save(frm) {
		frappe.realtime.publish(`golf_score_${frm.doc.ronda}`, {
			jugador: frm.doc.jugador,
			hoyo:    frm.doc.numero_de_hoyo,
			golpes:  frm.doc.golpes_brutos,
		});
		frm.trigger("_setup_scorecard_rapido");
	},
});

frappe.ui.form.on("penalizacion", {
	golpes_adicionales(frm) {
		frm.trigger("_mostrar_resumen_golpes");
	},
});
