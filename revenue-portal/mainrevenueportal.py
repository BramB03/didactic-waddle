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

ROOM_TYPE_IDS_BY_SERVICE: Dict[str, Dict[str, str]] = {
    # Service A (hotel)
    "3080a911-df89-488e-a3ef-af02007dad8a": {
        "Standard Double": "088e115f-30b0-4ff8-aaba-af0300d3a187",
        "Standard Twin": "6efe10de-bbd1-4334-b0a4-b364007c9e4a",
        "Deluxe Double": "58a0d7e8-b535-4ea4-9532-af0300d3a187",
        "Family Room": "6885bdbb-a3fe-4b6f-88f6-af0300d3a187",
    },
    # Service B (student)
    "5a6ee418-468c-45f7-a3d2-b364007a7c0f": {
        "Standard Double": "8fad2a22-594a-4c39-afb3-b364007ae8aa",
        "Standard Twin": "35f02589-5c0b-4eb5-9446-b3a000ef8159",
        "Deluxe Double": "1bc0cab7-d54f-4c3f-86d3-b3a000efb7db",
        "Family Room": "d7392203-a33e-4331-a566-b3a000efd4d2",
    },
    # Service C (extended stay)
    "d9668056-a076-434e-8412-b364007a95da": {
        "Standard Double": "ed2d470a-d6e1-4b6d-83fb-b364007acaa0",
        "Standard Twin": "427b22df-1ea3-4772-821d-b3a000f1463c",
        "Deluxe Double": "7d28e32b-1c8c-4586-861d-b3a000f1fe00",
        "Family Room": "7a86e76e-7a5a-42eb-ad14-b3a000f28080",
    },
}

HOTEL_SERVICE_ID = "3080a911-df89-488e-a3ef-af02007dad8a"
STUDENT_SERVICE_ID = "5a6ee418-468c-45f7-a3d2-b364007a7c0f"
EXTENDED_STAY_SERVICE_ID = "d9668056-a076-434e-8412-b364007a95da"

_canonical_source = ROOM_TYPE_IDS_BY_SERVICE.get(HOTEL_SERVICE_ID) or next(iter(ROOM_TYPE_IDS_BY_SERVICE.values()))
ROOM_TYPE_NAME_TO_ID: Dict[str, str] = {name.lower(): rid for name, rid in _canonical_source.items()}
CANONICAL_ID_TO_NAME: Dict[str, str] = {rid: name for name, rid in _canonical_source.items()}
CANONICAL_ROOM_TYPE_IDS = list(CANONICAL_ID_TO_NAME.keys())

SERVICE_SPECIFIC_CATEGORY_MAP: Dict[str, Dict[str, str]] = {}
for service_id, name_to_rcid in ROOM_TYPE_IDS_BY_SERVICE.items():
    SERVICE_SPECIFIC_CATEGORY_MAP[service_id] = {}
    for name, rcid in name_to_rcid.items():
        canonical_id = ROOM_TYPE_NAME_TO_ID.get(name.lower())
        if canonical_id:
            SERVICE_SPECIFIC_CATEGORY_MAP[service_id][rcid] = canonical_id

_RESOURCE_CATEGORY_CACHE: Dict[str, Dict[str, str]] = {}

# ============================================================
# Helpers
# ============================================================

def ensure_metric_length(arr: Any, n: int) -> List[int]:
    if not isinstance(arr, list):
        return [0] * n
    padded = (arr + [0] * n)[:n]
    normalized: List[int] = []
    for value in padded:
        if isinstance(value, (int, float)):
            normalized.append(int(value))  
        else:
            normalized.append(0)
    return normalized


def calculate_availability_arrays(metrics: Dict[str, Any], n: int) -> Dict[str, List[int]]:
    # Core inputs
    active = ensure_metric_length(metrics.get("ActiveResources"), n)
    usable = ensure_metric_length(metrics.get("UsableResources"), n)
    occupied = ensure_metric_length(metrics.get("Occupied"), n)
    other_service = ensure_metric_length(metrics.get("OtherServiceReservationCount"), n)
    public_adjustment = ensure_metric_length(metrics.get("PublicAvailabilityAdjustment"), n)

    # If required
    out_of_order = ensure_metric_length(metrics.get("OutOfOrderBlocks"), n)
    confirmed = ensure_metric_length(metrics.get("ConfirmedReservations"), n)
    optional = ensure_metric_length(metrics.get("OptionalReservations"), n)
    allocated = ensure_metric_length(metrics.get("AllocatedBlockAvailability"), n)

    # Legacy "true" if needed it later
    true_availability: List[int] = []
    for u, o, c, opt, alloc in zip(active, out_of_order, confirmed, optional, allocated):
        val = (u or 0) - (o or 0) - (c or 0) - (opt or 0) - (alloc or 0)
        true_availability.append(val)

    # UsableResources − Occupied − OtherServiceReservationCount + PublicAvailabilityAdjustment
    net_availability: List[int] = []
    for u, occ, other, adj in zip(usable, occupied, other_service, public_adjustment):
        val = (u or 0) - (occ or 0) - (other or 0) + (adj or 0)
        net_availability.append(val)

    return {
        "active": active,          # Total rooms
        "usable": usable,          # Available rooms
        "net": net_availability,   # My formula for Hotel/Student/Extended
        "true": true_availability  # extra
    }

def fetch_resource_category_mapping(
    session: requests.Session,
    mews_base: str,
    client_token: str,
    access_token: str,
    client_name: str,
    service_id: str,
) -> Dict[str, str]:

    if not service_id:
        return {}
    if service_id in _RESOURCE_CATEGORY_CACHE:
        return _RESOURCE_CATEGORY_CACHE[service_id]

    payload = {
        "ClientToken": client_token,
        "AccessToken": access_token,
        "Client": client_name,
        "ServiceIds": [service_id],
        "Limitation": {"Count": 20},
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

    n = len(time_axis)
    result: Dict[str, List[int]] = {}
    if not upstream:
        return result

    for rc in upstream.get("ResourceCategoryAvailabilities", []):
        canonical_id = room_type_map.get(rc.get("ResourceCategoryId"))
        if not canonical_id:
            continue

        arrays = calculate_availability_arrays(rc.get("Metrics", {}) or {}, n)
        # Use the SAME net formula for Student / Extended
        result[canonical_id] = arrays["net"]

    return result

def apply_metric_to_portal(
    portal: Dict[str, Any],
    metric_name: str,
    values_by_room: Dict[str, List[int]],
    n: int,
) -> None:

    if not values_by_room:
        return

    rca_index: Dict[str, Dict[str, Any]] = {}
    for rc in portal.get("ResourceCategoryAvailabilities", []):
        rca_index[rc.get("ResourceCategoryId")] = rc

    for room_id, values in values_by_room.items():
        if room_id not in rca_index:
            rca_index[room_id] = {
                "ResourceCategoryId": room_id,
                "ResourceCategoryName": CANONICAL_ID_TO_NAME.get(room_id, room_id),
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

    tz_nl = ZoneInfo("Europe/Amsterdam")
    n_days = monthrange(year, month_index + 1)[1]
    out: List[str] = []
    for d in range(1, n_days + 1):
        local_midnight = datetime(year, month_index + 1, d, 0, 0, 0, tzinfo=tz_nl)
        as_utc = local_midnight.astimezone(timezone.utc)
        out.append(as_utc.isoformat().replace("+00:00", "Z"))
    return out

def http_session_with_retries() -> requests.Session:

    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.4, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s

def transform_upstream_to_portal(upstream: Dict[str, Any], time_axis: List[str]) -> Dict[str, Any]:
    n = len(time_axis)
    rca: List[Dict[str, Any]] = []

    for rc in upstream.get("ResourceCategoryAvailabilities", []):
        rcid = rc.get("ResourceCategoryId") or "unknown"
        m = rc.get("Metrics", {}) or {}

        arrays = calculate_availability_arrays(m, n)

        metrics_portal: Dict[str, List[int]] = {
            # Hotel TOTAL ROOMS = ActiveResources
            METRIC_TOTAL_ROOMS: arrays["active"],
            # Hotel AVAILABLE ROOMS = UsableResources
            METRIC_AVAILABLE_ROOMS: arrays["usable"],
            # Hotel = net formula (Usable − Occupied − OtherServiceReservationCount + PublicAvailabilityAdjustment)
            METRIC_HOTEL: arrays["net"],
            # Student/Extended are filled later by other services
            METRIC_STUDENT: [0] * n,
            METRIC_EXTENDED_STAY: [0] * n,
        }

        rca.append({
            "ResourceCategoryId": rcid,
            "ResourceCategoryName": CANONICAL_ID_TO_NAME.get(rcid, rcid),
            "Metrics": metrics_portal,
        })

    return {
        "TimeUnitStartsUtc": time_axis,
        "ResourceCategoryAvailabilities": rca,
    }

def fallback_empty_payload(time_axis: List[str]) -> Dict[str, Any]:

    n = len(time_axis)
    zeros = [0] * n
    return {
        "TimeUnitStartsUtc": time_axis,
        "ResourceCategoryAvailabilities": [
            {
                "ResourceCategoryId": rid,
                "ResourceCategoryName": CANONICAL_ID_TO_NAME.get(rid, rid),
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
    return render_template("index-revenueportal.html")

# ============================================================
# API: ophalen
# ============================================================

# Helpers om platform URL te normaliseren
def _normalize_mews_base(raw: str) -> str:
    if not raw:
        return ""
    lower = raw.lower()
    if "/api/connector" in lower:
        raw = raw[: lower.index("/api/connector")]
    return raw.rstrip("/")


@app.get("/availability")
def get_availability():
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
    access_token = os.getenv("DAVID_WEST_ACCESSTOKEN")
    client_name = "RevenuePortal 1.0.0"
    hotel_service_id = HOTEL_SERVICE_ID
    student_service_id = STUDENT_SERVICE_ID
    extended_service_id = EXTENDED_STAY_SERVICE_ID

    missing = [
        name for name, value in [
            ("DEMO_CLIENTTOKEN", client_token),
            ("DAVID_WEST_ACCESSTOKEN", access_token),
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
        "Occupied",
        "UsableResources",
        "ConfirmedReservations",
        "OptionalReservations",
        "AllocatedBlockAvailability",
        "BlockAvailability",
        "PublicAvailabilityAdjustment",
        "OtherServiceReservationCount"
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

        # Use precomputed mapping from ROOM_TYPE_IDS_BY_SERVICE → canonical IDs
        mapping = SERVICE_SPECIFIC_CATEGORY_MAP.get(service_id, {})
        if not mapping:
            app.logger.warning(
                "No room type mapping available for %s service (service_id=%s), skipping metric merge",
                label,
                service_id,
            )
            continue

        metric_values = map_service_availability_to_canonical(extra_upstream, time_axis, mapping)
        if not metric_values:
            app.logger.info("No matching categories returned for %s service", label)
            continue

        apply_metric_to_portal(portal, metric_name, metric_values, len(time_axis))

    # Log wat er uit komt zonder gevoelige data
    ids = [rc.get("ResourceCategoryId") for rc in portal.get("ResourceCategoryAvailabilities", [])]
    names = [rc.get("ResourceCategoryName") or CANONICAL_ID_TO_NAME.get(rc.get("ResourceCategoryId"), rc.get("ResourceCategoryId")) for rc in portal.get("ResourceCategoryAvailabilities", [])]
    app.logger.info("Returning %d categories (names): %s", len(names), names)

    return jsonify(portal)
# ============================================================
# API: wijzigingen ontvangen (echo of doorsturen)
# ============================================================

@app.put("/availability/overrides")
def save_overrides():
    payload = request.get_json(silent=True) or {}
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
