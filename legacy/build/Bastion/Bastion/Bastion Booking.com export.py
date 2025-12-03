import requests, json, time, pytest, os, pprint
from datetime import datetime, timedelta, timezone
from pathlib import Path
from json import JSONDecodeError

def getReservationInformation(serviceId, count, travelAgencyId, startDate, endDate, clientToken, accessToken, client, url, headers):
    payload = {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": client,
        "ScheduledStartUtc": {
            "StartUtc": startDate,
            "EndUtc": endDate
        },
        "TravelAgencyIds": [
            travelAgencyId
        ],
        "States": [
            "Confirmed",
            "Processed",
            "Started",
            "Canceled"
        ],
        "Limitation":{
            "Count":count
        }
    }
    response = requests.post(url + "reservations/getAll/2023-06-06", headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print(json.dumps(payload))
        print("Reservations Get Response:", response.status_code, response.text)
        response = f'Failed with status code {response.status_code} dates {startDate} to {endDate}'
        return response
    else:
        reservationdData = []
        for item in response.json().get("Reservations", []):
            enterpriseId = item.get("ServiceId")
            enterpriseName = next((e['name'] for e in enterprises if e['serviceId'] == enterpriseId), "Unknown Property")
            payload = {
                "Property Name": enterpriseName,
                "Booking.com reservation Number": item.get("ChannelNumber"),
                "State": item.get("State"),
                "ScheduledStartUtc": item["ScheduledStartUtc"].split("T")[0],
                "ScheduledEndUtc": item.get("ScheduledEndUtc").split("T")[0],
                "AccountId": item.get("AccountId"),
                "ReservationId": item.get("Id"),
                "Mews reservation Number": item.get("Number")
            }
            reservationdData.append(payload)
        time.sleep(0.2)
        return reservationdData

# Database
# =====================================================
enterprises = [
  {"name": "Bastion Hotel Barendrecht", "id": "be79e4b5-86a1-4520-8fe8-b241009751c6", "serviceId": "0eea8bb2-9a32-42ea-9d21-b24100975bea"},
  {"name": "Bastion Hotel Maastricht", "id": "5379edad-69aa-4a63-b387-b24100900cd1", "serviceId": "cbff6618-7527-489c-a9e1-b24100902a5e"},
  {"name": "Bastion Hotel Den Haag Rijswijk", "id": "17be8f81-7658-4126-b446-b24100a0df33", "serviceId": "c4fb7589-42a4-433f-a773-b24100a0f00b"},
  {"name": "Bastion Hotel Arnhem", "id": "b63f6e4a-906a-4e8a-8f5c-b241007f14cc", "serviceId": "244f7e64-0049-47da-8d7c-b241007f2831"},
  {"name": "Bastion Hotel Breda", "id": "46cc7efa-ad79-42c8-8767-b241009f171f", "serviceId": "7025b5ed-c6b3-4832-98eb-b241009f226c"},
  {"name": "Bastion Hotel Leiden Oegstgeest", "id": "75ee11e7-29ea-49dd-a23a-b2410096ff64", "serviceId": "a6754d19-6eee-4a5a-8a92-b24100970efd"},
  {"name": "Bastion Hotel Brielle Europoort", "id": "0d14fa21-8161-47d1-9985-b24100c1a287", "serviceId": "a521547b-0a31-45b1-904d-b24100c1ad96"},
  {"name": "Bastion Hotel Haarlem Velsen", "id": "ad2c2779-3826-4a7c-9ec0-b241009774b3", "serviceId": "279b0e02-313c-479c-9a8e-b2410097833d"},
  {"name": "Bastion Hotel Utrecht", "id": "c799d6b2-e05d-4e1c-9959-b1fc0083118f", "serviceId": "e2f75770-b45c-49e1-be6e-b1fc00926cca"},
  {"name": "Bastion Hotel Nijmegen", "id": "b29e38cd-6ed7-4fba-a4a0-b24100b0dd1f", "serviceId": "5c0c5317-0a47-4bfb-80b9-b24100b0e768"},
  {"name": "Bastion Hotel Dordrecht Papendrecht", "id": "fd5126df-504d-4142-93fd-b241009e2621", "serviceId": "1cf2196b-3b6b-452c-8d01-b241009e34aa"},
  {"name": "Bastion Hotel Roosendaal", "id": "1c81efa2-0f29-49e9-b661-b241009eaabb", "serviceId": "f0032113-be6a-4cab-8814-b241009eb557"},
  {"name": "Bastion Hotel Rotterdam Zuid", "id": "37c6378b-6e68-47a4-a6b7-b2410099b91a", "serviceId": "afa6f19f-32e6-4796-9dc1-b2410099c5e2"},
  {"name": "Bastion Hotel Amsterdam Noord", "id": "6b314e2f-28f5-45ac-8f69-b2410088028d", "serviceId": "77dfd57c-c537-452a-b8bc-b24100880eff"},
  {"name": "Bastion Hotel Amsterdam Airport", "id": "1b1b915a-5f2e-4c2c-a957-b22d00d2ea9e", "serviceId": "6091d7d3-a30b-4f0f-bd06-b22d00d2f80c"},
  {"name": "Bastion Hotel Apeldoorn het Loo", "id": "dbc15586-6feb-44ae-8424-b241008be363", "serviceId": "f45dff3b-aeb5-41bf-8d7c-b241008bec58"},
  {"name": "Bastion Hotel Leeuwarden", "id": "8d477e4a-34a6-4d4a-a12f-b2410092c4e1", "serviceId": "d26ff3cc-8e7e-486c-a79a-b2410092cf18"},
  {"name": "Bastion Hotel Almere", "id": "a08f51b3-c4f4-44f1-ae06-b24100a105c7", "serviceId": "dd32c36c-84cb-4daa-b54a-b24100a1108a"},
  {"name": "Bastion Hotel Amersfoort", "id": "b1cf582c-8ee3-45bd-877a-b2410083ba33", "serviceId": "4fe735fc-02a7-400c-801c-b2410083c42e"},
  {"name": "Bastion Hotel Vlaardingen", "id": "b39f196c-ca0d-429d-9db4-b24100791ff2", "serviceId": "039aca0a-e0f3-4723-a48e-b24100792b2d"},
  {"name": "Bastion Hotel Schiphol Hoofddorp", "id": "7261885a-c502-479a-a628-b24100917b7c", "serviceId": "84da34b0-bab3-4178-ac90-b2410091a0ed"},
  {"name": "Bastion Hotel Amsterdam Amstel", "id": "fb99ddc6-4ce5-4805-80ba-b241009c2d27", "serviceId": "79935318-3d5a-4257-a840-b241009c44de"},
  {"name": "Bastion Hotel Amsterdam Zuidwest", "id": "c69b8bf8-25e2-4e06-91e2-b241008f4c59", "serviceId": "9ee9914e-d3ff-4eb8-9cf6-b241008f578c"},
  {"name": "Bastion Hotel Geleen", "id": "415dc47a-dd07-4bcf-b508-b24100ab99c4", "serviceId": "5d92d88e-5c79-4ec9-a91c-b24100aba608"},
  {"name": "Bastion Hotel Zaandam", "id": "2172211b-0f8d-485c-8dc4-b2410096ef12", "serviceId": "247756ea-70a8-4e2d-83d7-b2410097033a"},
  {"name": "Bastion Hotel Leiden Voorschoten", "id": "00ded0bd-a998-4888-a6ad-b24100932a8c", "serviceId": "065aba6e-2533-4985-9aef-b241009333a8"},
  {"name": "Bastion Hotel Groningen", "id": "6d53ebc5-5329-4858-a293-b241008b828c", "serviceId": "a4416914-785a-4203-897b-b241008b9081"},
  {"name": "Bastion Hotel Rotterdam Alexander", "id": "8e136c17-7061-4605-a1ef-b24100762bfc", "serviceId": "943166e7-0e04-4b6e-b31a-b241007637d8"},
  {"name": "Bastion Hotel Zoetermeer", "id": "f8a0652d-fa49-465e-9efa-b241009aac45", "serviceId": "8d9f84e5-4b5a-42d1-838e-b241009ab5a3"},
  {"name": "Bastion Hotel Heerlen", "id": "82d1e34d-23d2-4a51-beb4-b24100a2cad5", "serviceId": "318e6835-ee95-422b-83ed-b24100a2d4d0"},
  {"name": "Bastion Hotel Tilburg", "id": "7da9598d-47bb-4487-a10f-b2410099fe64", "serviceId": "8c63c25c-33bc-493f-913d-b241009a0f72"},
  {"name": "Bastion Hotel Bussum Hilversum", "id": "f9e5d993-0402-4730-9dda-b241009c9a84", "serviceId": "5b731b7f-4ef8-4953-a7c8-b241009ca4b0"},
  {"name": "Best Western Amsterdam Airport Hotel", "id": "f4f22503-ab03-4b71-a0b1-b2440103a713", "serviceId": "23abd1ab-9537-4be3-a72b-b2440103bc47"},
  {"name": "Bastion Hotel Eindhoven", "id": "3454c4f0-2f5f-4594-988d-b241007bdc73", "serviceId": "dc415f17-d51c-43c1-9bd4-b241007bf4fb"}
]

utcBefore = datetime.now(timezone.utc)
# Generic config
# =====================================================
clientToken = os.getenv("BAST_CLIENTTOKEN")
client = "Bastion data request"
url = "https://api.mews.com/api/connector/v1/"
headers = {
    "Content-Type": "application/json"
}
endpointCounter = 0
totalValuebefore = 0
totalValueafter = 0
totalIncrease = 0
reservationCounter = 0
PROCESSED_FILE = Path("reservations bcom.txt")
ERRORED_FILE = Path("full days.txt")

# Property specific config
# =====================================================
accessToken = os.getenv("BAST_MULTIACCESSTOKEN")
serviceId = ""

# Execution specific information
# =====================================================
reservationCount = 1000
dateRange = 330
dayRange = 1
start = "2026-01-01T00:00:00Z"
travelAgencyId = "d988b779-31e5-4716-b21b-b24100a3a684"

# Generic work
# =====================================================
if PROCESSED_FILE.exists():
    try:
        with open(PROCESSED_FILE, "r") as f:
            processed_ids = json.load(f)   # expect list of dicts
            if not isinstance(processed_ids, list):
                processed_ids = []
    except JSONDecodeError:
        # Old runs may have written line-by-line; start fresh
        processed_ids = []
else:
    processed_ids = []

processedIdSet = {
    (x.get("ReservationId") if isinstance(x, dict) else x)
    for x in processed_ids
    if (isinstance(x, dict) and x.get("ReservationId")) or isinstance(x, str)
}

if ERRORED_FILE.exists():
    with open(ERRORED_FILE, "r") as f:
        errored_ids = set(line.strip() for line in f if line.strip())
else:
    errored_ids = set()

timeList = [30,60,90,120,150,180,210,240,270,300,330,360]
startUtc = datetime.fromisoformat(start.replace("Z", "+00:00"))
for length in range(dateRange):
    if length in timeList:
        if length == 60:
            dayRange =+ 1
        if length == 120:
            dayRange += 1
        if length == 180:
            dayRange += 2
        time.sleep(30)

    print("Processing week starting at:", startUtc.isoformat())
    endUtc = startUtc + timedelta(days=dayRange)
    reservationsIds = getReservationInformation(
        serviceId, 
        reservationCount, 
        travelAgencyId,
        startUtc.isoformat().replace("+00:00", "Z"), 
        endUtc.isoformat().replace("+00:00", "Z"), 
        clientToken, 
        accessToken, 
        client, 
        url, 
        headers
    )
    if not reservationsIds:
        print("No reservations found for this period.")
        startUtc = endUtc
        continue
    elif isinstance(reservationsIds, str) and reservationsIds.startswith("Failed"):
        errored_ids.add(reservationsIds)
        continue
    else:
        if len(reservationsIds) == 1000:
            print(f"⚠️  Maximum reservations reached for {startUtc.date()}. There may be more reservations to fetch.")
            errored_ids.add(f"Maximum reservations reached for {startUtc.date()}")
        for r in reservationsIds:
            rid = r.get("ReservationId")
            if rid and rid not in processedIdSet:
                processed_ids.append(r)     # store the entire dict (your requirement)
                processedIdSet.add(rid)     # keep membership check fast & safe

    startUtc = endUtc

with open(PROCESSED_FILE, "a") as f:  # append mode
    for r in processed_ids:
        f.write(json.dumps(r) + "\n")
with open(ERRORED_FILE, "w") as f:
    for sid in errored_ids:
        f.write(sid + "\n")

utcAfter = datetime.now(timezone.utc)
timeDiff = utcAfter - utcBefore
print(f"⏱️ Tijd genomen voor uitvoering: {timeDiff}.")
count = len(processed_ids)  # gebruik count als variabelenaam
print(f"✅ Klaar. {count} ID's opgeslagen in {PROCESSED_FILE}.")
print("Total reservations processed:", reservationCounter)
