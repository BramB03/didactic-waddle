# revenue-portal/mainrevenueportal.py

from flask import Flask, render_template, request, jsonify
from pathlib import Path
from calendar import monthrange
from datetime import datetime, timezone
from typing import List, Dict, Any
from zoneinfo import ZoneInfo
import requests
from requests.adapters import HTTPAdapter, Retry
import os
import logging

from revenue_portal.profiles import PROFILES

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
logging.basicConfig(level=logging.INFO)

# ============================================================
# Helpers for profiles
# ============================================================

def get_profile(profile_key: str) -> dict:
    """Return profile dict or fallback to default"""
    if profile_key not in PROFILES:
        app.logger.warning("Unknown profile '%s', falling back to default", profile_key)
    return PROFILES.get(profile_key, PROFILES["default"])


# ============================================================
# Helper functions (same as before)
# ============================================================

def ensure_metric_length(arr: Any, n: int) -> List[int]:
    if not isinstance(arr, list):
        return [0] * n
    padded = (arr + [0] * n)[:n]
    return [int(v) if isinstance(v, (int, float)) else 0 for v in padded]


def calculate_basic_service_arrays(metrics: Dict[str, Any], n: int) -> Dict[str, List[int]]:
    usable = ensure_metric_length(metrics.get("UsableResources"), n)
    confirmed = ensure_metric_length(metrics.get("ConfirmedReservations"), n)
    optional = ensure_metric_length(metrics.get("OptionalReservations"), n)
    occupied = ensure_metric_length(metrics.get("Occupied"), n)
    public_adj = ensure_metric_length(metrics.get("PublicAvailabilityAdjustment"), n)

    non_picked_up = [(occ or 0) - (conf or 0) - (opt or 0)
                     for occ, conf, opt in zip(occupied, confirmed, optional)]

    return {
        "usable": usable,
        "confirmed": confirmed,
        "optional": optional,
        "occupied": occupied,
        "non_picked_up": non_picked_up,
        "public_adj": public_adj,
    }


def iso_midnights_utc_for_month_eu_amsterdam(year: int, month_index: int, tz_name: str) -> List[str]:
    tz_nl = ZoneInfo(tz_name)
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

def get_profile(profile_key: str) -> dict:
    if profile_key not in PROFILES:
        app.logger.warning("Unknown profile '%s', falling back to default", profile_key)
    return PROFILES.get(profile_key, PROFILES["default"])

def fallback_empty_payload(time_axis: List[str], canonical_map: Dict[str, str]) -> Dict[str, Any]:
    n = len(time_axis)
    zeros = [0] * n
    return {
        "TimeUnitStartsUtc": time_axis,
        "ResourceCategoryAvailabilities": [
            {
                "ResourceCategoryId": rid,
                "ResourceCategoryName": name,
                "Metrics": {
                    "Total rooms": zeros,
                    "Available rooms": zeros,
                    "Hotel": zeros,
                    "Student": zeros,
                    "Extended stay": zeros,
                },
            }
            for rid, name in canonical_map.items()
        ],
    }


# ============================================================
# Data transformation (same as before)
# ============================================================

def extract_service_arrays_by_canonical(upstream: Dict[str, Any], service_id: str, n: int,
                                        service_map: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, List[int]]]:
    if not upstream:
        app.logger.info("No upstream data for service %s", service_id)
        return {}
    rcid_to_canonical = service_map.get(service_id, {})

    result: Dict[str, Dict[str, List[int]]] = {}
    for rc in upstream.get("ResourceCategoryAvailabilities", []):
        rcid = rc.get("ResourceCategoryId")
        metrics = rc.get("Metrics", {}) or {}
        canonical_id = rcid_to_canonical.get(rcid)
        if not canonical_id:
            app.logger.debug("Service %s RC %s has no canonical mapping, skipping", service_id, rcid)
            continue
        result[canonical_id] = calculate_basic_service_arrays(metrics, n)

    return result


def build_portal_from_services(time_axis: List[str],
                               hotel_upstream: Dict[str, Any],
                               student_upstream: Dict[str, Any],
                               extended_upstream: Dict[str, Any],
                               profile: dict) -> Dict[str, Any]:

    n = len(time_axis)
    if not hotel_upstream:
        app.logger.info("No hotel upstream data, returning empty payload")
        return fallback_empty_payload(time_axis, get_canonical_map(profile))

    service_map = build_service_specific_map(profile)
    hotel_arrays = extract_service_arrays_by_canonical(hotel_upstream, profile["hotel_service_id"], n, service_map)
    student_arrays = extract_service_arrays_by_canonical(student_upstream, profile["student_service_id"], n, service_map) if student_upstream else {}
    extended_arrays = extract_service_arrays_by_canonical(extended_upstream, profile["extended_service_id"], n, service_map) if extended_upstream else {}

    rca = []

    for canonical_id, name in get_canonical_map(profile).items():
        h = hotel_arrays.get(canonical_id, {})
        s = student_arrays.get(canonical_id, {})
        e = extended_arrays.get(canonical_id, {})

        usable_h = h.get("usable", [0] * n)
        confirmed_h = h.get("confirmed", [0] * n)
        optional_h = h.get("optional", [0] * n)
        npb_h = h.get("non_picked_up", [0] * n)
        paa_h = h.get("public_adj", [0] * n)

        npb_s = s.get("non_picked_up", [0] * n)
        paa_s = s.get("public_adj", [0] * n)
        npb_e = e.get("non_picked_up", [0] * n)
        paa_e = e.get("public_adj", [0] * n)

        total_npb = [(nh or 0) + (ns or 0) + (ne or 0)
                     for nh, ns, ne in zip(npb_h, npb_s, npb_e)]
        base_available = [(u or 0) - (ch or 0) - (oh or 0) - (np or 0)
                          for u, ch, oh, np in zip(usable_h, confirmed_h, optional_h, total_npb)]

        total_rooms = list(usable_h)
        hotel_metric = [(b or 0) + (a or 0) for b, a in zip(base_available, paa_h)]
        student_metric = [(b or 0) + (a or 0) for b, a in zip(base_available, paa_s)]
        extended_metric = [(b or 0) + (a or 0) for b, a in zip(base_available, paa_e)]

        rca.append({
            "ResourceCategoryId": canonical_id,
            "ResourceCategoryName": name,
            "Metrics": {
                "Total rooms": total_rooms,
                "Available rooms": base_available,
                "Hotel": hotel_metric,
                "Student": student_metric,
                "Extended stay": extended_metric,
            },
        })

    return {"TimeUnitStartsUtc": time_axis, "ResourceCategoryAvailabilities": rca}


# ============================================================
# Utility builders
# ============================================================

def build_service_specific_map(profile: dict) -> Dict[str, Dict[str, str]]:
    room_type_ids_by_service = profile["room_type_ids_by_service"]
    frontend_map = profile.get("frontend_room_types", {})

    # canonical: name.lower() -> canonical_rcid (the ones used in the frontend)
    canonical_by_name: Dict[str, str] = {
        cfg["name"].lower(): canonical_rcid
        for canonical_rcid, cfg in frontend_map.items()
        if isinstance(cfg, dict) and "name" in cfg
    }

    service_map: Dict[str, Dict[str, str]] = {}

    for service_id, mapping in room_type_ids_by_service.items():
        # mapping: { "Standard Single": "<service-specific-rcid>", ... }
        rcid_to_canonical: Dict[str, str] = {}
        for name, service_rcid in mapping.items():
            canonical_id = canonical_by_name.get(name.lower())
            if not canonical_id:
                app.logger.warning(
                    "No canonical id found for name '%s' in service %s",
                    name, service_id
                )
                continue
            # Map upstream RCID -> canonical RCID
            rcid_to_canonical[service_rcid] = canonical_id

        service_map[service_id] = rcid_to_canonical

    return service_map


def get_canonical_map(profile: dict) -> Dict[str, str]:
    """Return canonical_id -> readable name from the first service"""
    canonical = list(profile["room_type_ids_by_service"].values())[0]
    return {rid: name for name, rid in canonical.items()}


# ============================================================
# ROUTES
# ============================================================

@app.get("/<profile>/")
def index(profile):
    return render_template("index-revenueportal.html")


@app.get("/")
def index_default():
    return render_template("index-revenueportal.html")


@app.get("/<profile>/availability")
def get_availability(profile):
    cfg = get_profile(profile)

    tz = cfg.get("timezone", "Europe/Amsterdam")
    tz_local = ZoneInfo(tz)
    now_local = datetime.now(tz_local)

    year = int(request.args.get("year", now_local.year))
    month_index = int(request.args.get("month", now_local.month - 1))

    time_axis = iso_midnights_utc_for_month_eu_amsterdam(year, month_index, tz)
    if not time_axis:
        return jsonify({"error": "No dates generated"}), 500

    mews_base = cfg["mews_base"]
    client_token = os.getenv(cfg["client_token_env"])
    access_token = os.getenv(cfg["access_token_env"])
    client_name = cfg["client_name"]

    hotel_service_id = cfg["hotel_service_id"]
    student_service_id = cfg["student_service_id"]
    extended_service_id = cfg["extended_service_id"]

    url = mews_base + "services/getAvailability/2024-01-22"  # <-- fixed
    metrics = [
        "ActiveResources", "Occupied", "UsableResources", "ConfirmedReservations",
        "OptionalReservations", "PublicAvailabilityAdjustment", "OtherServiceReservationCount"
    ]

    payload_template = {
        "ClientToken": client_token,
        "AccessToken": access_token,
        "Client": client_name,
        "FirstTimeUnitStartUtc": time_axis[0],
        "LastTimeUnitStartUtc": time_axis[-1],
        "Metrics": metrics,
    }

    session = http_session_with_retries()

    def call_service(service_id: str, label: str) -> Dict[str, Any]:
        payload = dict(payload_template)
        payload["ServiceId"] = service_id
        resp = session.post(url, json=payload, timeout=15)
        app.logger.info("%s upstream status %s", label, resp.status_code)
        resp.raise_for_status()
        return resp.json()

    try:
        hotel_upstream = call_service(hotel_service_id, "Hotel")
    except Exception as e:
        app.logger.warning("Hotel upstream failed: %s", e)
        return jsonify(fallback_empty_payload(time_axis, get_canonical_map(cfg))), 200

    student_upstream = None
    extended_upstream = None
    try:
        if student_service_id:
            student_upstream = call_service(student_service_id, "Student")
    except Exception as e:
        app.logger.warning("Student upstream failed: %s", e)
    try:
        if extended_service_id:
            extended_upstream = call_service(extended_service_id, "Extended stay")
    except Exception as e:
        app.logger.warning("Extended stay upstream failed: %s", e)

    portal = build_portal_from_services(time_axis, hotel_upstream, student_upstream, extended_upstream, cfg)
    return jsonify(portal)


@app.get("/availability")
def get_availability_default():
    return get_availability("default")


@app.put("/<profile>/availability/overrides")
def save_overrides(profile):
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "status": "ok",
        "profile": profile,
        "editCount": len(payload.get("Edits", []))
    })


@app.put("/availability/overrides")
def save_overrides_default():
    return save_overrides("default")


@app.get("/<profile>/room-types")
def get_room_types(profile):
    cfg = get_profile(profile)
    room_types = cfg.get("frontend_room_types", {})
    return jsonify(room_types)

from flask import jsonify

@app.get("/profiles")
def list_profiles():
    return jsonify(sorted(PROFILES.keys()))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)