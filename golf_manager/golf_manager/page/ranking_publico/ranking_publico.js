frappe.pages["ranking-publico"].on_page_load = function (wrapper) {
	// Redirigir a la página web pública de ranking
	// Se abre en pestaña nueva para no sacar al usuario del desk
	window.open("/ranking", "_blank");

	// Volver a la página anterior en el desk para no dejar una página en blanco
	frappe.set_route(frappe.router.back_history || "");
};
