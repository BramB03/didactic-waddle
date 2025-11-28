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
from profiles import PROFILES

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),  # templates/index-revenueportal.html
    static_folder=str(BASE_DIR / "static")        # /static/* assets
)
logging.basicConfig(level=logging.INFO)

def get_profile(profile_key: str) -> dict:
    """Return profile dict or fallback to default"""
    if profile_key not in PROFILES:
        app.logger.warning("Unknown profile '%s', falling back to default", profile_key)
    return PROFILES.get(profile_key, PROFILES["default"])

# ============================================================
# Constants / configuration
# ============================================================

METRIC_TOTAL_ROOMS = "Total rooms"
METRIC_AVAILABLE_ROOMS = "Available rooms"
METRIC_HOTEL = "Hotel"
METRIC_STUDENT = "Student"
METRIC_EXTENDED_STAY = "Extended stay"
timeZone = "Europe/Amsterdam"

ROOM_TYPE_IDS_BY_SERVICE: Dict[str, Dict[str, str]] = {
    # Service A (hotel)
    "2a11701c-061c-4262-830a-b3a200f3ff40": {
        "Standard Double": "d10c5a8e-3e0a-4180-a7f7-b3a200f423c0",
        "Standard Twin": "b527693b-4c9a-4778-8ee7-b3a200f488a5",
        "Deluxe Double": "f0df4d73-8a79-44f5-822c-b3a200f4b847",
        "Family Room": "36766d2f-c0b5-4ed0-a891-b3a200f4f15b",
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

HOTEL_SERVICE_ID = "2a11701c-061c-4262-830a-b3a200f3ff40"
STUDENT_SERVICE_ID = "5a6ee418-468c-45f7-a3d2-b364007a7c0f"
EXTENDED_STAY_SERVICE_ID = "d9668056-a076-434e-8412-b364007a95da"

# Canonical room type mapping (based on hotel service)
_canonical_source = ROOM_TYPE_IDS_BY_SERVICE.get(HOTEL_SERVICE_ID) or next(iter(ROOM_TYPE_IDS_BY_SERVICE.values()))
ROOM_TYPE_NAME_TO_ID: Dict[str, str] = {name.lower(): rid for name, rid in _canonical_source.items()}
CANONICAL_ID_TO_NAME: Dict[str, str] = {rid: name for name, rid in _canonical_source.items()}
CANONICAL_ROOM_TYPE_IDS = list(CANONICAL_ID_TO_NAME.keys())

# For each service: map that service's ResourceCategoryId -> canonical room type id
SERVICE_SPECIFIC_CATEGORY_MAP: Dict[str, Dict[str, str]] = {}
for service_id, name_to_rcid in ROOM_TYPE_IDS_BY_SERVICE.items():
    SERVICE_SPECIFIC_CATEGORY_MAP[service_id] = {}
    for name, rcid in name_to_rcid.items():
        canonical_id = ROOM_TYPE_NAME_TO_ID.get(name.lower())
        if canonical_id:
            SERVICE_SPECIFIC_CATEGORY_MAP[service_id][rcid] = canonical_id

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


def calculate_basic_service_arrays(metrics: Dict[str, Any], n: int) -> Dict[str, List[int]]:
    usable = ensure_metric_length(metrics.get("UsableResources"), n)
    confirmed = ensure_metric_length(metrics.get("ConfirmedReservations"), n)
    optional = ensure_metric_length(metrics.get("OptionalReservations"), n)
    occupied = ensure_metric_length(metrics.get("Occupied"), n)
    public_adj = ensure_metric_length(metrics.get("PublicAvailabilityAdjustment"), n)
    other_service = ensure_metric_length(metrics.get("OtherServiceReservationCount"), n)

    non_picked_up: List[int] = []
    for occ, conf, opt in zip(occupied, confirmed, optional):
        val = (occ or 0) - (conf or 0) - (opt or 0)
        non_picked_up.append(val)

    return {
        "usable": usable,
        "confirmed": confirmed,
        "optional": optional,
        "occupied": occupied,
        "non_picked_up": non_picked_up,
        "public_adj": public_adj,
        "other_service": other_service,
    }


def iso_midnights_utc_for_month_eu_amsterdam(year: int, month_index: int) -> List[str]:
    tz_nl = ZoneInfo(timeZone)
    month = month_index + 1
    n_days = monthrange(year, month)[1]
    out: List[str] = []
    for d in range(1, n_days + 1):
        local_midnight = datetime(year, month, d, 0, 0, 0, tzinfo=tz_nl)
        as_utc = local_midnight.astimezone(timezone.utc)
        out.append(as_utc.isoformat().replace("+00:00", "Z"))
    return out


def http_session_with_retries() -> requests.Session:
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.4, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s


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


def extract_service_arrays_by_canonical(
    upstream: Dict[str, Any],
    service_id: str,
    n: int,
) -> Dict[str, Dict[str, List[int]]]:
    if not upstream:
        return {}

    rcid_to_canonical = SERVICE_SPECIFIC_CATEGORY_MAP.get(service_id, {})
    result: Dict[str, Dict[str, List[int]]] = {}

    for rc in upstream.get("ResourceCategoryAvailabilities", []):
        rcid = rc.get("ResourceCategoryId")
        metrics = rc.get("Metrics", {}) or {}
        canonical_id = rcid_to_canonical.get(rcid)

        if not canonical_id:
            app.logger.info(
                "Service %s: RC %s has NO canonical mapping, skipping. Name? %s",
                service_id,
                rcid,
                rc.get("ResourceCategoryName"),
            )
            continue

        arrays = calculate_basic_service_arrays(metrics, n)
        result[canonical_id] = arrays

    return result


def build_portal_from_services(
    time_axis: List[str],
    hotel_upstream: Dict[str, Any],
    student_upstream: Dict[str, Any],
    extended_upstream: Dict[str, Any],
) -> Dict[str, Any]:

    n = len(time_axis)

    if not hotel_upstream:
        # No hotel -> nothing meaningful to show
        return fallback_empty_payload(time_axis)

    hotel_arrays = extract_service_arrays_by_canonical(hotel_upstream, HOTEL_SERVICE_ID, n)
    student_arrays = extract_service_arrays_by_canonical(student_upstream, STUDENT_SERVICE_ID, n) if student_upstream else {}
    extended_arrays = extract_service_arrays_by_canonical(extended_upstream, EXTENDED_STAY_SERVICE_ID, n) if extended_upstream else {}

    rca: List[Dict[str, Any]] = []

    for canonical_id in CANONICAL_ROOM_TYPE_IDS:
        h = hotel_arrays.get(canonical_id, {})
        s = student_arrays.get(canonical_id, {})
        e = extended_arrays.get(canonical_id, {})

        usable_h = h.get("usable", [0] * n)
        confirmed_h = h.get("confirmed", [0] * n)
        optional_h = h.get("optional", [0] * n)
        npb_h = h.get("non_picked_up", [0] * n)
        paa_h = h.get("public_adj", [0] * n)
        other_h = h.get("other_service", [0] * n)

        npb_s = s.get("non_picked_up", [0] * n)
        paa_s = s.get("public_adj", [0] * n)

        npb_e = e.get("non_picked_up", [0] * n)
        paa_e = e.get("public_adj", [0] * n)

        # Total Nonpickupblock across ALL services
        total_npb = [
            (nh or 0) + (ns or 0) + (ne or 0)
            for nh, ns, ne in zip(npb_h, npb_s, npb_e)
        ]

        # Available rooms =
        # UsableResources(hotel)
        # - ConfirmedReservations(hotel)
        # - OptionalReservations(hotel)
        # - OtherServiceReservationCount(hotel)
        # - Nonpickupblock(all services)
        base_available = [
            (u or 0) - (ch or 0) - (oh or 0) - (oth or 0) - (np or 0)
            for u, ch, oh, oth, np in zip(usable_h, confirmed_h, optional_h, other_h, total_npb)
        ]

        # Total rooms = UsableResources (Hotel)
        total_rooms = list(usable_h)

        # Service-specific columns
        hotel_metric = [(base or 0) + (adj or 0) for base, adj in zip(base_available, paa_h)]
        student_metric = [(base or 0) + (adj or 0) for base, adj in zip(base_available, paa_s)]
        extended_metric = [(base or 0) + (adj or 0) for base, adj in zip(base_available, paa_e)]

        rca.append({
            "ResourceCategoryId": canonical_id,
            "ResourceCategoryName": CANONICAL_ID_TO_NAME.get(canonical_id, canonical_id),
            "Metrics": {
                METRIC_TOTAL_ROOMS: total_rooms,
                METRIC_AVAILABLE_ROOMS: base_available,
                METRIC_HOTEL: hotel_metric,
                METRIC_STUDENT: student_metric,
                METRIC_EXTENDED_STAY: extended_metric,
            },
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
    return render_template("index-revenueportal.html")

# ============================================================
# API: ophalen
# ============================================================

def _normalize_mews_base(raw: str) -> str:
    if not raw:
        return ""
    lower = raw.lower()
    if "/api/connector" in lower:
        raw = raw[: lower.index("/api/connector")]
    return raw.rstrip("/")


@app.get("/availability")
def get_availability():
    # 1) Params: if missing/invalid -> default to current month in Europe/Amsterdam
    tz_nl = ZoneInfo(timeZone)
    now_local = datetime.now(tz_nl)

    raw_year = request.args.get("year")
    raw_month = request.args.get("month")

    try:
        if raw_year is not None and raw_month is not None:
            year = int(raw_year)
            month = int(raw_month)
            assert 0 <= month <= 11
        else:
            raise ValueError("Missing params")
    except Exception:
        year = now_local.year
        month = now_local.month - 1  # monthIndex 0–11
        app.logger.info(
            "No/invalid year/month provided, defaulting to current month: year=%s monthIndex=%s",
            year,
            month,
        )

    # 2) Time axis based on Europe/Amsterdam → UTC
    time_axis = iso_midnights_utc_for_month_eu_amsterdam(year, month)
    if not time_axis:
        return jsonify({"error": "No dates generated for given month/year"}), 500

    first_utc = time_axis[0]
    last_utc = time_axis[-1]
    app.logger.info("Availability request year=%s monthIndex=%s first=%s last=%s", year, month, first_utc, last_utc)

    # 3) Mews upstream configuration
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
            ("HOTEL_SERVICE_ID", hotel_service_id),
        ]
        if not value
    ]
    if missing:
        app.logger.warning("Upstream config missing: %s", missing)
        return jsonify(fallback_empty_payload(time_axis)), 200

    # Endpoint: getAvailability (ver 2024-01-22)
    url = mews_base + "services/getAvailability/2024-01-22"

    metrics = [
        "ActiveResources",                # not strictly needed, but harmless
        "OutOfOrderBlocks",              # not used in current formulas
        "Occupied",
        "UsableResources",
        "ConfirmedReservations",
        "OptionalReservations",
        "AllocatedBlockAvailability",    # not used but might be useful later
        "BlockAvailability",             # same
        "PublicAvailabilityAdjustment",
        "OtherServiceReservationCount",
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
        resp = session.post(url, json=payload, timeout=15)
        app.logger.info("%s upstream status %s, ServiceId=%s", label, resp.status_code, service_id)
        resp.raise_for_status()

        # TEMP FIX
        body = resp.json()

        if label == "Hotel":
            time_units = body.get("TimeUnitStartsUtc", [])
            rcs = body.get("ResourceCategoryAvailabilities", [])
            if rcs:
                m0 = rcs[0].get("Metrics", {})
                app.logger.info(
                    "Hotel upstream first RC metrics (day0): usable=%s, confirmed=%s, optional=%s, occupied=%s, other=%s, adj=%s",
                    (m0.get("UsableResources") or [None])[0],
                    (m0.get("ConfirmedReservations") or [None])[0],
                    (m0.get("OptionalReservations") or [None])[0],
                    (m0.get("Occupied") or [None])[0],
                    (m0.get("OtherServiceReservationCount") or [None])[0],
                    (m0.get("PublicAvailabilityAdjustment") or [None])[0],
                )

        return body

    # 4) Call Hotel (required)
    try:
        hotel_upstream = call_service(hotel_service_id, "Hotel")
    except requests.RequestException as e:
        app.logger.warning("Hotel upstream call failed, serving fallback payload: %s", e)
        return jsonify(fallback_empty_payload(time_axis)), 200

    # 5) Call Student / Extended (optional; if they fail, just treat as zeros)
    student_upstream = None
    if student_service_id:
        try:
            student_upstream = call_service(student_service_id, "Student")
        except requests.RequestException as e:
            app.logger.warning("Student upstream call failed, ignoring: %s", e)

    extended_upstream = None
    if extended_service_id:
        try:
            extended_upstream = call_service(extended_service_id, "Extended stay")
        except requests.RequestException as e:
            app.logger.warning("Extended stay upstream call failed, ignoring: %s", e)

    # 6) Aggregate into portal payload
    try:
        portal = build_portal_from_services(time_axis, hotel_upstream, student_upstream, extended_upstream)
    except Exception as e:
        app.logger.exception("Transform failed")
        return jsonify({"error": "Transform failed", "detail": str(e)}), 500

    ids = [rc.get("ResourceCategoryId") for rc in portal.get("ResourceCategoryAvailabilities", [])]
    names = [rc.get("ResourceCategoryName") for rc in portal.get("ResourceCategoryAvailabilities", [])]

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