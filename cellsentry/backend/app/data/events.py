"""Curated corpus of real 2023-25 battery-material supply-chain events.

Each event carries the raw headline/body/source AND a ground-truth `extracted`
mapping. The pipeline uses `extracted` deterministically when no API key is set
(demo-safe), and the Claude extraction agent reproduces it from `body` when a
key is present (and serves as the labelled set for the evaluation harness).

severity is 0-100 (event-boost magnitude). direction is informational.
Entity names match graph node labels so the pipeline can map them to node ids.
"""

EVENTS: list[dict] = [
    {
        "id": "graphite-china-export-2023",
        "date": "2023-12-01",
        "headline": "China imposes export-permit requirements on graphite",
        "body": (
            "China's commerce ministry began requiring export permits for several "
            "graphite products from 1 December 2023, citing national security. Graphite "
            "is the dominant anode material in lithium-ion batteries and China supplies "
            "the large majority of the world's battery-grade output."
        ),
        "source": {"name": "Reuters", "url": "https://www.reuters.com"},
        "extracted": {
            "materials": ["Graphite"], "countries": ["China"], "suppliers": [],
            "event_type": "export_control", "severity": 80, "direction": "supply_down",
            "rationale": "Permit regime on the single most concentrated anode input.",
        },
    },
    {
        "id": "drc-cobalt-export-suspension-2025",
        "date": "2025-02-22",
        "headline": "DR Congo suspends cobalt exports for four months",
        "body": (
            "The Democratic Republic of Congo, source of roughly three-quarters of global "
            "cobalt, suspended cobalt exports for four months to arrest a price collapse. "
            "The move squeezes refiners and cell makers dependent on Congolese hydroxide."
        ),
        "source": {"name": "Reuters", "url": "https://www.reuters.com"},
        "extracted": {
            "materials": ["Cobalt"], "countries": ["DR Congo"], "suppliers": ["Glencore"],
            "event_type": "export_ban", "severity": 85, "direction": "supply_down",
            "rationale": "Hard export halt from the dominant cobalt source.",
        },
    },
    {
        "id": "indonesia-nickel-policy-2023",
        "date": "2023-06-01",
        "headline": "Indonesia tightens nickel ore export and downstream rules",
        "body": (
            "Indonesia, now half of global nickel mine supply, continued enforcing ore "
            "export restrictions and domestic-processing requirements, reshaping nickel "
            "availability for cathode makers outside its smelter ecosystem."
        ),
        "source": {"name": "Argus Media", "url": "https://www.argusmedia.com"},
        "extracted": {
            "materials": ["Nickel"], "countries": ["Indonesia"], "suppliers": [],
            "event_type": "export_control", "severity": 55, "direction": "supply_down",
            "rationale": "Resource-nationalism on the leading nickel source.",
        },
    },
    {
        "id": "eu-battery-regulation-2023",
        "date": "2023-08-17",
        "headline": "EU Battery Regulation enters into force",
        "body": (
            "The EU Battery Regulation took effect, phasing in supply-chain due-diligence "
            "obligations, carbon-footprint declarations and a digital battery passport for "
            "lithium, cobalt, nickel and natural graphite."
        ),
        "source": {"name": "European Commission", "url": "https://commission.europa.eu"},
        "extracted": {
            "materials": ["Lithium", "Cobalt", "Nickel", "Graphite"], "countries": [], "suppliers": [],
            "event_type": "regulation", "severity": 40, "direction": "compliance",
            "rationale": "Due-diligence + passport obligations across all four key inputs.",
        },
    },
    {
        "id": "chile-lithium-nationalisation-2023",
        "date": "2023-04-20",
        "headline": "Chile announces national lithium strategy with state control",
        "body": (
            "Chile, the second-largest lithium producer, announced a national lithium "
            "strategy giving the state a controlling role in future projects, raising "
            "uncertainty for offtake and new supply."
        ),
        "source": {"name": "Financial Times", "url": "https://www.ft.com"},
        "extracted": {
            "materials": ["Lithium"], "countries": ["Chile"], "suppliers": [],
            "event_type": "resource_nationalism", "severity": 50, "direction": "supply_down",
            "rationale": "State control over a major lithium source.",
        },
    },
    {
        "id": "us-tariff-graphite-2024",
        "date": "2024-05-14",
        "headline": "US sets tariffs on Chinese graphite and anode material",
        "body": (
            "The United States announced increased tariffs on Chinese natural graphite and "
            "anode active material, raising landed costs for cell makers sourcing Chinese "
            "anode and accelerating diversification pressure."
        ),
        "source": {"name": "Reuters", "url": "https://www.reuters.com"},
        "extracted": {
            "materials": ["Graphite"], "countries": ["China"], "suppliers": [],
            "event_type": "tariff", "severity": 55, "direction": "price_up",
            "rationale": "Tariff cost shock on concentrated anode supply.",
        },
    },
    {
        "id": "red-sea-shipping-2024",
        "date": "2024-01-15",
        "headline": "Red Sea attacks force shipping diversions",
        "body": (
            "Attacks on Red Sea shipping forced carriers to divert around southern Africa, "
            "adding one to two weeks of transit and freight cost to Asia-Europe battery-"
            "material flows."
        ),
        "source": {"name": "Lloyd's List", "url": "https://www.lloydslist.com"},
        "extracted": {
            "materials": [], "countries": [], "suppliers": [],
            "event_type": "logistics", "severity": 45, "direction": "supply_down",
            "rationale": "General logistics drag; not specific to one material.",
        },
    },
    {
        "id": "cobalt-artisanal-esg-2024",
        "date": "2024-03-10",
        "headline": "Renewed scrutiny of artisanal cobalt mining in DR Congo",
        "body": (
            "Reports renewed attention on hazardous and child labour in artisanal cobalt "
            "mining in DR Congo, sharpening ESG and due-diligence exposure for buyers of "
            "Congolese cobalt."
        ),
        "source": {"name": "Amnesty International", "url": "https://www.amnesty.org"},
        "extracted": {
            "materials": ["Cobalt"], "countries": ["DR Congo"], "suppliers": ["Glencore"],
            "event_type": "esg", "severity": 45, "direction": "compliance",
            "rationale": "ESG / human-rights exposure on Congolese cobalt.",
        },
    },
    {
        "id": "china-graphite-tightening-2025",
        "date": "2025-01-20",
        "headline": "China expands graphite export-licensing list",
        "body": (
            "China added further battery-grade graphite items to its export-licensing "
            "regime, lengthening approval times and tightening availability of high-purity "
            "anode feedstock."
        ),
        "source": {"name": "Benchmark Mineral Intelligence", "url": "https://www.benchmarkminerals.com"},
        "extracted": {
            "materials": ["Graphite"], "countries": ["China"], "suppliers": [],
            "event_type": "export_control", "severity": 75, "direction": "supply_down",
            "rationale": "Further licensing on already-concentrated graphite.",
        },
    },
    {
        "id": "drc-security-2024",
        "date": "2024-11-05",
        "headline": "Conflict in eastern DR Congo threatens mining logistics",
        "body": (
            "Escalating conflict in eastern DR Congo threatened transport corridors used to "
            "move cobalt and copper concentrate, raising delivery risk for Congolese output."
        ),
        "source": {"name": "Bloomberg", "url": "https://www.bloomberg.com"},
        "extracted": {
            "materials": ["Cobalt"], "countries": ["DR Congo"], "suppliers": [],
            "event_type": "conflict", "severity": 60, "direction": "supply_down",
            "rationale": "Security risk to Congolese cobalt logistics.",
        },
    },
    {
        "id": "eu-crma-2024",
        "date": "2024-05-23",
        "headline": "EU Critical Raw Materials Act sets diversification benchmarks",
        "body": (
            "The EU Critical Raw Materials Act set 2030 benchmarks capping reliance on any "
            "single third country for strategic raw materials, pressing manufacturers to "
            "diversify lithium, cobalt, nickel and graphite sourcing."
        ),
        "source": {"name": "European Commission", "url": "https://commission.europa.eu"},
        "extracted": {
            "materials": ["Lithium", "Cobalt", "Nickel", "Graphite"], "countries": [], "suppliers": [],
            "event_type": "regulation", "severity": 35, "direction": "compliance",
            "rationale": "Single-country reliance caps across key inputs.",
        },
    },
    {
        "id": "lithium-price-crash-2024",
        "date": "2024-02-01",
        "headline": "Lithium prices fall sharply on oversupply",
        "body": (
            "Lithium carbonate prices fell roughly 80% from their 2022 peak on oversupply "
            "and softer EV demand, easing input-cost pressure for cell makers."
        ),
        "source": {"name": "Fastmarkets", "url": "https://www.fastmarkets.com"},
        "extracted": {
            "materials": ["Lithium"], "countries": [], "suppliers": [],
            "event_type": "price_move", "severity": 20, "direction": "price_down",
            "rationale": "Lower cost, mild de-risking — not a supply threat.",
        },
    },
    {
        "id": "indonesia-nickel-oversupply-2024",
        "date": "2024-07-01",
        "headline": "Indonesian nickel oversupply pressures prices",
        "body": (
            "Rapid Indonesian smelter expansion produced a nickel surplus, depressing prices "
            "and squeezing higher-cost producers elsewhere."
        ),
        "source": {"name": "Reuters", "url": "https://www.reuters.com"},
        "extracted": {
            "materials": ["Nickel"], "countries": ["Indonesia"], "suppliers": [],
            "event_type": "price_move", "severity": 20, "direction": "price_down",
            "rationale": "Surplus lowers price risk; concentration risk persists.",
        },
    },
    {
        "id": "australia-lithium-expansion-2024",
        "date": "2024-09-01",
        "headline": "Australia expands lithium output",
        "body": (
            "New and expanded Australian hard-rock lithium operations added supply from a "
            "low-geopolitical-risk source, improving diversification options for buyers."
        ),
        "source": {"name": "Mining.com", "url": "https://www.mining.com"},
        "extracted": {
            "materials": ["Lithium"], "countries": ["Australia"], "suppliers": [],
            "event_type": "supply_expansion", "severity": 15, "direction": "supply_up",
            "rationale": "More low-risk supply; slightly de-risking.",
        },
    },
]

# The scripted demo anchor.
DEMO_EVENT_ID = "graphite-china-export-2023"

EVENTS_BY_ID = {e["id"]: e for e in EVENTS}
