from __future__ import annotations
from flask import Flask, jsonify, render_template_string, request
from pathlib import Path
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import json, tempfile, shutil
import requests

app = Flask(__name__)

# Config

queueFilePath = Path("data_storage.txt")  # TXT-bestand met JSON array van wachtrij-items

# (Alleen gebruikt als USE_DEMO=False)
clientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
accessToken = "BEC33DAD4C57410C9E6DB09600C7FB9B-310471532A30162E5B6F0EB4F4AD2BF"
client = "Mews Import Application"
url = "https://api.mews-demo.com/api/connector/v1/"

# Helpers (IO + tijd)
def readQueue():
    """Lees de wachtrij uit TXT (JSON array)."""
    if not queueFilePath.exists():
        return []
    try:
        return json.loads(queueFilePath.read_text(encoding="utf-8")) or []
    except Exception:
        return []

def writeQueue(items):
    """Schrijf wachtrij op atomaire manier naar TXT."""
    queueFilePath.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(queueFilePath.parent), encoding="utf-8") as tmp:
        json.dump(items, tmp, ensure_ascii=False)
        tmp.flush()
        tmpName = tmp.name
    shutil.move(tmpName, queueFilePath)

def nowIso():
    return datetime.now(timezone.utc).isoformat()

def getUtcMidnights(timezoneName: str):
    """Bepaalt lokale midnights en converteert naar UTC ISO (millis, Z)."""
    tz = ZoneInfo(timezoneName)
    now = datetime.now(tz)
    lastMidnightLocal = now.replace(hour=0, minute=0, second=0, microsecond=0)
    nextMidnightLocal = lastMidnightLocal + timedelta(days=1)
    lastMidnightUtc = lastMidnightLocal.astimezone(ZoneInfo("UTC"))
    nextMidnightUtc = nextMidnightLocal.astimezone(ZoneInfo("UTC"))
    formatIso = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return formatIso(lastMidnightUtc), formatIso(nextMidnightUtc)


# Hooks voor “verdere flow”
def processNewEntry(reservation: dict, customer: dict | None):
    """
    Acties voor NIEUWE items (bijv. Teams-bericht, Mews Task).
    Hou dit idempotent. Voor demo: log alleen.
    """
    rid = reservation.get("reservationId")
    gname = (customer or {}).get("fullName")
    print(f"[processNewEntry] New on waitlist -> reservationId={rid}, guest={gname}")


# Extractors
def extractReservationInformation(apiResponse: dict) -> list[dict]:
    """Uit Mews reservations/getAll response -> basale velden voor onze logic."""
    out = []
    for r in apiResponse.get("Reservations", []):
        out.append({
            "number": r.get("Number"),
            "reservationId": r.get("Id"),
            "reservationUrl": f"https://app.mews-demo.com/Commander/8dc59049-c9d0-4d08-a489-ae94011b28e5/Reservation/Detail/{r.get('Id')}",
            "assignedResourceId": r.get("AssignedResourceId"),
            "accountId": r.get("AccountId"),
            "requestedResourceCategoryId": r.get("RequestedResourceCategoryId"),
        })
    return out

def extractCustomerBasics(apiResponse: dict) -> list[dict]:
    """Uit Mews customers/getAll -> alleen klanten met classificatie 'WaitingForRoom'."""
    dataOut = []
    for customer in apiResponse.get("Customers", []):
        if "WaitingForRoom" not in (customer.get("Classifications") or []):
            continue
        fullName = f"{customer.get('FirstName','')} {customer.get('LastName','')}".strip()
        phone = customer.get("Phone")
        email = customer.get("Email")
        classifications = customer.get("Classifications") or []
        filtered = [v for v in classifications if v != "WaitingForRoom"]
        classification = ", ".join(filtered) if filtered else None
        contactMethod = phone or email or "Not Available"
        dataOut.append({
            "fullName": fullName,
            "customerId": customer.get("Id"),
            "contactMethod": contactMethod,
            "notes": customer.get("Notes"),
            "classification": classification
        })
    return dataOut


# Upstream fetchers (REAL)
def fetchReservationsAndCustomers_real() -> tuple[list[dict], list[dict]]:
    """ECHTE Mews calls: reservations/getAll en customers/getAll."""
    headers = { "Content-Type": "application/json" }
    tzName = "Europe/Amsterdam"
    startUtc, endUtc = getUtcMidnights(tzName)

    payloadReservations = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "ScheduledStartUtc": { "StartUtc": startUtc, "EndUtc": endUtc },
        "States": ["Confirmed"],
        "Limitation": { "Count": 1000 }
    }
    resReservations = requests.post(url + "reservations/getAll/2023-06-06", data=json.dumps(payloadReservations), headers=headers)
    if resReservations.status_code != 200:
        raise RuntimeError(f"reservations/getAll error: {resReservations.status_code} {resReservations.text}")
    reservations_extracted = extractReservationInformation(resReservations.json())

    accountIds = list({ r["accountId"] for r in reservations_extracted if r.get("accountId") })
    payloadCustomers = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "Extent": {"Customers": True, "Documents": False, "Addresses": False},
        "CustomerIds": accountIds,
        "Limitation": { "Count": 1000 }
    }
    resCustomers = requests.post(url + "customers/getAll", data=json.dumps(payloadCustomers), headers=headers)
    if resCustomers.status_code != 200:
        raise RuntimeError(f"customers/getAll error: {resCustomers.status_code} {resCustomers.text}")
    customers_extracted = extractCustomerBasics(resCustomers.json())

    return reservations_extracted, customers_extracted

def fetchResourcesAndOccupancy_real(resourceIds: list[str], resourceCategoryIds: list[str]):
    """Haalt Resources + ResourceCategories + OccupancyState op en maakt handige lookups."""
    headers = { "Content-Type": "application/json" }

    payloadResources = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "ResourceIds": resourceIds,
        "Extent": {"Resources": True, "ResourceCategories": True},
        "Limitation": {"Count": 100}
    }
    resResources = requests.post(url + "resources/getAll", data=json.dumps(payloadResources), headers=headers)
    if resResources.status_code != 200:
        raise RuntimeError(f"resources/getAll error: {resResources.status_code} {resResources.text}")
    resources_json = resResources.json()
    resourceLookup = {}
    for r in resources_json.get("Resources", []):
        resourceLookup[r.get("Id")] = {"name": r.get("Name"), "State": r.get("State")}
    categoryNames = {}
    for c in resources_json.get("ResourceCategories", []):
        # Neem Engelse naam als die er is, anders Id
        nm = (c.get("Names") or {}).get("en-GB") or c.get("Id")
        categoryNames[c.get("Id")] = nm

    payloadStates = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "ResourceCategoryIds": resourceCategoryIds,
        "Limitation": { "Count": 100 }
    }
    resStates = requests.post(url + "resources/getOccupancyState", data=json.dumps(payloadStates), headers=headers)
    if resStates.status_code != 200:
        raise RuntimeError(f"resources/getOccupancyState error: {resStates.status_code} {resStates.text}")
    occ_json = resStates.json()
    occupancyLookup = {}
    for cat in occ_json.get("ResourceCategoryOccupancyStates", []):
        for s in cat.get("ResourceOccupancyStates", []):
            rid = s.get("ResourceId")
            if rid:
                occupancyLookup[rid] = {"occupancyState": s.get("OccupancyState")}

    return resourceLookup, occupancyLookup, categoryNames


# Kernfunctie: getAllData
def combineState(baseState: str | None, occupancyState: str | None) -> str | None:
    """Combineert housekeeping state + occupancy naar leesbare vorm zoals in je originele bestand."""
    if occupancyState == "Unknown":
        occupancyState = None
    elif occupancyState == "ReservedLocked":
        occupancyState = "Occupied"
    elif occupancyState == "Reserved":
        occupancyState = "Reserved"
    elif occupancyState == "Vacant":
        occupancyState = "Vacant"
    elif occupancyState == "InternalUse":
        occupancyState = "House use"
    elif occupancyState == "OutOfOrder":
        occupancyState = "Out of order"

    parts = [s for s in [baseState, occupancyState] if s]
    return ", ".join(parts) if parts else None

def getAllData():
    """
    Haalt upstream data (demo/real), filtert op WaitingForRoom, verrijkt met kamers + occupancy,
    en vergelijkt met TXT:
    - Nieuwe -> toevoegen + processNewEntry()
    - Bestaande -> velden updaten (geen extra flow)
    - Niet-terugkomende -> verwijderen
    Schrijft TXT en retourneert diff + actuele queue.
    """
    # 1) Reservations + Customers
    reservations, customers = fetchReservationsAndCustomers_real()

    # Geen enkele WaitingForRoom -> queue leegmaken
    if not customers:
        oldQueue = readQueue()
        writeQueue([])
        return { "added": [], "kept": [], "removed": oldQueue, "waitlist": [] }

    # 2) Filter reservations tot accounts die wachten
    waitingCustomerIds = { c["customerId"] for c in customers }
    reservations_filtered = [ r for r in reservations if r.get("accountId") in waitingCustomerIds ]

    # 3) Resources + Occupancy (REAL) of DEMO lookups
    resourceIds = list({ r["assignedResourceId"] for r in reservations_filtered if r.get("assignedResourceId") })
    resourceCategoryIds = list({ r["requestedResourceCategoryId"] for r in reservations_filtered if r.get("requestedResourceCategoryId") })
    resourceLookup, occupancyLookup, categoryNames = fetchResourcesAndOccupancy_real(resourceIds, resourceCategoryIds)

    # 4) Verrijk records
    customerById = { c["customerId"]: c for c in customers }
    enrichedByResId: dict[str, dict] = {}
    for r in reservations_filtered:
        rid = r.get("reservationId")
        if not rid:
            continue
        assignedResourceId = r.get("assignedResourceId")
        resInfo = resourceLookup.get(assignedResourceId, {}) if assignedResourceId else {}
        baseState = resInfo.get("State")
        occState = (occupancyLookup.get(assignedResourceId) or {}).get("occupancyState") if assignedResourceId else None
        combined = combineState(baseState, occState)

        categoryId = r.get("requestedResourceCategoryId")
        categoryName = categoryNames.get(categoryId, categoryId) if categoryId else None

        cust = customerById.get(r.get("accountId"))
        enrichedByResId[str(rid)] = {
            "number": r.get("number"),
            "reservationId": r.get("reservationId"),
            "reservationUrl": r.get("reservationUrl"),
            "accountId": r.get("accountId"),
            "fullName": (cust or {}).get("fullName"),
            "contactMethod": (cust or {}).get("contactMethod"),
            "notes": (cust or {}).get("notes"),
            "Classification": (cust or {}).get("classification"),
            "assignedResourceId": assignedResourceId,
            "assignedResourceName": resInfo.get("name"),
            "assignedResourceState": combined,
            "requestedResourceCategoryId": categoryName
          }

    # 5) Queue diff (add/keep/remove)
    queueItems = readQueue()
    queueByReservationId = { str(i.get("reservationId")): i for i in queueItems if i.get("reservationId") }

    currentIds = set(enrichedByResId.keys())
    queueIds   = set(queueByReservationId.keys())

    toAddIds    = currentIds - queueIds
    toKeepIds   = currentIds & queueIds
    toRemoveIds = queueIds   - currentIds

    addedItems, keptItems, removedItems = [], [], []

    # Voeg nieuw toe
    for rid in toAddIds:
        enriched = enrichedByResId[rid].copy()
        enriched["queuedAt"] = datetime.now(ZoneInfo("Europe/Amsterdam")).strftime("%H:%M:%S")
        processNewEntry(enriched, None)  # je kunt hier ook reservation/customer doorgeven als je wilt
        addedItems.append(enriched)

    # Bestaande bijwerken met nieuwste velden, queuedAt behouden
    for rid in toKeepIds:
        old = queueByReservationId[rid].copy()
        enriched = enrichedByResId[rid]
        # velden updaten (maar queuedAt laten staan)
        for k, v in enriched.items():
            old[k] = v
        keptItems.append(old)

    # Verwijderen
    for rid in toRemoveIds:
        removedItems.append(queueByReservationId[rid])

    # Nieuwe queue schrijven
    newQueue = keptItems + addedItems
    writeQueue(newQueue)

    print(f"Queue sync → added: {len(addedItems)}, kept: {len(keptItems)}, removed: {len(removedItems)}")

    return { "added": addedItems, "kept": keptItems, "removed": removedItems, "waitlist": newQueue }


# UI (met jouw HTML/layout)
@app.route("/")
def index():
    """
    1) Render direct vanuit TXT (snel zichtbaar) in jouw UI-layout.
    2) Buttons voor Sync en Demo.
    """
    items = readQueue()

    # Map queue-items naar de template-verwachting "result"
    result = []
    for i in items:
        result.append({
            "number": i.get("number"),
            "fullName": i.get("fullName"),
            "contactMethod": i.get("contactMethod"),
            "assignedResourceName": i.get("assignedResourceName"),
            "assignedResourceState": i.get("assignedResourceState"),
            "Classification": i.get("Classification"),
            "requestedResourceCategoryId": i.get("requestedResourceCategoryId"),
            "notes": i.get("notes"),
            "reservationId": i.get("reservationId"),
            "accountId": i.get("accountId"),
            "reservationUrl": i.get("reservationUrl"),
            "assignedResourceId": i.get("assignedResourceId"),
            "queuedAt": i.get("queuedAt"),
        })

    HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Reservation Queue Overview</title>

  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

  <style>
    :root{
      --bg: #f7f8fa;
      --surface: #ffffff;
      --text: #1a1d29;
      --text-muted: #6b7280;
      --border: #e7eaf0;
      --brand: #1c7ed6;
      --brand-600: #1864ab;
      --chip-bg: #f1f3f5;
      --chip-text: #343a40;
      --link: #0b6bcb;
      --row-hover: #f8fafc;
      --shadow-sm: 0 1px 2px rgba(16,24,40,.06);
      --shadow-md: 0 8px 24px rgba(16,24,40,.08);
      --radius: 10px;
    }

    html, body { height: 100%; }
    body{
      margin:0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Apple Color Emoji","Segoe UI Emoji";
    }

    .container{ max-width: 1200px; margin: 32px auto; padding: 0 20px; }

    .btn[data-loading="1"] { opacity: .7; cursor: wait; }

    .header{ display:flex; align-items:center; justify-content: space-between; margin-bottom: 16px; }
    .title{ display:flex; align-items:baseline; gap:12px; }
    .title h1{ margin:0; font-size: clamp(18px, 2.2vw, 24px); font-weight: 600; }
    .subtitle{
      color: var(--text-muted); font-size: 13px;
      padding: 2px 8px; border: 1px solid var(--border); border-radius: 999px; background: #fff;
    }

    .toolbar{ display:flex; gap:10px; }
    .btn{
      appearance:none; border:1px solid var(--border); background:#fff; color: var(--text);
      padding: 8px 12px; border-radius: 8px; font-weight: 600; font-size: 13px; cursor:pointer;
      transition: background .15s ease, border-color .15s ease, transform .04s ease;
      box-shadow: var(--shadow-sm);
    }
    .btn:hover{ background:#f9fafb; border-color:#dde3ea; }
    .btn.primary{ background: var(--brand); border-color: var(--brand); color:#fff; }
    .btn.primary:hover{ background: var(--brand-600); border-color: var(--brand-600); }
    .btn[disabled]{ opacity:.7; cursor:not-allowed; background:#f1f3f5; color:#9ca3af; border-color:#e5e7eb; }

    .card{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow-md);
      overflow: hidden;
    }
    .table-wrap{ overflow:auto; }
    table{ width:100%; border-collapse: collapse; font-size: 13.5px; min-width: 960px; }
    thead th{
      position: sticky; top:0; z-index:1;
      text-align:left; font-weight:600;
      background: #fff;
      border-bottom: 1px solid var(--border);
      padding: 12px 14px; color: #111827;
    }
    tbody td{ padding: 12px 14px; border-bottom: 1px solid var(--border); color: #283041; }
    tbody tr:hover{ background: var(--row-hover); }
    .mono{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
    .footer{ display:flex; align-items:center; justify-content: space-between; padding: 10px 14px; color: var(--text-muted); font-size: 12px; background:#fff; }
    .btn.small { padding: 6px 10px; font-size: 12px; border-radius: 6px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="title">
        <h1>Reservation Overview</h1>
        <span class="subtitle">Live view</span>
      </div>
      <div class="toolbar">
        <button class="btn primary" id="syncBtn" title="Sync the waitlist">⟲ Sync now</button>
        <button class="btn" id="lastSyncBtn" disabled>Last sync: —</button>
      </div>
    </div>

    <div class="card">
      <div class="table-wrap">
        <table aria-label="Reservation overview table">
          <thead>
            <tr>
              <th>Res No.</th>
              <th>Queued At</th>
              <th>Guest</th>
              <th>Contact</th>
              <th>Room Number</th>
              <th>Room State</th>
              <th>Classification</th>
              <th>Requested Category</th>
              <th>Notes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {% for r in result %}
              <tr>
                <td class="mono">{{ r.number | default('—') }}</td>
                <td class="mono">{{ r.queuedAt | default('—') }}</td>
                <td>{{ r.fullName | default('—') }}</td>
                <td class="mono">{{ r.contactMethod | default('—') }}</td>
                <td>{{ r.assignedResourceName | default('—') }}</td>
                <td>{{ r.assignedResourceState | default('—') }}</td>
                <td>{{ r.Classification | default('—') }}</td>
                <td class="mono">{{ r.requestedResourceCategoryId | default('—') }}</td>
                <td>{{ r.notes if r.notes is not none and r.notes != '' else '—' }}</td>
                <td>
                  {% set state = (r.assignedResourceState or '') %}
                  {% set allowedStates = ['Inspected, Vacant', 'Inspected, Reserved', 'Inspected, Reserved/Vacant'] %}
                  {% set canCheckIn = state in allowedStates %}
                  {% set hasPaymaster = r.Classification and 'PaymasterAccount' in r.Classification %}

                  <div class="actions" style="display:flex; gap:8px;">
                    <button
                      class="btn small action-checkin"
                      data-reservation-id="{{ r.reservationId }}"
                      data-reservation-queuedAt="{{ r.queuedAt }}"
                      data-reservation-url="{{ r.reservationUrl }}"
                      data-number="{{ r.number }}"
                      data-full-name="{{ r.fullName }}"
                      data-assigned-resource-id="{{ r.assignedResourceId }}"
                      data-requested-category="{{ r.requestedResourceCategoryId }}"
                      data-account-id="{{ r.accountId }}"
                      data-classification="{{ r.Classification or '' }}"
                      {% if not canCheckIn %}disabled{% endif %}
                    >Check in</button>

                    <button
                      class="btn small action-paymaster"
                      data-reservation-id="{{ r.reservationId }}"
                      data-number="{{ r.number }}"
                      data-full-name="{{ r.fullName }}"
                      data-account-id="{{ r.accountId }}"
                      data-classification="{{ r.Classification or '' }}"
                      {% if hasPaymaster %}disabled{% endif %}
                    >Enable roomcharging</button>
                  </div>
                </td>
              </tr>
            {% else %}
              <tr>
                <td colspan="9" class="muted">No data available.</td>
              </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      <div class="footer">
        <span class="muted">Tip: Click “Sync now” to refresh. Timestamp shows last sync time.</span>
      </div>
    </div>
  </div>

  <script>
    function formatDateTimeHuman(date) {
      const pad = (n) => String(n).padStart(2, '0');
      return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
    }
    function setLastSyncNow(){
      const btn = document.getElementById('lastSyncBtn');
      btn.textContent = 'Last sync: ' + formatDateTimeHuman(new Date());
    }

    async function postJSON(url, payload, button){
      try {
        button?.setAttribute('disabled', 'disabled');
        button?.setAttribute('data-loading', '1');
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
        return data;
      } finally {
        button?.removeAttribute('data-loading');
        button?.removeAttribute('disabled');
      }
    }

    function gatherPayloadFromButton(btn){
      const classificationArr = (btn.dataset.classification || '')
        .split(',')
        .map(s => s.trim())
        .filter(Boolean);

      return {
        reservationId: btn.dataset.reservationId || null,
        accountId: btn.dataset.accountId || null,
        number: btn.dataset.number || null,
        fullName: btn.dataset.fullName || null,
        assignedResourceId: btn.dataset.assignedResourceId || null,
        requestedResourceCategoryId: btn.dataset.requestedCategory || null,
        classification: classificationArr,
        reservationUrl: btn.dataset.reservationUrl || null,
      };
    }

    async function syncNow(btn){
      try{
        const res = await fetch('/sync');
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        // Herlaad pagina om nieuwe TXT te tonen in de tabel
        setLastSyncNow();
        window.location.reload();
      }catch(e){
        alert('Sync failed: ' + e.message);
      }
    }

    let lastVersion = null;

    async function checkForUpdates() {
      try {
        const res = await fetch("/cache/version");
        const data = await res.json();
        const currentVersion = data.mtime;

        // Altijd initialiseren als eerste stap
        if (!lastVersion) lastVersion = currentVersion;

        const age = Date.now() / 1000 - currentVersion;
        const isStale = age > 60;

        if (isStale) {
          console.log("♻️ TXT stale — syncing...");
          const syncRes = await fetch("/sync");
          if (syncRes.ok) {
            console.log("✅ Sync done — reloading page");
            window.location.reload();
          }
        }

      } catch (e) {
        console.error("Auto-sync check failed:", e);
      }
    }
    
    document.addEventListener('click', async (ev) => {
      const btn = ev.target.closest('button');
      if (!btn) return;

      if (btn.id === 'syncBtn') {
        syncNow(btn);
      }

      if (btn.id === 'demoBtn') {
        await fetch('/demo/next').then(() => syncNow(btn));
      }

      if (btn.classList.contains('action-paymaster')) {
        const payload = gatherPayloadFromButton(btn);
        try {
          await postJSON('/api/paymaster', payload, btn);
          window.location.reload();
        } catch (e) {
          alert(`Paymaster failed: ${e.message}`);
        }
      }
    });

    // init
    setLastSyncNow();
    checkForUpdates();
    setInterval(checkForUpdates, 60000); // check every 60s
  </script>
</body>
</html>
'''
    return render_template_string(HTML, result=result)


# =========================
# API endpoints
# =========================
@app.route("/sync")
def syncRoute():
    """Volledige delta-sync uitvoeren en queue updaten."""
    try:
        result = getAllData()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/waitlist")
def apiWaitlist():
    """Raw uit TXT (zonder sync)."""
    return jsonify(readQueue())

@app.route("/api/check-in", methods=["POST"])
def api_check_in():
    """Volledige delta-sync uitvoeren en queue updaten."""
    import time
    time.sleep(120)
    try:
        result = getAllData()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/paymaster", methods=["POST"])
def api_paymaster():
    import json, requests
    payload = request.get_json(silent=True) or {}
    customerId = payload.get("accountId")
    number = payload.get("number")
    full_name = payload.get("fullName")
    classification = payload.get("classification") or []  # should be list

    if isinstance(classification, str):
        classification = [c.strip() for c in classification.split(",") if c.strip()]

    filtered = [c for c in classification if c not in ("WaitingForRoom",)]
    for flag in ("PaymasterAccount", "WaitingForRoom"):
        if flag not in filtered:
            filtered.append(flag)

    payloadPaymaster = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "CustomerId": customerId,
        "Classifications": filtered,
    }

    responsePaymaster = requests.post(
        url + "customers/update",
        json=payloadPaymaster,
        timeout=20
    )
    if responsePaymaster.status_code != 200:
        return jsonify({
            "status": "error",
            "message": f"Paymaster creation failed: {responsePaymaster.text}"
        }), 500
    else:
      queue = readQueue()  # jouw helper die data storage.txt als JSON laadt

      for item in queue:
          if item.get("number") == number:
              classifications = item.get("Classification", "")
              if "PaymasterAccount" not in classifications:
                  # Voeg classificatie toe
                  if isinstance(classifications, str):
                      classifications = classifications.split(", ") if classifications else []
                  classifications.append("PaymasterAccount")
                  item["Classification"] = ", ".join(sorted(set(classifications)))

              # Voeg eventueel een timestamp toe
              from datetime import datetime
              from zoneinfo import ZoneInfo
              item["paymasterEnabledAt"] = datetime.now(ZoneInfo("Europe/Amsterdam")).strftime("%Y-%m-%d %H:%M:%S")
              break

      # 3️⃣ Schrijf terug naar bestand
      writeQueue(queue)

    return jsonify({
        "success": True,
        "reservationId": number,
        "updatedClassification": item.get("Classification", ""),        
        "message": f"Paymaster created for {number} ({full_name})"
    }), 200

import os

@app.route("/cache/version")
def cache_version():
    if queueFilePath.exists():
        mtime = os.path.getmtime(queueFilePath)
        return jsonify({"mtime": mtime})
    else:
        return jsonify({"mtime": 0})


if __name__ == "__main__":
    # Init: zorg voor leeg TXT-bestand als het er niet is
    if not queueFilePath.exists():
        writeQueue([])

    print("=== Start info ===")
    print(f"Queue file: {queueFilePath.resolve()}")
    print("Endpoints: /  (UI),  /sync  (sync + diff),  /api/waitlist (raw),  /api/check-in, /api/paymaster\n")

    app.run(host="0.0.0.0", port=5000, debug=True)