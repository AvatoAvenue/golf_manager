{
  "charts": [],
  "content": "[{\"id\":\"section-torneos\",\"type\":\"header\",\"data\":{\"text\":\"Mis Torneos\",\"level\":4,\"col\":12}},{\"id\":\"sc-torneo\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Torneo de Golf\",\"col\":4}},{\"id\":\"sc-participacion\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Mis Participaciones\",\"col\":4}},{\"id\":\"section-scores\",\"type\":\"header\",\"data\":{\"text\":\"Mis Puntuaciones\",\"level\":4,\"col\":12}},{\"id\":\"sc-score\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Mis Puntuaciones\",\"col\":4}},{\"id\":\"section-ranking\",\"type\":\"header\",\"data\":{\"text\":\"Ranking\",\"level\":4,\"col\":12}},{\"id\":\"sc-ranking\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Ranking Publico\",\"col\":4}}]",
  "creation": "2026-04-01 00:00:00.000000",
  "custom_blocks": [],
  "docstatus": 0,
  "doctype": "Workspace",
  "for_user": "",
  "hide_custom": 0,
  "icon": "fa fa-flag",
  "idx": 0,
  "indicator_color": "green",
  "is_hidden": 0,
  "label": "Mi Golf",
  "links": [
    {
      "dependencies": "",
      "doctype": "Workspace Link",
      "hidden": 0,
      "is_query_report": 0,
      "label": "Torneos",
      "link_count": 0,
      "onboard": 0,
      "type": "Card Break"
    },
    {
      "dependencies": "",
      "doctype": "Workspace Link",
      "hidden": 0,
      "is_query_report": 0,
      "label": "Torneo de Golf",
      "link_count": 0,
      "link_to": "torneo de golf",
      "link_type": "DocType",
      "onboard": 1,
      "only_for": "",
      "type": "Link"
    },
    {
      "dependencies": "torneo de golf",
      "doctype": "Workspace Link",
      "hidden": 0,
      "is_query_report": 0,
      "label": "Mis Participaciones",
      "link_count": 0,
      "link_to": "participacion en torneo",
      "link_type": "DocType",
      "onboard": 1,
      "only_for": "",
      "type": "Link"
    },
    {
      "dependencies": "",
      "doctype": "Workspace Link",
      "hidden": 0,
      "is_query_report": 0,
      "label": "Mis Puntuaciones",
      "link_count": 0,
      "onboard": 0,
      "type": "Card Break"
    },
    {
      "dependencies": "",
      "doctype": "Workspace Link",
      "hidden": 0,
      "is_query_report": 0,
      "label": "Mis Puntuaciones",
      "link_count": 0,
      "link_to": "puntuacion por hoyo",
      "link_type": "DocType",
      "onboard": 1,
      "only_for": "",
      "type": "Link"
    }
  ],
  "modified": "2026-04-01 00:00:00.000000",
  "modified_by": "Administrator",
  "module": "Golf Manager",
  "name": "Mi Golf",
  "number_cards": [],
  "owner": "Administrator",
  "parent_page": "",
  "public": 1,
  "quick_lists": [
    {
      "doctype": "Workspace Quick List",
      "document_type": "torneo de golf",
      "filters": "[{\"field\":\"estado\",\"condition\":\"in\",\"value\":[\"Activo\",\"Finalizado\"]}]",
      "label": "Torneos activos"
    }
  ],
  "roles": [
    {
      "doctype": "Workspace Role",
      "role": "jugador"
    }
  ],
  "sequence_id": 40.0,
  "shortcuts": [
    {
      "color": "Green",
      "doctype": "Workspace Shortcut",
      "format": "{} activos",
      "label": "Torneo de Golf",
      "link_to": "torneo de golf",
      "stats_filter": "{\"estado\":\"Activo\"}",
      "type": "DocType"
    },
    {
      "color": "Blue",
      "doctype": "Workspace Shortcut",
      "label": "Mis Participaciones",
      "link_to": "participacion en torneo",
      "type": "DocType"
    },
    {
      "color": "Purple",
      "doctype": "Workspace Shortcut",
      "label": "Mis Puntuaciones",
      "link_to": "puntuacion por hoyo",
      "type": "DocType"
    },
    {
      "color": "Green",
      "doctype": "Workspace Shortcut",
      "label": "Ranking Publico",
      "link_to": "ranking-publico",
      "type": "Page"
    }
  ],
  "title": "Mi Golf"
}
