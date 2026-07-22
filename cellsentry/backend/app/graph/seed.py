"""Week-2 seed supply graph: two products (NMC e-scooter, LFP e-rickshaw).

Companies, countries and raw-material country shares are grounded in real
~2023-24 USGS / industry figures so demo numbers hold up. BOM relationships,
dependency fractions and buffer (inventory) days are illustrative but chosen so
the headline path (graphite -> anode -> cell -> pack -> product) sums to ~21
inventory-days of lead time.

Edge direction = supply flow: source FEEDS target, ending at a product.
Edge attributes:
  - dependency : fraction of the downstream node's need met via this edge (risk weight)
  - buffer_days: inventory/stock days on this link (used for lead-time-to-impact)
"""

SEED_NODES: list[dict] = [
    # --- countries (geopolitical anchors for suppliers) ---
    {"id": "country_china", "label": "China", "type": "country"},
    {"id": "country_skorea", "label": "South Korea", "type": "country"},
    {"id": "country_belgium", "label": "Belgium", "type": "country"},
    {"id": "country_drc", "label": "DR Congo", "type": "country"},
    {"id": "country_indonesia", "label": "Indonesia", "type": "country"},
    {"id": "country_australia", "label": "Australia", "type": "country"},

    # --- raw materials (carry global country shares -> concentration) ---
    {"id": "rm_cobalt", "label": "Cobalt", "type": "raw_material",
     "country_shares": {"DR Congo": 0.74, "Indonesia": 0.06, "Russia": 0.04, "Australia": 0.03, "Others": 0.13}},
    {"id": "rm_lithium", "label": "Lithium", "type": "raw_material",
     "country_shares": {"Australia": 0.52, "Chile": 0.25, "China": 0.13, "Argentina": 0.06, "Others": 0.04}},
    {"id": "rm_nickel", "label": "Nickel", "type": "raw_material",
     "country_shares": {"Indonesia": 0.50, "Philippines": 0.11, "Russia": 0.07, "Others": 0.32}},
    {"id": "rm_graphite", "label": "Graphite", "type": "raw_material",
     "country_shares": {"China": 0.77, "Mozambique": 0.06, "Madagascar": 0.05, "Others": 0.12}},
    {"id": "rm_iron", "label": "Iron / Phosphate", "type": "raw_material",
     "country_shares": {"Australia": 0.35, "Brazil": 0.20, "China": 0.15, "India": 0.10, "Others": 0.20}},

    # --- suppliers ---
    {"id": "sup_glencore", "label": "Glencore", "type": "supplier", "tier": 3, "country": "DR Congo"},
    {"id": "sup_ganfeng", "label": "Ganfeng Lithium", "type": "supplier", "tier": 3, "country": "China"},
    {"id": "sup_vale", "label": "Vale", "type": "supplier", "tier": 3, "country": "Indonesia"},
    {"id": "sup_btr", "label": "BTR New Material", "type": "supplier", "tier": 2, "country": "China"},
    {"id": "sup_ironco", "label": "Fortescue (iron ore)", "type": "supplier", "tier": 3, "country": "Australia"},
    {"id": "sup_umicore", "label": "Umicore (NMC cathode)", "type": "supplier", "tier": 2, "country": "Belgium"},
    {"id": "sup_dynanonic", "label": "Dynanonic (LFP cathode)", "type": "supplier", "tier": 2, "country": "China"},
    {"id": "sup_catl", "label": "CATL", "type": "supplier", "tier": 1, "country": "China"},
    {"id": "sup_lges", "label": "LG Energy Solution", "type": "supplier", "tier": 1, "country": "South Korea"},
    {"id": "sup_byd", "label": "BYD (LFP cell)", "type": "supplier", "tier": 1, "country": "China"},

    # --- materials / components ---
    {"id": "mat_cathode_nmc811", "label": "Cathode (NMC811)", "type": "material"},
    {"id": "mat_cathode_lfp", "label": "Cathode (LFP)", "type": "material"},
    {"id": "mat_anode", "label": "Anode (Graphite)", "type": "material"},

    # --- cells / packs / products ---
    {"id": "cell_nmc811", "label": "NMC811 Cell", "type": "cell"},
    {"id": "cell_lfp", "label": "LFP Cell", "type": "cell"},
    {"id": "pack_35", "label": "3.5 kWh Pack (NMC)", "type": "pack"},
    {"id": "pack_lfp", "label": "4.0 kWh Pack (LFP)", "type": "pack"},
    {"id": "prod_s1", "label": "E-Scooter S1", "type": "product"},
    {"id": "prod_l1", "label": "E-Rickshaw L1", "type": "product"},
]


def _e(source: str, target: str, type_: str = "supplies", dependency: float = 1.0, buffer_days: int = 0) -> dict:
    return {"source": source, "target": target, "type": type_, "dependency": dependency, "buffer_days": buffer_days}


SEED_EDGES: list[dict] = [
    # country -> supplier (located_in)
    _e("country_drc", "sup_glencore", "located_in"),
    _e("country_china", "sup_ganfeng", "located_in"),
    _e("country_indonesia", "sup_vale", "located_in"),
    _e("country_china", "sup_btr", "located_in"),
    _e("country_australia", "sup_ironco", "located_in"),
    _e("country_belgium", "sup_umicore", "located_in"),
    _e("country_china", "sup_dynanonic", "located_in"),
    _e("country_china", "sup_catl", "located_in"),
    _e("country_skorea", "sup_lges", "located_in"),
    _e("country_china", "sup_byd", "located_in"),

    # supplier -> raw material (mines / refines)
    _e("sup_glencore", "rm_cobalt"),
    _e("sup_ganfeng", "rm_lithium"),
    _e("sup_vale", "rm_nickel"),
    _e("sup_btr", "rm_graphite"),
    _e("sup_ironco", "rm_iron"),

    # raw material -> component (with material fraction + inventory buffer)
    _e("rm_cobalt", "mat_cathode_nmc811", dependency=0.33, buffer_days=10),
    _e("rm_lithium", "mat_cathode_nmc811", dependency=0.34, buffer_days=8),
    _e("rm_nickel", "mat_cathode_nmc811", dependency=0.33, buffer_days=8),
    _e("rm_lithium", "mat_cathode_lfp", dependency=0.5, buffer_days=8),
    _e("rm_iron", "mat_cathode_lfp", dependency=0.5, buffer_days=20),
    _e("rm_graphite", "mat_anode", dependency=1.0, buffer_days=12),

    # supplier (maker) -> component
    _e("sup_umicore", "mat_cathode_nmc811", "makes", dependency=1.0, buffer_days=0),
    _e("sup_dynanonic", "mat_cathode_lfp", "makes", dependency=1.0, buffer_days=0),

    # component -> cell  (note: anode feeds BOTH cells -> shared graphite exposure)
    _e("mat_cathode_nmc811", "cell_nmc811", dependency=1.0, buffer_days=4),
    _e("mat_anode", "cell_nmc811", dependency=1.0, buffer_days=4),
    _e("mat_cathode_lfp", "cell_lfp", dependency=1.0, buffer_days=4),
    _e("mat_anode", "cell_lfp", dependency=1.0, buffer_days=4),

    # supplier (cell maker) -> cell
    _e("sup_catl", "cell_nmc811", "makes", dependency=0.5, buffer_days=0),
    _e("sup_lges", "cell_nmc811", "makes", dependency=0.5, buffer_days=0),
    _e("sup_byd", "cell_lfp", "makes", dependency=1.0, buffer_days=0),

    # cell -> pack -> product
    _e("cell_nmc811", "pack_35", dependency=1.0, buffer_days=3),
    _e("cell_lfp", "pack_lfp", dependency=1.0, buffer_days=3),
    _e("pack_35", "prod_s1", dependency=1.0, buffer_days=2),
    _e("pack_lfp", "prod_l1", dependency=1.0, buffer_days=2),
]
