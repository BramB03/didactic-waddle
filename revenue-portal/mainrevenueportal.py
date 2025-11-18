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
    Pas DIT aan je daadwerkelijke upstream response aan.
    Het portal-schema dat de UI verwacht:

    {
      "TimeUnitStartsUtc": [...],
      "ResourceCategoryAvailabilities": [
        {
          "ResourceCategoryId": "uuid/naam",
          "Metrics": {
            "Totaal kamers": [...],
            "Vrije kamers":  [...],
            "Hotel":         [...],
            "Student":       [...],
            "Lang verblijf": [...]
          }
        },
        ...
      ]
    }

    ── VOORBEELD adapter ──
    Verwacht upstream als:
    {
      "items": [
        { "resourceCategoryId":"...", "total":[...], "free":[...], "hotel":[...], "student":[...], "longStay":[...] },
        ...
      ]
    }
    """
    n = len(time_axis)

    def ensure(arr) -> List[int]:
        if not isinstance(arr, list):
            return [0] * n
        # trim/pad naar n en maak ints ≥ 0
        arr = (arr + [0] * n)[:n]
        return [int(x) if isinstance(x, (int, float)) else 0 for x in arr]

    rca = []
    for it in upstream.get("items", []):
        rcid = it.get("resourceCategoryId") or it.get("ResourceCategoryId") or "unknown"
        metrics = {
            "Totaal kamers": ensure(it.get("total")),
            "Vrije kamers":  ensure(it.get("free")),
            "Hotel":         ensure(it.get("hotel")),
            "Student":       ensure(it.get("student")),
            "Lang verblijf": ensure(it.get("longStay") or it.get("long_stay")),
        }
        rca.append({"ResourceCategoryId": rcid, "Metrics": metrics})

    return {"TimeUnitStartsUtc": time_axis, "ResourceCategoryAvailabilities": rca}

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
    - Roep jouw UPSTREAM (Mews/DB/eigen service) aan met passende parameters
    - Map de upstream response naar het portal-schema met transform_upstream_to_portal()
    """
    # 1) Params
    try:
        year = int(request.args.get("year"))
        month = int(request.args.get("month"))
        assert 0 <= month <= 11
    except Exception:
        return jsonify({"error": "Provide valid 'year' (int) and 'month' in 0..11"}), 400

    # 2) Tijdas op basis van Europe/Amsterdam → UTC
    time_axis = iso_midnights_utc_for_month_eu_amsterdam(year, month)
    print("Timeaxis: ", time_axis)
    # 3) MARK: UPSTREAM CALL (VUL IN)
    #    - Vul hieronder je eigen URL, headers en payload in.
    #    - Vaak wil je ook startUtc en endUtc meegeven.
    #    - Voorbeeld laat een POST zien; gebruik GET als jouw API dat verwacht.
    upstream_base = os.getenv("UPSTREAM_BASE")           # bv. https://api.mijnservice.nl
    upstream_path = os.getenv("UPSTREAM_PATH", "/v1/availability")
    if not upstream_base:
        # Geen upstream geconfigureerd → geef duidelijke melding
        return jsonify({
            "error": "Upstream not configured",
            "hint":  "Set environment variable UPSTREAM_BASE and implement payload mapping."
        }), 502

    start_utc = time_axis[0]                  # eerste lokale 00:00 (in UTC)
    # 'end' meegeven als eerste lokale 00:00 van de VOLGENDE maand in UTC:
    # → pak laatste dag van de maand en tel 1 dag op
    n_days = monthrange(year, month + 1)[1]
    tz_nl = ZoneInfo("Europe/Amsterdam")
    local_first_next = datetime(year, month + 1, n_days, 0, 0, 0, tzinfo=tz_nl).replace(day=n_days) \
        .astimezone(timezone.utc)
    # local_first_next is 00:00 op laatste dag; we willen 00:00 van DAG+1 (volgende dag):
    local_first_next = (datetime(year, month + 1, n_days, 0, 0, 0, tzinfo=tz_nl)
                        .astimezone(timezone.utc))
    # maak einde = volgende lokale 00:00:
    # eenvoudige manier: neem laatste ISO in time_axis en voeg 24h toe in UTC; maar DST maakt het tricky.
    # veiliger: bouw 00:00 lokale tijd van (jaar, maand, n_days) + 1 dag:
    from datetime import timedelta
    local_day_after = datetime(year, month + 1, n_days, 0, 0, 0, tzinfo=tz_nl) + timedelta(days=1)
    end_utc = local_day_after.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    # Stel een payload samen die jouw upstream verwacht (PAS AAN):
    upstream_payload: Dict[str, Any] = {
        "startUtc": start_utc,
        "endUtc": end_utc,
        # Voeg hier jouw identifiers/filters toe:
        # "enterpriseId": "...",
        # "serviceId": "...",
        # "resourceCategoryIds": ["...", "..."],
        # "limitation": {"count": 100},
    }

    try:
        session = http_session_with_retries()
        url = upstream_base.rstrip("/") + upstream_path
        # KIES GET of POST afhankelijk van je API:
        # resp = session.get(url, params=upstream_payload, timeout=15)
        resp = session.post(url, json=upstream_payload, timeout=15)
        resp.raise_for_status()
        upstream_json = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": "Upstream call failed", "detail": str(e)}), 502

    # 4) Transformeer naar portal-schema
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