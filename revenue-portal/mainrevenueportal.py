# revenue-portal/mainrevenueportal.py
"""
STRUCTUUR & WAT WAAR KOMT
─────────────────────────
- templates/index-revenueportal.html  → jouw UI (de pagina die fetches doet)
- static/                             → optionele JS/CSS assets
- DIT BESTAND (Flask app)             → serveert UI + twee API endpoints

ROUTES
- GET  /                      → render templates/index-revenueportal.html
- GET  /availability          → HAAL DATA OP voor (year, month) [0=jan..11=dec]
- PUT  /availability/overrides → ONTVANG WIJZIGINGEN uit de UI (echo/doorsturen)

HOE DE TIJDAS WERKT (Europe/Amsterdam → UTC)
- Voor elke dag in de gekozen maand maken we 00:00:00 op Europe/Amsterdam.
- Die tijdstippen converteren we naar UTC, en leveren ze als ISO-string met "Z".
- Zo sluiten tijdas en kolommen exact aan op lokale kalenderdagen in NL.

WAT JE MOET INVULLEN
- In get_availability(): zoek naar  # MARK: UPSTREAM CALL (VUL IN)
  Zet daar je request naar Mews/DB/eigen service (requests.get/post).
  Daarna: map de upstream response → portal-schema met transform_upstream_to_portal().

LET OP
- Er is GEEN mock-data meer; als je upstream-blok niet is ingevuld, retourneren we 502.
"""

from flask import Flask, render_template, request, jsonify
from pathlib import Path
from calendar import monthrange
from datetime import datetime, timezone
from typing import List, Dict, Any
from zoneinfo import ZoneInfo  # Python 3.9+
import requests
from requests.adapters import HTTPAdapter, Retry
import os

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),  # templates/index-revenueportal.html
    static_folder=str(BASE_DIR / "static")        # /static/* assets
)

# ============================================================
# Helpers
# ============================================================

def iso_midnights_utc_for_month_eu_amsterdam(year: int, month_index: int) -> List[str]:
    """
    Geef voor elke dag in de maand het UTC-tijdstip terug dat overeenkomt met
    00:00:00 lokale tijd (Europe/Amsterdam) op die dag.
    Voorbeeld: 2025-02-01 00:00:00 Europe/Amsterdam → 2025-01-31T23:00:00Z (winter/zomer afhankelijk).
    """
    tz_nl = ZoneInfo("Europe/Amsterdam")
    n_days = monthrange(year, month_index + 1)[1]
    out: List[str] = []
    for d in range(1, n_days + 1):
        local_midnight = datetime(year, month_index + 1, d, 0, 0, 0, tzinfo=tz_nl)
        as_utc = local_midnight.astimezone(timezone.utc)
        out.append(as_utc.isoformat().replace("+00:00", "Z"))
    return out

def http_session_with_retries() -> requests.Session:
    """
    Maak een requests Session met retries/timeouts. Pas headers aan op jouw upstream.
    """
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.4, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    # Voeg hier upstream-auth toe indien nodig (bijv. Mews tokens):
    # s.headers.update({"ClientToken": "...", "AccessToken": "...", "Content-Type": "application/json"})
    return s

def transform_upstream_to_portal(upstream: Dict[str, Any], time_axis: List[str]) -> Dict[str, Any]:
    """
    Adapter voor Mews services/getAvailability/2024-01-22 → portal-schema.

    Verwacht upstream ongeveer als:
    {
      "TimeUnitStartsUtc": [...],
      "ResourceCategoryAvailabilities": [
        {
          "ResourceCategoryId": "uuid",
          "Metrics": {
            "UsableResources": [...],
            "OutOfOrderBlocks": [...],
            "ConfirmedReservations": [...],
            "OptionalReservations": [...],
            "AllocatedBlockAvailability": [...],
            ...
          }
        },
        ...
      ]
    }

    Portal-output die de UI verwacht:
    {
      "TimeUnitStartsUtc": [...],
      "ResourceCategoryAvailabilities": [
        {
          "ResourceCategoryId": "uuid/naam",
          "Metrics": {
            "Totaal kamers": [...],   # UsableResources
            "Vrije kamers":  [...],   # trueAvailability
            "Hotel":         [...],   # voorlopig gelijk aan Vrije kamers of 0
            "Student":       [...],   # voorlopig 0
            "Lang verblijf": [...]    # voorlopig 0
          }
        },
        ...
      ]
    }
    """
    n = len(time_axis)

    def ensure_metric(arr: Any) -> List[int]:
        """Normaliseer een metric-array naar lengte n → ints ≥ 0."""
        if not isinstance(arr, list):
            return [0] * n
        # trim/pad naar n
        arr = (arr + [0] * n)[:n]
        out: List[int] = []
        for x in arr:
            if isinstance(x, (int, float)):
                out.append(max(0, int(x)))
            else:
                out.append(0)
        return out

    rca: List[Dict[str, Any]] = []

    for rc in upstream.get("ResourceCategoryAvailabilities", []):
        rcid = rc.get("ResourceCategoryId") or "unknown"
        m = rc.get("Metrics", {}) or {}

        usable = ensure_metric(m.get("UsableResources"))
        out_of_order = ensure_metric(m.get("OutOfOrderBlocks"))
        confirmed = ensure_metric(m.get("ConfirmedReservations"))
        optional = ensure_metric(m.get("OptionalReservations"))
        allocated = ensure_metric(m.get("AllocatedBlockAvailability"))

        # trueAvailability = UsableResources - OOO - Confirmed - Optional - AllocatedBlocks
        true_availability: List[int] = []
        for u, o, c, opt, alloc in zip(usable, out_of_order, confirmed, optional, allocated):
            val = (u or 0) - (o or 0) - (c or 0) - (opt or 0) - (alloc or 0)
            true_availability.append(max(0, val))

        # TODO: als je later segmentatie “Hotel / Student / Lang verblijf”
        # uit een andere bron haalt, kun je die hier mappen.
        metrics_portal: Dict[str, List[int]] = {
            "Totaal kamers": usable,
            "Vrije kamers":  true_availability,
            "Hotel":         true_availability,   # of [0] * n als je dit liever leeg laat
            "Student":       [0] * n,
            "Lang verblijf": [0] * n,
        }

        rca.append({
            "ResourceCategoryId": rcid,
            "Metrics": metrics_portal,
        })

    return {
        "TimeUnitStartsUtc": time_axis,
        "ResourceCategoryAvailabilities": rca,
    }
# ============================================================
# Page route (UI)
# ============================================================

@app.get("/")
def index():
    """
    Serve de UI. Zorg dat templates/index-revenueportal.html bestaat.
    De UI haalt bij init de huidige maand op via /availability?year=...&month=...
    """
    return render_template("index-revenueportal.html")

# ============================================================
# API: ophalen
# ============================================================

@app.get("/availability")
def get_availability():
    """
    Ophalen van data voor een specifieke maand.

    Query parameters:
      - year  (int)  bijv. 2025
      - month (int)  0=jan .. 11=dec

    Werking:
    - Bepaal de tijdas (lokale middernacht in NL → UTC) voor alle dagen in de maand
    - Roep Mews services/getAvailability/2024-01-22 aan (UPSTREAM)
    - Map de upstream response naar het portal-schema met transform_upstream_to_portal()
      → daar kun je trueAvailability berekenen als:
         UsableResources
       - OutOfOrderBlocks
       - ConfirmedReservations
       - OptionalReservations
       - AllocatedBlockAvailability
    """
    # 1) Params
    try:
        year = int(request.args.get("year"))
        month = int(request.args.get("month"))
        assert 0 <= month <= 11
    except Exception:
        return jsonify({"error": "Provide valid 'year' (int) and 'month' in 0..11"}), 400

    # 2) Tijdas op basis van Europe/Amsterdam → UTC
    #    Deze functie zou ISO-strings als "2025-02-01T23:00:00.000Z" moeten teruggeven
    time_axis = iso_midnights_utc_for_month_eu_amsterdam(year, month)
    if not time_axis:
        return jsonify({"error": "No dates generated for given month/year"}), 500

    first_utc = time_axis[0]
    last_utc = time_axis[-1]

    # 3) Mews upstream configuratie
    mews_base = "https://api.mews-demo.com/api/connector/v1/" # bv. https://mews-sandbox.mews-demo.com
    client_token = os.getenv("DAvid_CLIENTTOKEN")
    access_token = os.getenv("DAVID_ACCESSTOKEN")
    client_name = "client 1.0.0"
    service_id = "5291ecd7-c75f-4281-bca0-ae94011b2f3a"     # Accommodation service Id

    missing = [
        name for name, value in [
            ("MEWS_PLATFORM_ADDRESS", mews_base),
            ("MEWS_CLIENT_TOKEN", client_token),
            ("MEWS_ACCESS_TOKEN", access_token),
            ("MEWS_SERVICE_ID", service_id),
        ]
        if not value
    ]
    if missing:
        return jsonify({
            "error": "Upstream not configured",
            "missingEnv": missing,
            "hint": "Set the missing MEWS_* environment variables."
        }), 502

    # Endpoint: getAvailability (ver 2024-01-22)
    url = mews_base.rstrip("/") + "/api/connector/v1/services/getAvailability/2024-01-22"

    # Metrics die we nodig hebben voor trueAvailability + wat extra's die handig kunnen zijn
    metrics = [
        "UsableResources",
        "OutOfOrderBlocks",
        "ConfirmedReservations",
        "OptionalReservations",
        "AllocatedBlockAvailability",
        "BlockAvailability",
        "PublicAvailabilityAdjustment",
        "OtherServiceReservationCount",
        "ActiveResources",
    ]

    upstream_payload: Dict[str, Any] = {
        "ClientToken": client_token,
        "AccessToken": access_token,
        "Client": client_name,
        "ServiceId": service_id,
        "FirstTimeUnitStartUtc": first_utc,
        "LastTimeUnitStartUtc": last_utc,
        "Metrics": metrics,
    }

    try:
        session = http_session_with_retries()
        resp = session.post(url, json=upstream_payload, timeout=15)
        resp.raise_for_status()
        upstream_json = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": "Upstream call failed", "detail": str(e)}), 502

    # 4) Transformeer naar portal-schema
    #    TIP in transform_upstream_to_portal:
    #    - loop over ResourceCategoryAvailabilities
    #    - per dag i:
    #         trueAvailability[i] =
    #             UsableResources[i]
    #           - OutOfOrderBlocks[i]
    #           - ConfirmedReservations[i]
    #           - OptionalReservations[i]
    #           - AllocatedBlockAvailability[i]
    try:
        portal = transform_upstream_to_portal(upstream_json, time_axis)
    except Exception as e:
        return jsonify({"error": "Transform failed", "detail": str(e)}), 500

    return jsonify(portal)
# ============================================================
# API: wijzigingen ontvangen (echo of doorsturen)
# ============================================================

@app.put("/availability/overrides")
def save_overrides():
    """
    Ontvangt wijzigingen van de UI. Twee varianten:

    (A) Alleen veranderingen (diff):
    {
      "Year": 2025,
      "MonthIndex": 1,            # 0=jan
      "TimeUnitStartsUtc": [...], # optioneel
      "Edits": [
        {
          "ResourceCategoryId": "uuid/naam",
          "Metrics": {
            "Hotel": [...],
            "Student": [...],
            "Lang verblijf": [...]
          }
        }
      ]
    }

    (B) Volledige workingData per roomtype:
    {
      "Classic": { "Totaal kamers":[...], "Vrije kamers":[...], "Hotel":[...], ... },
      "Deluxe":  { ... },
      ...
    }

    NU: we hoeven niet echt op te slaan; we kunnen echo’en of doorsturen naar upstream.
    """
    payload = request.get_json(silent=True) or {}

    # Als je het door wilt sturen naar je upstream, doe dat hier (optioneel):
    #   session = http_session_with_retries()
    #   resp = session.put(UPSTREAM_URL, json=payload, timeout=15)
    #   return jsonify(resp.json()), resp.status_code

    # Anders: echo terug met een korte samenvatting
    if "Edits" in payload and isinstance(payload["Edits"], list):
        return jsonify({
            "status": "ok",
            "mode": "diff",
            "year": payload.get("Year"),
            "monthIndex": payload.get("MonthIndex"),
            "editCount": len(payload["Edits"]),
            "receivedSample": payload["Edits"][:1]
        })

    return jsonify({
        "status": "ok",
        "mode": "full_or_unknown",
        "received_keys": list(payload.keys())[:10]
    })

# ============================================================
# Run (lokaal)
# ============================================================

if __name__ == "__main__":
    # Start lokaal: http://127.0.0.1:5000
    app.run(host="0.0.0.0", port=5000, debug=True)