# revenue-portal/mainrevenueportal.py

from flask import Flask, render_template, request, jsonify
from pathlib import Path
from calendar import monthrange
from datetime import datetime, timezone
from typing import List, Dict, Any
from zoneinfo import ZoneInfo  # Python 3.9+
import requests
from requests.adapters import HTTPAdapter, Retry
import os
import logging

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),  # templates/index-revenueportal.html
    static_folder=str(BASE_DIR / "static")        # /static/* assets
)
logging.basicConfig(level=logging.INFO)

# ============================================================
# Constants / configuration
# ============================================================

METRIC_TOTAL_ROOMS = "Total rooms"
METRIC_AVAILABLE_ROOMS = "Available rooms"
METRIC_HOTEL = "Hotel"
METRIC_STUDENT = "Student"
METRIC_EXTENDED_STAY = "Extended stay"

ROOM_TYPE_ID_TO_NAME: Dict[str, str] = {
    "01d9c47b-2dea-4e3f-b87e-ae94011b33bb": "Standard Double",
    "185695d6-ab95-4416-bd3d-b30c00f0a37f": "Standard Twin",
    "a42186d8-9b8d-4d00-ab1b-ae94011b33bb": "Deluxe Double",
    "14bd53d1-3058-49cc-84b9-ae94011b33bb": "Family Room",
}
ROOM_TYPE_NAME_TO_ID: Dict[str, str] = {name.lower(): rid for rid, name in ROOM_TYPE_ID_TO_NAME.items()}
CANONICAL_ROOM_TYPE_IDS = list(ROOM_TYPE_ID_TO_NAME.keys())

HOTEL_SERVICE_ID = os.getenv("MEWS_SERVICE_ID") or "5291ecd7-c75f-4281-bca0-ae94011b2f3a"
STUDENT_SERVICE_ID = os.getenv("MEWS_STUDENT_SERVICE_ID") or "d4f7e1b3-5e2e-4f6a-8f3a-ae94011b33bb"
EXTENDED_STAY_SERVICE_ID = os.getenv("MEWS_EXTENDED_SERVICE_ID") or "7c3f4e2a-1d2b-4c5d-9f6a-ae94011b33cc"

_RESOURCE_CATEGORY_CACHE: Dict[str, Dict[str, str]] = {}

# ============================================================
# Helpers
# ============================================================

def ensure_metric_length(arr: Any, n: int) -> List[int]:
    """
    Normaliseer een metric-array naar lengte n → ints ≥ 0.
    """
    if not isinstance(arr, list):
        return [0] * n
    padded = (arr + [0] * n)[:n]
    normalized: List[int] = []
    for value in padded:
        if isinstance(value, (int, float)):
            normalized.append(max(0, int(value)))
        else:
            normalized.append(0)
    return normalized


def calculate_availability_arrays(metrics: Dict[str, Any], n: int) -> Dict[str, List[int]]:
    """
    Bepaal arrays voor totalen, true availability en hotel availability.
    """
    active = ensure_metric_length(metrics.get("ActiveResources"), n)
    out_of_order = ensure_metric_length(metrics.get("OutOfOrderBlocks"), n)
    confirmed = ensure_metric_length(metrics.get("ConfirmedReservations"), n)
    optional = ensure_metric_length(metrics.get("OptionalReservations"), n)
    allocated = ensure_metric_length(metrics.get("AllocatedBlockAvailability"), n)
    public_adjustment = ensure_metric_length(metrics.get("PublicAvailabilityAdjustment"), n)

    true_availability: List[int] = []
    for u, o, c, opt, alloc in zip(active, out_of_order, confirmed, optional, allocated):
        val = (u or 0) - (o or 0) - (c or 0) - (opt or 0) - (alloc or 0)
        true_availability.append(max(0, val))

    hotel_availability = [
        max(0, t - adj) for t, adj in zip(true_availability, public_adjustment)
    ]

    return {
        "active": active,
        "true": true_availability,
        "hotel": hotel_availability,
    }


def fetch_resource_category_mapping(
    session: requests.Session,
    mews_base: str,
    client_token: str,
    access_token: str,
    client_name: str,
    service_id: str,
) -> Dict[str, str]:
    """
    Haal de resource category namen op en map service-specifieke ids naar canonieke ids.
    """
    if not service_id:
        return {}
    if service_id in _RESOURCE_CATEGORY_CACHE:
        return _RESOURCE_CATEGORY_CACHE[service_id]

    payload = {
        "ClientToken": client_token,
        "AccessToken": access_token,
        "Client": client_name,
        "ServiceIds": [service_id],
        "Limitation": {"Count": 200},
    }
    url = mews_base + "resourceCategories/getAll"

    try:
        resp = session.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        body = resp.json()
    except requests.RequestException as exc:
        app.logger.warning("Failed to load resource categories for service %s: %s", service_id, exc)
        return {}

    mapping: Dict[str, str] = {}
    for item in body.get("ResourceCategories", []):
        name = (item.get("Name") or "").strip().lower()
        canonical_id = ROOM_TYPE_NAME_TO_ID.get(name)
        if canonical_id:
            mapping[item.get("Id")] = canonical_id

    _RESOURCE_CATEGORY_CACHE[service_id] = mapping
    return mapping


def map_service_availability_to_canonical(
    upstream: Dict[str, Any],
    time_axis: List[str],
    room_type_map: Dict[str, str],
) -> Dict[str, List[int]]:
    """
    Gebruik service-specifieke roomtype mapping om hotel availability arrays te koppelen aan canonieke roomtype ids.
    """
    n = len(time_axis)
    result: Dict[str, List[int]] = {}
    if not upstream:
        return result

    for rc in upstream.get("ResourceCategoryAvailabilities", []):
        canonical_id = room_type_map.get(rc.get("ResourceCategoryId"))
        if not canonical_id:
            continue
        arrays = calculate_availability_arrays(rc.get("Metrics", {}) or {}, n)
        result[canonical_id] = arrays["hotel"]
    return result


def apply_metric_to_portal(
    portal: Dict[str, Any],
    metric_name: str,
    values_by_room: Dict[str, List[int]],
    n: int,
) -> None:
    """
    Injecteer een metric-array (bijv. Student) per canoniek roomtype in het portal payload.
    """
    if not values_by_room:
        return

    rca_index: Dict[str, Dict[str, Any]] = {}
    for rc in portal.get("ResourceCategoryAvailabilities", []):
        rca_index[rc.get("ResourceCategoryId")] = rc

    for room_id, values in values_by_room.items():
        if room_id not in rca_index:
            rca_index[room_id] = {
                "ResourceCategoryId": room_id,
                "Metrics": {
                    METRIC_TOTAL_ROOMS: [0] * n,
                    METRIC_AVAILABLE_ROOMS: [0] * n,
                    METRIC_HOTEL: [0] * n,
                    METRIC_STUDENT: [0] * n,
                    METRIC_EXTENDED_STAY: [0] * n,
                },
            }
            portal.setdefault("ResourceCategoryAvailabilities", []).append(rca_index[room_id])

        metrics = rca_index[room_id].setdefault("Metrics", {})
        metrics[metric_name] = values


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
            "ActiveResources": [...],
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
            "Total rooms":    [...],   # ActiveResources
            "Available rooms":[...],   # trueAvailability
            "Hotel":          [...],
            "Student":        [...],
            "Extended stay":  [...]
          }
        },
        ...
      ]
    }
    """
    n = len(time_axis)

    rca: List[Dict[str, Any]] = []

    for rc in upstream.get("ResourceCategoryAvailabilities", []):
        rcid = rc.get("ResourceCategoryId") or "unknown"
        m = rc.get("Metrics", {}) or {}

        arrays = calculate_availability_arrays(m, n)

        metrics_portal: Dict[str, List[int]] = {
            METRIC_TOTAL_ROOMS: arrays["active"],
            METRIC_AVAILABLE_ROOMS: arrays["true"],
            METRIC_HOTEL: arrays["hotel"],
            METRIC_STUDENT: [0] * n,
            METRIC_EXTENDED_STAY: [0] * n,
        }

        rca.append({
            "ResourceCategoryId": rcid,
            "Metrics": metrics_portal,
        })

    return {
        "TimeUnitStartsUtc": time_axis,
        "ResourceCategoryAvailabilities": rca,
    }

def fallback_empty_payload(time_axis: List[str]) -> Dict[str, Any]:
    """
    Fallback payload zodat de UI iets kan tonen als upstream-config mist.
    Roomtype-ids komen overeen met de mapping in de frontend.
    """
    n = len(time_axis)
    zeros = [0] * n
    return {
        "TimeUnitStartsUtc": time_axis,
        "ResourceCategoryAvailabilities": [
            {
                "ResourceCategoryId": rid,
                "Metrics": {
                    METRIC_TOTAL_ROOMS: zeros,
                    METRIC_AVAILABLE_ROOMS: zeros,
                    METRIC_HOTEL: zeros,
                    METRIC_STUDENT: zeros,
                    METRIC_EXTENDED_STAY: zeros,
                },
            }
            for rid in CANONICAL_ROOM_TYPE_IDS
        ],
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

# Helpers om platform URL te normaliseren
def _normalize_mews_base(raw: str) -> str:
    """
    Zorg dat we een basis als https://{platform} terugkrijgen.
    Als raw al /api/connector bevat, strip dat deel om dubbele paden te voorkomen.
    """
    if not raw:
        return ""
    lower = raw.lower()
    if "/api/connector" in lower:
        raw = raw[: lower.index("/api/connector")]
    return raw.rstrip("/")


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
         ActiveResources
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
    app.logger.info("Availability request received year=%s month=%s first=%s last=%s", year, month, first_utc, last_utc)

    # 3) Mews upstream configuratie
    mews_base = "https://api.mews-demo.com/api/connector/v1/"
    client_token = os.getenv("DEMO_CLIENTTOKEN")
    access_token = os.getenv("DAVID_ACCESSTOKEN")
    client_name = "RevenuePortal 1.0.0"
    hotel_service_id = HOTEL_SERVICE_ID
    student_service_id = STUDENT_SERVICE_ID
    extended_service_id = EXTENDED_STAY_SERVICE_ID

    missing = [
        name for name, value in [
            ("DEMO_CLIENTTOKEN", client_token),
            ("DAVID_ACCESSTOKEN", access_token),
            ("MEWS_SERVICE_ID", hotel_service_id),
        ]
        if not value
    ]
    if missing:
        # Geen upstream configuratie → geef lege payload zodat de UI blijft werken
        app.logger.warning("Upstream config missing: %s", missing)
        return jsonify(fallback_empty_payload(time_axis)), 200

    # Endpoint: getAvailability (ver 2024-01-22)
    url = mews_base + "services/getAvailability/2024-01-22"

    # Metrics die we nodig hebben voor trueAvailability + wat extra's die handig kunnen zijn
    metrics = [
        "ActiveResources",
        "OutOfOrderBlocks",
        "ConfirmedReservations",
        "OptionalReservations",
        "AllocatedBlockAvailability",
        "BlockAvailability",
        "PublicAvailabilityAdjustment",
        "OtherServiceReservationCount",
        "ActiveResources",
    ]

    payload_template: Dict[str, Any] = {
        "ClientToken": client_token,
        "AccessToken": access_token,
        "Client": client_name,
        "FirstTimeUnitStartUtc": first_utc,
        "LastTimeUnitStartUtc": last_utc,
        "Metrics": metrics,
    }

    session = http_session_with_retries()

    def call_service(service_id: str, label: str) -> Dict[str, Any]:
        payload = dict(payload_template)
        payload["ServiceId"] = service_id
        app.logger.info("POST %s (%s ServiceId=%s, metrics=%d)", url, label, service_id, len(metrics))
        resp = session.post(url, json=payload, timeout=15)
        app.logger.info("%s upstream status %s", label, resp.status_code)
        resp.raise_for_status()
        return resp.json()

    try:
        upstream_json = call_service(hotel_service_id, "Hotel")
    except requests.RequestException as e:
        app.logger.warning("Upstream call failed, serving fallback payload: %s", e)
        return jsonify(fallback_empty_payload(time_axis)), 200

    # 4) Transformeer naar portal-schema
    #    TIP in transform_upstream_to_portal:
    #    - loop over ResourceCategoryAvailabilities
    #    - per dag i:
    #         trueAvailability[i] =
    #             ActiveResources[i]
    #           - OutOfOrderBlocks[i]
    #           - ConfirmedReservations[i]
    #           - OptionalReservations[i]
    #           - AllocatedBlockAvailability[i]
    try:
        portal = transform_upstream_to_portal(upstream_json, time_axis)
    except Exception as e:
        return jsonify({"error": "Transform failed", "detail": str(e)}), 500

    # 5) Verrijk met Student- en Extended stay-data
    additional_services = [
        (student_service_id, "Student", METRIC_STUDENT),
        (extended_service_id, "Extended stay", METRIC_EXTENDED_STAY),
    ]
    for service_id, label, metric_name in additional_services:
        if not service_id:
            continue
        try:
            extra_upstream = call_service(service_id, label)
        except requests.RequestException as exc:
            app.logger.warning("Skipping %s service due to upstream error: %s", label, exc)
            continue

        mapping = fetch_resource_category_mapping(
            session=session,
            mews_base=mews_base,
            client_token=client_token,
            access_token=access_token,
            client_name=client_name,
            service_id=service_id,
        )
        if not mapping:
            app.logger.warning("No room type mapping available for %s service, skipping metric merge", label)
            continue

        metric_values = map_service_availability_to_canonical(extra_upstream, time_axis, mapping)
        if not metric_values:
            app.logger.info("No matching categories returned for %s service", label)
            continue

        apply_metric_to_portal(portal, metric_name, metric_values, len(time_axis))

    # Log wat er uit komt zonder gevoelige data
    ids = [rc.get("ResourceCategoryId") for rc in portal.get("ResourceCategoryAvailabilities", [])]
    app.logger.info("Returning %d categories: %s", len(ids), ids)

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
            "Extended stay": [...]
          }
        }
      ]
    }

    (B) Volledige workingData per roomtype:
    {
      "Classic": { "Total rooms":[...], "Available rooms":[...], "Hotel":[...], ... },
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
