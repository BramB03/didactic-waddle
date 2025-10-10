from flask import Flask, request, jsonify, render_template_string, Response, send_file

app = Flask(__name__)

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

  clientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
  accessToken = "BEC33DAD4C57410C9E6DB09600C7FB9B-310471532A30162E5B6F0EB4F4AD2BF"
  client = "Mews Import Application"
  url = "https://api.mews-demo.com/api/connector/v1/"

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
    print("Error:", responseReservations.text)
  json_response_reservations = responseReservations.json()

  def extractReservationInformation(apiResponse):
    DataOut = []
    for reservation in apiResponse.get("Reservations", []):
      DataOut.append({
        "number": reservation.get("Number"),
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
    print("Error:", responseCustomers.text)
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
      classification = customer.get("Classifications") or "No classification"
      contactMethod = phone or email or "Not Available"

      dataOut.append({
        "fullName": fullName,
        "id": customer.get("Id"),
        "contactMethod": contactMethod,
        "notes": customer.get("Notes"),
        "classification": classification
      })
    return dataOut

  json_response_customers_extracted = extractCustomerBasics(json_response_customers)

  #filter out the accountids from the reservations that are not in the customers list
  json_response_reservations_extracted = [reservation for reservation in json_response_reservations_extracted if any(customer.get("id") == reservation.get("accountId") for customer in json_response_customers_extracted)]

  resourceIds = list(set([reservation['assignedResourceId'] for reservation in json_response_reservations_extracted if reservation['assignedResourceId'] is not None]))

  payloadResources = {
      "ClientToken": clientToken,
      "AccessToken": accessToken,
      "Client": client,
      "ResourceIds": resourceIds,
      "Extent": {
          "Resources": True
      },
      "Limitation": {
          "Count": 100
      }
  }

  jsonPayloadResources = json.dumps(payloadResources)
  responseResources = requests.post(url + "resources/getAll", data=jsonPayloadResources, headers=headers)
  if responseResources.status_code != 200:
      print("Error:", responseResources.text)
  json_response_resources = responseResources.json()
  def extractResourceBasics(apiResponse):
      dataOut = []
      for resource in apiResponse.get("Resources", []):
          dataOut.append({
              "name": resource.get("Name"),
              "id": resource.get("Id"),
              "State": resource.get("State"),
              "ResourceCategoryId": resource.get("ResourceCategoryId")
          })
      return dataOut

  json_response_resources_extracted = extractResourceBasics(json_response_resources)

  def mergeData(reservationList, customerList, resourceList):
      # Build lookup dictionaries for fast access
      customerLookup = {customer["id"]: customer for customer in customerList}
      resourceLookup = {resource["id"]: resource for resource in resourceList}

      merged = []
      for reservation in reservationList:
          accountId = reservation.get("accountId")
          assignedResourceId = reservation.get("assignedResourceId")

          customer = customerLookup.get(accountId, {})
          resource = resourceLookup.get(assignedResourceId, {})

          merged.append({
              "number": reservation.get("number"),
              "fullName": customer.get("fullName"),
              "Classification": customer.get("classification"),
              "contactMethod": customer.get("contactMethod"),
              "notes": customer.get("notes"),
              "assignedResourceId": assignedResourceId,
              "assignedResourceName": resource.get("name"),
              "assignedResourceState": resource.get("State"),
              "requestedResourceCategoryId": reservation.get("requestedResourceCategoryId")
          })
      return merged

  result = mergeData(json_response_reservations_extracted, json_response_customers_extracted, json_response_resources_extracted)
  return result


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
  <style>
    :root {
      --bg: #0b1020;
      --card: #121a33;
      --muted: #6b7a99;
      --text: #e8ecf8;
      --accent: #5b8cff;
      --border: rgba(255,255,255,0.08);
      --success: #36d399;
    }
    html, body { height: 100%; }
    body {
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
      background:
        radial-gradient(1200px 800px at 10% -10%, rgba(91,140,255,.15), transparent),
        radial-gradient(1200px 800px at 90% 10%, rgba(139,91,255,.12), transparent),
        var(--bg);
      color: var(--text);
    }
    .container { max-width: 1100px; margin: 40px auto; padding: 0 16px; }

    .header {
      display: flex; gap: 12px; align-items: center; justify-content: space-between;
      margin-bottom: 18px;
    }
    .title {
      font-weight: 700; letter-spacing: .2px; font-size: clamp(20px, 2.4vw, 28px);
      display:flex; align-items:center; gap:10px;
    }
    .title .pill { font-size: 12px; color: var(--muted); border: 1px solid var(--border); padding: 2px 8px; border-radius: 999px; }

    .toolbar { display:flex; gap: 10px; align-items:center; }
    .btn {
      appearance: none; border: 1px solid var(--border);
      background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
      color: var(--text); padding: 10px 14px; border-radius: 12px; font-weight: 600; letter-spacing: .2px; cursor: pointer;
      transition: transform .06s ease, box-shadow .2s ease, border-color .2s ease;
      box-shadow: 0 6px 16px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .btn:hover { transform: translateY(-1px); border-color: rgba(255,255,255,0.18); }
    .btn:active { transform: translateY(0); }
    .btn.primary { border-color: rgba(91,140,255,.45); background: linear-gradient(180deg, rgba(91,140,255,.25), rgba(91,140,255,.15)); }
    .btn.ghost { background: transparent; }
    .btn[disabled] { opacity: .7; cursor: default; }

    .card {
      background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.02));
      border: 1px solid var(--border); border-radius: 18px; padding: 14px; overflow: hidden;
      box-shadow: 0 12px 24px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,0.04);
    }

    .table-wrap { overflow:auto; border-radius: 12px; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; min-width: 900px; }
    thead th {
      position: sticky; top: 0; z-index: 2; text-align: left; font-weight: 700; color: var(--text);
      background: linear-gradient(180deg, rgba(18,26,51,.9), rgba(18,26,51,.75));
      border-bottom: 1px solid var(--border);
      padding: 12px 14px;
    }
    tbody td { padding: 12px 14px; border-bottom: 1px solid var(--border); color: #d7def0; }
    tbody tr:hover { background: rgba(91,140,255,0.06); }

    .badge {
      display: inline-flex; align-items:center; gap:6px; border:1px solid var(--border); color: #dfe7ff; padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;
      background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
    }
    .badge .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--success); box-shadow: 0 0 0 3px rgba(54,211,153,.18); }
    .muted { color: var(--muted); }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

    .footer { margin-top: 12px; display:flex; align-items:center; justify-content: space-between; color: var(--muted); font-size: 12px; }
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
              <th>No.</th>
              <th>Guest</th>
              <th>Contact</th>
              <th>Room Name</th>
              <th>Room Id</th>
              <th>Room State</th>
              <th>Classification</th>
              <th>Requested Category</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {% for r in result %}
              <tr>
                <td class="mono">{{ r.number | default('—') }}</td>
                <td>{{ r.fullName | default('—') }}</td>
                <td class="mono">{{ r.contactMethod | default('—') }}</td>
                <td>{{ r.assignedResourceName | default('—') }}</td>
                <td class="mono">{{ r.assignedResourceId | default('—') }}</td>
                <td>{{ r.assignedResourceState | default('—') }}</td>
                <td>{{ r.Classification | default('—') }}</td>
                <td class="mono">{{ r.requestedResourceCategoryId | default('—') }}</td>
                <td>{{ r.notes if r.notes is not none and r.notes != '' else '—' }}</td>
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
    function formatDateTimeISO(date) {
      const pad = (n, z=2) => (""+n).padStart(z, '0');
      const ms = (date.getUTCMilliseconds()+" ").trim().padStart(3, '0');
      return `${date.getUTCFullYear()}-${pad(date.getUTCMonth()+1)}-${pad(date.getUTCDate())}T${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}:${pad(date.getUTCSeconds())}.${ms}Z`;
    }
    document.getElementById('lastSyncBtn').textContent = `Last sync: ${formatDateTimeISO(new Date())}`;
  </script>
</body>
</html>
'''


if __name__ == '__main__':
    app.run(debug=True)

