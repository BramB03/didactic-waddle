from flask import Flask, request, jsonify, render_template_string, Response, send_file

app = Flask(__name__)

clientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
accessToken = "BEC33DAD4C57410C9E6DB09600C7FB9B-310471532A30162E5B6F0EB4F4AD2BF"
client = "Mews Import Application"
url = "https://api.mews-demo.com/api/connector/v1/"


def getAllData():
  import requests
  import json
  from datetime import datetime, timedelta
  from zoneinfo import ZoneInfo
  from datetime import datetime, timedelta, timezone
  import json
  import xml.etree.ElementTree as ET
  import requests
  from zoneinfo import ZoneInfo

  headers = {
      "Content-Type": "application/json"
  }

  from datetime import datetime, timedelta
  from zoneinfo import ZoneInfo

  def getUtcMidnights(timezoneName):
    tz = ZoneInfo(timezoneName)
    now = datetime.now(tz)

    # Last midnight in local time
    lastMidnightLocal = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # Next midnight in local time
    nextMidnightLocal = lastMidnightLocal + timedelta(days=1)

    # Convert to UTC
    lastMidnightUtc = lastMidnightLocal.astimezone(ZoneInfo("UTC"))
    nextMidnightUtc = nextMidnightLocal.astimezone(ZoneInfo("UTC"))

    # Format as ISO 8601 (milliseconds precision, ending with Z)
    formatIso = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    return formatIso(lastMidnightUtc), formatIso(nextMidnightUtc)

  # Example usage
  timezoneName = "Europe/Amsterdam"
  lastMidnightUtc, nextMidnightUtc = getUtcMidnights(timezoneName)

  payloadReservations = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "Client": client,
    "ScheduledStartUtc": {
      "StartUtc": lastMidnightUtc,
      "EndUtc": nextMidnightUtc
    },
    "States": [
      "Confirmed"
    ],
    "Limitation": {
      "Count": 1000,
    }
  }

  jsonPayloadReservations = json.dumps(payloadReservations)
  responseReservations = requests.post(url + "reservations/getAll/2023-06-06", data=jsonPayloadReservations, headers=headers)
  if responseReservations.status_code != 200:
    print("Error reservations:", responseReservations.text)
  json_response_reservations = responseReservations.json()

  def extractReservationInformation(apiResponse):
    DataOut = []
    for reservation in apiResponse.get("Reservations", []):
      DataOut.append({
        "number": reservation.get("Number"),
        "reservationId": reservation.get("Id"),
        "reservationUrl": f"https://app.mews-demo.com/Commander/8dc59049-c9d0-4d08-a489-ae94011b28e5/Reservation/Detail/{reservation.get('Id')}",
        "assignedResourceId": reservation.get("AssignedResourceId"),
        "accountId": reservation.get("AccountId"),
        "requestedResourceCategoryId": reservation.get("RequestedResourceCategoryId"),
      })
    return DataOut

  json_response_reservations_extracted = extractReservationInformation(json_response_reservations)
  #pprint.pprint(json_response_reservations_extracted)

  accountIds = list(set([reservation['accountId'] for reservation in json_response_reservations_extracted if reservation['accountId'] is not None]))

  payloadCustomers = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "Client": client,
    "Extent": {
      "Customers": True,
      "Documents": False,
      "Addresses": False
    },
    "CustomerIds": accountIds,
    "Limitation": {
      "Count": 1000,
    }
  }

  jsonPayloadCustomers = json.dumps(payloadCustomers)
  responseCustomers = requests.post(url + "customers/getAll", data=jsonPayloadCustomers, headers=headers)
  if responseCustomers.status_code != 200:
    print("Error Customers:", responseCustomers.text)
  json_response_customers = responseCustomers.json()

  def extractCustomerBasics(apiResponse):
    dataOut = []
    for customer in apiResponse.get("Customers", []):
      if "WaitingForRoom" not in (customer.get("Classifications") or []):
        continue
          
      fullName = f"{customer.get('FirstName', '')} {customer.get('LastName', '')}".strip()

      # Determine contact method
      phone = customer.get("Phone")
      email = customer.get("Email")
      classifications = customer.get("Classifications") or []
      # Filter out "WaitingForRoom"
      filteredClassifications = [value for value in classifications if value != "WaitingForRoom"]

      classification = ", ".join(filteredClassifications) if filteredClassifications else None      
      contactMethod = phone or email or "Not Available"

      dataOut.append({
        "fullName": fullName,
        "customerId": customer.get("Id"),
        "contactMethod": contactMethod,
        "notes": customer.get("Notes"),
        "classification": classification
      })
    return dataOut

  json_response_customers_extracted = extractCustomerBasics(json_response_customers)

  #filter out the accountids from the reservations that are not in the customers list
  json_response_reservations_extracted = [reservation for reservation in json_response_reservations_extracted if any(customer.get("customerId") == reservation.get("accountId") for customer in json_response_customers_extracted)]

  resourceIds = list(set([reservation['assignedResourceId'] for reservation in json_response_reservations_extracted if reservation['assignedResourceId'] is not None]))
  resourceCategoryIds = list(set([reservation['requestedResourceCategoryId'] for reservation in json_response_reservations_extracted if reservation['requestedResourceCategoryId'] is not None]))
  
  payloadResources = {
      "ClientToken": clientToken,
      "AccessToken": accessToken,
      "Client": client,
      "ResourceIds": resourceIds,
      "Extent": {
          "Resources": True,
          "ResourceCategories": True
      },
      "Limitation": {
          "Count": 100
      }
  }

  jsonPayloadResources = json.dumps(payloadResources)
  responseResources = requests.post(url + "resources/getAll", data=jsonPayloadResources, headers=headers)
  if responseResources.status_code != 200:
      print("Error Resources:", responseResources.text)
  json_response_resources = responseResources.json()
  def extractResourceBasics(apiResponse):
      dataOut = []
      for resource in apiResponse.get("Resources", []):
          dataOut.append({
              "name": resource.get("Name"),
              "resourceId": resource.get("Id"),
              "State": resource.get("State")
          })
      return dataOut

  json_response_resources_extracted = extractResourceBasics(json_response_resources)
  json_response_resource_categories_extracted = json_response_resources.get("ResourceCategories", [])

  payloadResourceStates = {
      "ClientToken": clientToken,
      "AccessToken": accessToken,
      "Client": client,
      "ResourceCategoryIds": resourceCategoryIds,
      "Limitation": {
          "Count": 100
      }
  }
  jsonPayloadResourceStates = json.dumps(payloadResourceStates)
  responseResourceStates = requests.post(url + "resources/getOccupancyState", data=jsonPayloadResourceStates, headers=headers)
  if responseResourceStates.status_code != 200:
      print("Error State:", responseResourceStates.text)
  json_response_resource_occupancy_states = responseResourceStates.json()

  def mergeData(reservationList, customerList, resourceList):
      # Build lookup dictionaries for fast access
      customerLookup = {customer["customerId"]: customer for customer in customerList}
      resourceLookup = {resource["resourceId"]: resource for resource in resourceList}
      occupancyLookup = {}
      for category in json_response_resource_occupancy_states.get("ResourceCategoryOccupancyStates", []):
          for stateItem in category.get("ResourceOccupancyStates", []):
              resourceId = stateItem.get("ResourceId")
              if resourceId:
                  occupancyLookup[resourceId] = {
                    "resourceState": stateItem.get("ResourceState"),
                    "occupancyState": stateItem.get("OccupancyState")
                  }

      merged = []

      for reservation in reservationList:
          accountId = reservation.get("accountId")
          assignedResourceId = reservation.get("assignedResourceId")

          customer = customerLookup.get(accountId, {})
          resource = resourceLookup.get(assignedResourceId, {})

          # Combine base housekeeping State from `resource` with live OccupancyState
          stateInfo = occupancyLookup.get(assignedResourceId, {})
          baseState = resource.get("State")  # e.g. "Dirty"
          occupancyState = stateInfo.get("occupancyState")  # e.g. "Vacant"
          if occupancyState == "Unknown":
              occupancyState = None  # Don't show "Unknown"
          elif occupancyState == "ReservedLocked":
              occupancyState = "Occupied"  # More friendly wording
          elif occupancyState == "Reserved":
              occupancyState = "Reserved/Vacant"
          elif occupancyState == "Vacant":
              occupancyState = "Vacant"
          elif occupancyState == "InternalUse":
              occupancyState = "House use"
          elif occupancyState == "OutOfOrder":
              occupancyState = "Out of order"
          combinedState = ", ".join(s for s in [baseState, occupancyState] if s)

          merged.append({
              "number": reservation.get("number"),
              "reservationId": reservation.get("reservationId"),
              "reservationUrl": reservation.get("reservationUrl"),
              "fullName": customer.get("fullName"),
              "accountId": customer.get("customerId"),
              "Classification": customer.get("classification"),
              "contactMethod": customer.get("contactMethod"),
              "notes": customer.get("notes"),
              "assignedResourceId": assignedResourceId,
              "assignedResourceName": resource.get("name"),
              "assignedResourceState": combinedState,  # e.g. "Dirty, Vacant"
              "requestedResourceCategoryId": reservation.get("requestedResourceCategoryId")
            })
          
      for row in merged:
         for i in range(len(json_response_resource_categories_extracted)):
            if row["requestedResourceCategoryId"] == json_response_resource_categories_extracted[i]["Id"]:
               row["requestedResourceCategoryId"] = json_response_resource_categories_extracted[i]["Names"]["en-GB"]
               break
      return merged

  result = mergeData(json_response_reservations_extracted, json_response_customers_extracted, json_response_resources_extracted)
  return result


result = getAllData()

@app.route('/')
def index():
    result = getAllData()
    return render_template_string(HTML, result=result)


HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Reservation Queue Overview</title>

  <!-- Optional: Inter font (nice, neutral SaaS look) -->
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

  <style>
    :root{
      /* Light, clean SaaS palette with Mews-like blue accent */
      --bg: #f7f8fa;
      --surface: #ffffff;
      --text: #1a1d29;
      --text-muted: #6b7280;
      --border: #e7eaf0;
      --brand: #1c7ed6;      /* primary blue */
      --brand-600: #1864ab;
      --brand-50: #e7f1fb;
      --chip-bg: #f1f3f5;
      --chip-text: #343a40;
      --link: #0b6bcb;
      --row-hover: #f8fafc;
      --shadow-sm: 0 1px 2px rgba(16,24,40,.06);
      --shadow-md: 0 8px 24px rgba(16,24,40,.08);
      --radius: 10px;

      /* State colors */
      --ok: #12b886;         /* clean/inspected/ok */
      --warn: #f59f00;       /* dirty/in-progress */
      --info: #228be6;       /* reserved/occupied generic */
      --empty: #adb5bd;      /* vacant/unknown */
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

    /* Header */
    .header{
      display:flex; align-items:center; justify-content: space-between;
      margin-bottom: 16px;
    }
    .title{
      display:flex; align-items:baseline; gap:12px;
    }
    .title h1{
      margin:0; font-size: clamp(18px, 2.2vw, 24px); font-weight: 600; letter-spacing:.2px;
    }
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
    .btn:active{ transform: translateY(1px); }
    .btn.primary{
      background: var(--brand); border-color: var(--brand);
      color:#fff; box-shadow: 0 1px 2px rgba(28,126,214,.2);
    }
    .btn.primary:hover{ background: var(--brand-600); border-color: var(--brand-600); }
    .btn.ghost{ background:#fff; }
    .btn[disabled]{ opacity:.7; cursor: default; }

    /* Card/Table */
    .card{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow-md);
      overflow: hidden;
    }
    .table-wrap{ overflow:auto; }
    table{
      width:100%; border-collapse: collapse; font-size: 13.5px;
      min-width: 960px;
    }
    thead th{
      position: sticky; top:0; z-index:1;
      text-align:left; font-weight:600;
      background: #fff;
      border-bottom: 1px solid var(--border);
      padding: 12px 14px; color: #111827;
    }
    tbody td{
      padding: 12px 14px; border-bottom: 1px solid var(--border); color: #283041;
      vertical-align: middle;
    }
    tbody tr:hover{ background: var(--row-hover); }
    .mono{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

    .footer{
      display:flex; align-items:center; justify-content: space-between;
      padding: 10px 14px; color: var(--text-muted); font-size: 12px; background:#fff;
    }

    .btn[disabled] {
      background: #f1f3f5;
      color: #9ca3af;
      border-color: #e5e7eb;
      cursor: not-allowed;
      opacity: 0.7;
    }

    /* Chips & links */
    .chip{
      display:inline-flex; align-items:center; gap:6px;
      padding: 4px 8px; border-radius: 999px; font-weight: 600; font-size: 12px;
      background: var(--chip-bg); color: var(--chip-text); border: 1px solid var(--border);
      line-height: 1;
    }
    .chip .dot{ width:8px; height:8px; border-radius: 999px; background: var(--empty); }
    .chip.ok .dot{ background: var(--ok); }
    .chip.warn .dot{ background: var(--warn); }
    .chip.info .dot{ background: var(--info); }

    a.link{
      color: var(--link); text-decoration: none; font-weight: 600;
    }
    a.link:hover{ text-decoration: underline; }

    /* Compact first column button look */
    .open-link{
      display:inline-flex; align-items:center; gap:6px;
      padding: 6px 10px; border-radius: 8px; border: 1px solid var(--border);
      background:#fff; color: var(--link); font-weight:600; text-decoration:none;
    }
    .open-link:hover{ background:#f9fafb; }

    /* Small helper to space state chips */
    .chips{ display:flex; flex-wrap: wrap; gap:6px; }
    .btn.small { padding: 6px 10px; font-size: 12px; border-radius: 6px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="title">
        Reservation Overview
        <span class="pill">Live view</span>
      </div>
      <div class="toolbar">
        <button class="btn ghost" id="lastSyncBtn" disabled>Last sync: —</button>
        <button class="btn primary" id="refreshBtn" title="Reload the page">⟲ Refresh</button>
      </div>
    </div>

    <div class="card">
      <div class="table-wrap">
        <table aria-label="Reservation overview table">
          <thead>
            <tr>
              <th>Mews URL</th>
              <th>Res No.</th>
              <th>Guest</th>
              <th>Contact</th>
              <th>Room Number</th>
              <th>Room State</th>
              <th>Classification</th>
              <th>Requested Category</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {% for r in result %}
              <tr>
                <td><a href="{{ r.reservationUrl }}" target="_blank" rel="noopener" style="color: var(--accent); text-decoration: none;">🔗 Link</a></td>
                <td class="mono">{{ r.number | default('—') }}</td>
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
                      data-number="{{ r.number }}"
                      data-full-name="{{ r.fullName }}"
                      data-assigned-resource-id="{{ r.assignedResourceId }}"
                      data-requested-category="{{ r.requestedResourceCategoryId }}"
                      data-account-id="{{ r.accountId }}"
                      data-classification="{{ r.Classification or '' }}"
                      {% if not canCheckIn %}disabled style="opacity:0.5; cursor:not-allowed;"{% endif %}
                    >Check in</button>

                    <button
                      class="btn small action-paymaster"
                      data-reservation-id="{{ r.reservationId }}"
                      data-number="{{ r.number }}"
                      data-full-name="{{ r.fullName }}"
                      data-account-id="{{ r.accountId }}"
                      data-classification="{{ r.Classification or '' }}"
                      {% if hasPaymaster %}disabled style="opacity:0.5; cursor:not-allowed;"{% endif %}
                    >Enable roomcharging</button>
                  </div>
                </td>
              </tr>
            {% else %}
              <tr>
                <td colspan="10" class="muted">No data available.</td>
              </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      <div class="footer">
        <span class="muted">Tip: Click Refresh to reload data. The timestamp shows the last load time.</span>
        <span class="badge"><span class="dot"></span> Status: OK</span>
      </div>
    </div>
  </div>

  <script>
    // Refresh button: simple full reload (your server will rebuild `result`)
    document.getElementById('refreshBtn').addEventListener('click', () => {
      window.location.reload();
    });

    // Last sync indicator: use the client's current UTC time in ISO 8601 with ms
    function formatDateTimeHuman(date) {
        const pad = (n) => String(n).padStart(2, '0');
        const year = date.getFullYear();
        const month = pad(date.getMonth() + 1);
        const day = pad(date.getDate());
        const hours = pad(date.getHours());
        const minutes = pad(date.getMinutes());
        const seconds = pad(date.getSeconds());
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
      }

      document.getElementById('lastSyncBtn').textContent =
        `Last sync: ${formatDateTimeHuman(new Date())}`; 
    
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
          // laat 'disabled' staan tot reload, dat voorkomt dubbele acties
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
        classification: classificationArr, // <-- array
      };
    }

    function softRefresh(delayMs = 800) {
      setTimeout(() => window.location.reload(), delayMs);
    }

    document.addEventListener('click', async (ev) => {
      const btn = ev.target.closest('button');
      if (!btn) return;

      if (btn.classList.contains('action-checkin')) {
        const payload = gatherPayloadFromButton(btn);
        try {
          await postJSON('/api/check-in', payload, btn);
          // Korte bevestiging in de knop
          const prev = btn.textContent;
          btn.textContent = '✓ Checked in';
          softRefresh();
        } catch (e) {
          alert(`Check-in failed: ${e.message}`);
        }
      }

      if (btn.classList.contains('action-paymaster')) {
        const payload = gatherPayloadFromButton(btn);
        try {
          await postJSON('/api/paymaster', payload, btn);
          const prev = btn.textContent;
          btn.textContent = '✓ Enabled';
          softRefresh();
        } catch (e) {
          alert(`Paymaster failed: ${e.message}`);
        }
      }
    });
            
  </script>
</body>
</html>
'''

@app.post("/api/check-in")
def api_check_in():
    import json
    import requests
    payload = request.get_json(silent=True) or {}
    reservation_id = payload.get("reservationId")
    number = payload.get("number")
    full_name = payload.get("fullName")

    payloadCheckIn = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "ReservationId": reservation_id,
    }
    jsonPayloadCheckIn = json.dumps(payloadCheckIn)
    responseCheckIn = requests.post(url + "reservations/start", data=jsonPayloadCheckIn, headers={"Content-Type": "application/json"})
    if responseCheckIn.status_code != 200:
        return jsonify({
            "status": "error",
            "message": f"Check-in failed: {responseCheckIn.text}"
        }), 500
    
    return jsonify({
        "status": "ok",
        "reservationId": reservation_id,
        "message": f"Checked in {number} ({full_name})"
    }), 200


@app.post("/api/paymaster")
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

    return jsonify({
        "status": "ok",
        "reservationId": number,
        "message": f"Paymaster created for {number} ({full_name})"
    }), 200

if __name__ == '__main__':
    app.run(debug=True)

